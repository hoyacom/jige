"""터미널 표시용 — 폭 계산/패딩/기호(유니코드 또는 ASCII 대체)/신뢰도 배지.
네트워크·파일시스템에 의존하지 않는 순수 함수들만 모아둠.
"""
from __future__ import annotations

import os
import re
import sys
import unicodedata

KIND_ICON_UNICODE = {"jim": "💻", "dogu": "🔧", "unknown": "❓"}  # jim=GUI 앱, dogu=CLI 도구
KIND_ICON_ASCII = {"jim": "GUI", "dogu": "CLI", "unknown": "?"}


def _supports_color() -> bool:
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _supports_unicode() -> bool:
    """출력 인코딩이 UTF-8 계열이 아니면(옛 터미널, 특정 locale 등) 이모지/기호
    대신 ASCII로 대체 — 깨진 문자(□, ?)로 나오는 것보단 밋밋해도 읽히는 게 나음."""
    enc = (getattr(sys.stdout, "encoding", None) or "").lower()
    return "utf" in enc


def _sym(unicode_form: str, ascii_form: str) -> str:
    return unicode_form if _supports_unicode() else ascii_form


def kind_icon(kind: str) -> str:
    table = KIND_ICON_UNICODE if _supports_unicode() else KIND_ICON_ASCII
    return table.get(kind, table["unknown"])


def trust_badge(entry: dict) -> str:
    """search처럼 짧게만 보여줄 때 쓰는 한 토큰짜리 신뢰 단계 표시.
    UTF-8이 아닌 터미널에선 이모지/기호 대신 ASCII로."""
    n = len(entry.get("confirmations") or [])
    if n == 0:
        return _sym("🆕", "NEW")
    if n < 3:
        return _sym(f"✓{n}", f"OK{n}")
    return _sym(f"✓✓{n}", f"OK+{n}")


def trust_label(entry: dict) -> str:
    """recipes/legacy/<token>.json의 confirmations 배열 길이로 신뢰 단계를 보여줌.
    confirmations는 실제로 설치해본 사람들이 GitHub PR로 한 줄씩 추가하는 기록이라,
    jige가 뭘 자동 집계하는 게 아니라 그 배열 길이 자체가 신뢰 단계임."""
    n = len(entry.get("confirmations") or [])
    if n == 0:
        return _sym("🆕", "NEW") + " 방금 등록됨 (공식 문서로 확인, 다른 사용자 확인 아직 없음)"
    if n < 3:
        return _sym("✓", "OK") + f" 실제 설치로 확인됨 ({n}명)"
    return _sym("✓✓", "OK+") + f" 여러 명이 확인함 ({n}명)"


def _bold(s: str) -> str:
    """항상 _pad()/_truncate_to_width()로 먼저 폭을 맞춘 뒤에 감싸야 함 — ANSI
    코드 자체는 화면에 안 보이지만 글자 수로는 잡혀서, 먼저 감싸면 폭 계산이 틀어짐."""
    return f"\033[1m{s}\033[0m" if _supports_color() else s


def _display_width(s: str) -> int:
    """터미널에서 실제로 차지하는 칸 수. 한글/이모지처럼 두 칸 쓰는 문자가 있어서
    len()만으로 패딩하면(파이썬은 글자 수만 셈) 한글이 섞인 칸이 실제보다 좁게
    계산돼 테이블이 밀림 — search 결과에 한글 헤더(종류/분류/버전)·태그(🆕 등)가
    섞이면서 실제로 겪은 문제. "A"(폭 모호, "…"·"★"·"▼" 등)도 2칸으로 침 — 한글
    로케일 터미널에서는 이런 문자를 넓게 그리는 경우가 많아서("…" 때문에 줄바꿈이
    생겼던 적 있음), 좀 넉넉하게 잡는 쪽이 줄바꿈/정렬 깨짐보다 안전함."""
    width = 0
    for ch in s:
        width += 2 if unicodedata.east_asian_width(ch) in ("W", "F", "A") else 1
    return width


def _pad(s: str, width: int) -> str:
    return s + " " * max(0, width - _display_width(s))


def _truncate_to_width(s: str, max_width: int) -> str:
    if _display_width(s) <= max_width:
        return s
    ellipsis = _sym("…", "...")
    ellipsis_w = _display_width(ellipsis)
    out: list[str] = []
    w = 0
    for ch in s:
        cw = 2 if unicodedata.east_asian_width(ch) in ("W", "F", "A") else 1  # _display_width와 맞춤
        if w + cw > max_width - ellipsis_w:
            break
        out.append(ch)
        w += cw
    return "".join(out) + ellipsis


def simplify_version_for_display(version: str) -> str:
    """search 결과 화면에만 쓰는 버전 표시 — 빌드번호/리비전 suffix(",175245"나
    "-174740" 같은 것)는 보기엔 필요 없어서 뺌. 설치에 쓰는 실제 레시피의 version/
    url/sha256은 이 함수를 안 거치고 fetch_recipe()로 새로 받아오므로 전혀 영향 없음."""
    v = version.split(",")[0]
    v = re.split(r"-(?=\d)", v, maxsplit=1)[0]
    return v
