"""GitHub 자체 기능(파일 수정/새 파일/이슈 만들기 — 전부 자동 fork+PR 또는 prefill URL)만
빌려 써서, 커스텀 서버·DB 없이 recipes/legacy/ 기여를 쉽게 받기 위한 URL 생성기.
"""
from __future__ import annotations

import urllib.parse

JIGE_REPO_SLUG = "hoyacom/jige"
JIGE_REPO = f"https://github.com/{JIGE_REPO_SLUG}"
JIGE_LEGACY_RAW_BASE = f"https://raw.githubusercontent.com/{JIGE_REPO_SLUG}/main/recipes/legacy"


def github_edit_url(path: str) -> str:
    """GitHub 자체의 '파일 수정하면 자동 fork + PR 생성' 흐름을 그대로 가리킴 —
    커스텀 서버/DB 없이 recipes/legacy/ 기여를 쉽게 하기 위한 링크일 뿐.
    이미 있는 파일에 한 줄 보탤 때만 씀 — 새 파일은 github_new_file_url()."""
    return f"{JIGE_REPO}/edit/main/{path}"


def github_new_file_url(path: str, content: str = "") -> str:
    """GitHub의 '새 파일 만들기 + 내용 미리 채우기(+자동 fork/PR)' URL. recipes/legacy/<token>.json이
    아직 없는 새 토큰에 처음 추가할 때 씀."""
    return f"{JIGE_REPO}/new/main?" + urllib.parse.urlencode({"filename": path, "value": content})


def github_new_issue_url(title: str, body: str) -> str:
    return f"{JIGE_REPO}/issues/new?" + urllib.parse.urlencode({"title": title, "body": body})


LEGACY_ENTRY_TEMPLATE = """{
  "<macOS 메이저 번호, 예: 12>": {
    "commit_url": "<https://raw.githubusercontent.com/Homebrew/homebrew-cask/커밋SHA/Casks/x/token.rb — 이 macOS에서 쓸 수 있는 구버전이 담긴 특정 커밋>",
    "found_by": "<depends_on 또는 info_plist — 그 커밋에 macOS 요구치가 명시돼 있었는지, 실제 파일을 받아 Info.plist로 확인했는지>",
    "confirmations": []
  }
}"""
