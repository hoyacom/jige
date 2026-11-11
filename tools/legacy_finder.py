#!/usr/bin/env python3
"""legacy_finder.py — recipes/legacy/<token>.json 후보를 AI 없이 자동으로 찾아주는 개발자 도구.

jige 본체(./jige)와는 별도의 메인테이너용 스크립트. "이 cask가 과거 어느 버전까지 이
macOS를 지원했는지"를 사람이 벤더 사이트를 뒤지는 대신, Homebrew-Cask 저장소 자체의
git 커밋 기록에서 과거 버전의 cask 정의(.rb)를 읽어와 알아낸다.

판단 순서:
  1) 그 커밋 시점의 cask가 depends_on macos: 를 버전 비교 형태로 선언해뒀으면 그걸로 판단.
  2) 안 써놨으면(VirtualBox가 실제로 이 경우) 그 버전의 실제 설치 파일을 받아서
     Info.plist의 LSMinimumSystemVersion을 직접 읽어 판단 — "AI의 판단"이 아니라
     파일 자체에 적힌 사실을 기계적으로 읽는 것.

체크섬은 Ruby 파일에 적힌 값을 그대로 베끼지 않고, 받은 파일로 매번 직접 재계산한다.

사용법:
  python3 tools/legacy_finder.py <token> --target-macos 12
  python3 tools/legacy_finder.py <token> --target-macos 12 --write   # recipes/legacy/<token>.json로 저장
"""
from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = "Homebrew/homebrew-cask"
API_BASE = f"https://api.github.com/repos/{REPO}"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}"

# jige의 MACOS_CODENAME과 같은 정보 — 여기서는 심볼(:monterey) -> 메이저 번호 방향으로 씀
CODENAME_TO_MAJOR = {
    "catalina": 10, "big_sur": 11, "monterey": 12, "ventura": 13,
    "sonoma": 14, "sequoia": 15, "tahoe": 26, "golden_gate": 27,
}


def gh_api(path: str) -> dict | list:
    req = urllib.request.Request(f"{API_BASE}{path}", headers={"User-Agent": "jige-legacy-finder"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def cask_path(token: str) -> str:
    letter = token[0].lower()
    return f"Casks/{letter}/{token}.rb"


def list_commits(path: str, max_commits: int = 60) -> list[dict]:
    """최신 -> 과거 순. GitHub API 하나당 최대 100개, 필요한 만큼만 페이지네이션."""
    commits = []
    page = 1
    while len(commits) < max_commits:
        batch = gh_api(f"/commits?path={path}&per_page=100&page={page}")
        if not batch:
            break
        commits.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return commits[:max_commits]


def fetch_raw(path: str, sha: str) -> str | None:
    url = f"{RAW_BASE}/{sha}/{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "jige-legacy-finder"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError:
        return None


def parse_cask(text: str) -> dict:
    """정규식으로 뽑을 수 있는 만큼만 뽑음 — 복잡한 on_arch_conditional/if 블록 등은
    건드리지 않고 못 찾으면 None으로 둠(틀린 값을 지어내지 않는 게 핵심)."""
    out: dict = {
        "version": None, "arch_map": None, "sha256": None,
        "url_template": None, "depends_on_macos": None,
    }

    m = re.search(r'^\s*version\s+"([^"]+)"', text, re.M)
    if m:
        out["version"] = m.group(1)

    m = re.search(r'^\s*arch\s+arm:\s*"([^"]+)"\s*,\s*intel:\s*"([^"]+)"', text, re.M)
    if m:
        out["arch_map"] = {"arm": m.group(1), "intel": m.group(2)}

    # sha256 단일 문자열
    m = re.search(r'^\s*sha256\s+"([0-9a-f]{64})"', text, re.M)
    if m:
        out["sha256"] = {"arm": m.group(1), "intel": m.group(1)}
    else:
        # sha256 arm: "...", intel: "..." 형태 (줄바꿈 포함 가능)
        m = re.search(
            r'^\s*sha256\s+arm:\s*"([0-9a-f]{64})"\s*,?\s*\n?\s*intel:\s*"([0-9a-f]{64})"',
            text, re.M,
        )
        if m:
            out["sha256"] = {"arm": m.group(1), "intel": m.group(2)}

    m = re.search(r'^\s*url\s+"([^"]+)"', text, re.M)
    if m:
        out["url_template"] = m.group(1)

    # depends_on macos: <값>  — "depends_on :macos"(플랫폼 마커, 버전 정보 없음)는 매치 안 되게
    m = re.search(r'^\s*depends_on\s+macos:\s*(.+)$', text, re.M)
    if m:
        out["depends_on_macos"] = m.group(1).strip()

    return out


def resolve_url(template: str, version: str, arch_literal: str) -> str | None:
    """#{version}, #{version.csv.first}, #{version.csv.second}, #{arch} 정도의
    흔한 패턴만 치환. 그 외 #{...}가 남아있으면 못 푼 걸로 보고 None."""
    csv_parts = version.split(",")
    repl = {
        "version.csv.first": csv_parts[0],
        "version.csv.second": csv_parts[1] if len(csv_parts) > 1 else "",
        "version": version,
        "arch": arch_literal,
    }
    out = template
    for key, val in repl.items():
        out = out.replace("#{" + key + "}", val)
    if "#{" in out:
        return None  # 모르는 변수가 남음 — 안전하게 포기
    return out


def depends_on_satisfies(expr: str, target_major: int) -> bool | None:
    """">= :monterey"/":monterey"/">= 13"/"13" 같은 표현을 target_major와 비교.
    해석 불가능하면 None(모름)을 돌려줌 — 모르면서 True/False로 단정하지 않음."""
    expr = expr.strip()
    m = re.search(r':(\w+)', expr)
    if m and m.group(1) in CODENAME_TO_MAJOR:
        required = CODENAME_TO_MAJOR[m.group(1)]
    else:
        m = re.search(r'(\d+)', expr)
        if not m:
            return None
        required = int(m.group(1))
    if expr.startswith("=="):
        return required == target_major
    return target_major >= required  # 기본/">=": 그 버전 이상이면 지원


def major_minor(version: str) -> str:
    core = version.split(",")[0]
    parts = core.split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 else core


def attach_dmg(dmg_path: Path, label: str) -> Path:
    mount_point = Path("/Volumes") / f"legacy-finder-{label}"
    subprocess.run(["hdiutil", "detach", str(mount_point)], capture_output=True)
    subprocess.run(
        ["hdiutil", "attach", "-nobrowse", "-quiet", "-mountpoint", str(mount_point), str(dmg_path)],
        check=True, capture_output=True,
    )
    return mount_point


def detach_dmg(mount_point: Path) -> None:
    subprocess.run(["hdiutil", "detach", str(mount_point)], capture_output=True)


def check_min_os_from_dmg(dmg_path: Path, label: str) -> str | None:
    """dmg 안의 .app Info.plist에서 LSMinimumSystemVersion을 직접 읽음 — 추측이 아니라
    실제 바이너리에 적힌 값. .app이 없으면(예: .pkg만 있는 cask) None."""
    mount_point = attach_dmg(dmg_path, label)
    try:
        apps = list(mount_point.glob("*.app"))
        if not apps:
            return None
        plist_path = apps[0] / "Contents" / "Info.plist"
        if not plist_path.exists():
            return None
        with open(plist_path, "rb") as f:
            return plistlib.load(f).get("LSMinimumSystemVersion")
    finally:
        detach_dmg(mount_point)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    print(f"    다운로드 중: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "jige-legacy-finder"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("token")
    ap.add_argument("--target-macos", required=True, type=int, help="예: 12 (Monterey)")
    ap.add_argument("--max-candidates", type=int, default=12, help="과거로 거슬러 올라가며 확인할 버전 수 상한")
    ap.add_argument("--write", action="store_true", help="recipes/legacy/<token>.json로 저장(기본은 출력만)")
    args = ap.parse_args()

    path = cask_path(args.token)
    print(f"cask 경로: {path}")
    print("GitHub 커밋 기록 조회 중...")
    commits = list_commits(path, max_commits=150)
    print(f"  {len(commits)}개 커밋 찾음 (최신 -> 과거)")

    # 버전 하나당 가장 최신 커밋 하나만 남김(패치 릴리스 여러 커밋 중복 확인 안 하려고),
    # 그리고 같은 major.minor 라인은 한 번만 확인(매크로스 요구치는 보통 마이너 단위로 안 바뀜).
    seen_mm: set[str] = set()
    candidates: list[tuple[str, dict]] = []  # (sha, parsed)
    for c in commits:
        sha = c["sha"]
        text = fetch_raw(path, sha)
        if not text:
            continue
        parsed = parse_cask(text)
        if not parsed["version"]:
            continue
        mm = major_minor(parsed["version"])
        if mm in seen_mm:
            continue
        seen_mm.add(mm)
        candidates.append((sha, parsed))
        if len(candidates) >= args.max_candidates:
            break

    print(f"  확인할 버전 라인: {[p['version'] for _, p in candidates]}")

    found = None
    for sha, parsed in candidates:
        version = parsed["version"]
        print(f"\n[{version}] (커밋 {sha[:10]})")

        dep = parsed["depends_on_macos"]
        if dep:
            verdict = depends_on_satisfies(dep, args.target_macos)
            print(f"  depends_on macos: {dep!r} -> {'만족' if verdict else '불만족' if verdict is False else '해석 불가'}")
            if verdict is True:
                found = (sha, parsed, f"depends_on macos: {dep}")
                break
            if verdict is False:
                continue
            # 해석 불가 -> 아래 실측으로 넘어감

        if not parsed["url_template"] or not parsed["arch_map"] or not parsed["sha256"]:
            print("  (이 커밋은 url/arch/sha256을 정규식으로 못 읽음 — 건너뜀, 수동 확인 필요)")
            continue

        arch_literal = parsed["arch_map"]["intel"]  # Intel Mac 기준으로 실측(이 iMac 기준)
        url = resolve_url(parsed["url_template"], version, arch_literal)
        if not url:
            print(f"  (url 템플릿을 못 풂: {parsed['url_template']!r} — 건너뜀)")
            continue

        print(f"  depends_on 정보 없음 -> 실제 파일 받아서 Info.plist 직접 확인")
        tmp = Path(tempfile.mkdtemp()) / f"{args.token}-{version.replace(',', '_')}.dmg"
        try:
            download(url, tmp)
        except Exception as e:
            print(f"  (다운로드 실패: {e} — 건너뜀)")
            continue
        actual_sha = sha256_of(tmp)
        expected_sha = parsed["sha256"]["intel"]
        match = "일치" if actual_sha == expected_sha else "불일치!!"
        print(f"  sha256(직접 계산) = {actual_sha} ({match} / Ruby 파일 값 {expected_sha})")

        min_os = check_min_os_from_dmg(tmp, f"{args.token}-{version}")
        if min_os is None:
            print("  (.app을 못 찾음 — .pkg 전용 cask일 수 있음, 실측 불가)")
            continue
        print(f"  Info.plist LSMinimumSystemVersion = {min_os}")
        satisfied = tuple(int(p) for p in min_os.split(".")) <= (args.target_macos, 0, 0)
        if satisfied:
            found = (sha, parsed, f"Info.plist LSMinimumSystemVersion={min_os} (실측)")
            break

    if not found:
        print("\n못 찾음 — max-candidates를 늘려서 더 과거까지 보거나 수동으로 확인하세요.")
        sys.exit(1)

    sha, parsed, reason = found
    version = parsed["version"]
    print(f"\n=== 결론: {args.token} {version} (macOS {args.target_macos} 지원 근거: {reason}) ===")

    # 최종 체크섬은 arm/intel 둘 다 실제로 받아서 재계산(단일 아키텍처만 실측했으면 나머지도 받음)
    final_hashes = {}
    for which in ("arm", "intel"):
        arch_literal = parsed["arch_map"][which]
        url = resolve_url(parsed["url_template"], version, arch_literal)
        if not url:
            continue
        tmp = Path(tempfile.mkdtemp()) / f"{args.token}-{which}.dmg"
        print(f"  [{which}] 최종 체크섬 확인차 재다운로드: {url}")
        download(url, tmp)
        final_hashes[which] = (url, sha256_of(tmp))

    entry = {
        "version": version,
        "min_macos": str(args.target_macos),
        "max_macos": str(args.target_macos),  # 보수적으로 타겟 버전만 — 범위는 사람이 넓혀도 됨
        "latest_min_macos": "확인 필요 — 최신판 cask의 depends_on.macos 보고 채울 것",
        "vendor_status": "os_limit",
        "note": f"legacy_finder.py로 자동 탐색 (근거: {reason}, Homebrew-Cask 커밋 {sha})",
        "source": [f"https://github.com/{REPO}/blob/{sha}/{cask_path(args.token)}"],
        "confirmations": [],
        "url": final_hashes.get("arm", (None, None))[0],
        "sha256": final_hashes.get("arm", (None, None))[1],
        "variations": {},
    }
    if "intel" in final_hashes:
        entry["variations"] = {"__INTEL_CODENAME__": {"url": final_hashes["intel"][0], "sha256": final_hashes["intel"][1]}}

    print(json.dumps(entry, ensure_ascii=False, indent=2))

    if args.write:
        out_path = Path(__file__).resolve().parent.parent / "recipes" / "legacy" / f"{args.token}.auto.json"
        out_path.write_text(json.dumps({"versions": [entry]}, ensure_ascii=False, indent=2))
        print(f"\n저장함: {out_path} (검토 후 .json으로 이름 바꾸고 variations의 코드네임을 채우세요)")


if __name__ == "__main__":
    main()
