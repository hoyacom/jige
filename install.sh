#!/usr/bin/env bash
# jige 부트스트랩 설치기 — brew.sh의 한 줄 설치와 같은 역할.
#   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/<GITHUB_USER>/jige/main/install.sh)"
set -euo pipefail

REPO_URL="https://github.com/<GITHUB_USER>/jige.git"
INSTALL_DIR="$HOME/.jige"
BIN_TARGET="/usr/local/bin/jige"

if ! command -v git >/dev/null 2>&1; then
  echo "git이 필요합니다 (macOS는 Xcode Command Line Tools, Linux는 배포판 패키지로 설치)." >&2
  exit 1
fi

if [ -d "$INSTALL_DIR/.git" ]; then
  echo "jige 업데이트 중: $INSTALL_DIR"
  git -C "$INSTALL_DIR" pull --ff-only
else
  echo "jige 받는 중: $REPO_URL -> $INSTALL_DIR"
  git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
fi

chmod +x "$INSTALL_DIR/jige"

BIN_DIR="$(dirname "$BIN_TARGET")"
if [ -w "$BIN_DIR" ]; then
  ln -sf "$INSTALL_DIR/jige" "$BIN_TARGET"
else
  echo
  echo "$BIN_DIR 에 쓰기 권한이 없어서, 아래 명령을 직접 한 번 실행해주세요:"
  echo "  sudo ln -sf \"$INSTALL_DIR/jige\" \"$BIN_TARGET\""
  exit 1
fi

echo
echo "설치 완료: $(command -v jige)"
"$BIN_TARGET" --help
