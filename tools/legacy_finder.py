#!/usr/bin/env python3
"""legacy_finder.py — recipes/legacy/<token>.json 후보를 AI 없이 자동으로 찾는 조사 전용 도구.

실제 검색 로직은 ../jige의 find_legacy_commit_live()에 있음(jige install --find-legacy가
쓰는 것과 완전히 같은 코드) — 이 스크립트는 설치는 안 하고 "어느 커밋을 쓰면 되는지"만
찾아서 recipes/legacy/<token>.json에 바로 쓸 수 있는 형태로 보여주는 조사용 래퍼.

사용법:
  python3 tools/legacy_finder.py virtualbox --target-macos 12
  python3 tools/legacy_finder.py virtualbox --target-macos 12 --write   # recipes/legacy/<token>.json에 병합
"""
from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import json
from pathlib import Path


def load_jige():
    jige_path = Path(__file__).resolve().parent.parent / "jige"
    loader = importlib.machinery.SourceFileLoader("jige", str(jige_path))
    spec = importlib.util.spec_from_loader("jige", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("token")
    ap.add_argument("--target-macos", required=True, type=int, help="예: 12 (Monterey)")
    ap.add_argument("--cpu", default=None, help="arm64 또는 x86_64 (생략하면 이 기기 기준)")
    ap.add_argument("--write", action="store_true", help="recipes/legacy/<token>.json에 병합해서 저장")
    args = ap.parse_args()

    jige = load_jige()
    cpu = args.cpu or jige.arch()

    print(f"'{args.token}' 토큰의 Homebrew-Cask 커밋 기록에서 macOS {args.target_macos} 지원 버전을 찾는 중...")
    found = jige.find_legacy_commit_live(args.token, args.target_macos, cpu)
    if not found:
        print("못 찾음 — 수동으로 확인하거나 더 넓게 찾아봐야 합니다.")
        raise SystemExit(1)

    recipe = jige.fetch_recipe_from_cask_rb(found["commit_url"], cpu)
    print()
    print(f"찾음: 버전 {recipe['version']} (근거: {found['found_by']})")
    print(f"  커밋: {found['commit_url']}")
    print(f"  url : {recipe['url']}")
    print(f"  sha256: {recipe['sha256']}")

    entry = {"commit_url": found["commit_url"], "found_by": found["found_by"], "confirmations": []}

    if args.write:
        out_path = jige.LOCAL_LEGACY_DIR / f"{args.token}.json"
        data = json.loads(out_path.read_text()) if out_path.exists() else {}
        data[str(args.target_macos)] = entry
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        print(f"\n저장함: {out_path}")
    else:
        print()
        print(f'recipes/legacy/{args.token}.json에 추가할 내용 (키: "{args.target_macos}"):')
        print(json.dumps(entry, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
