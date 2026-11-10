#!/usr/bin/env bash
# jige 부트스트랩 설치기 — brew.sh의 한 줄 설치와 같은 역할.
#   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/hoyacom/jige/main/install.sh)"
set -euo pipefail

REPO_URL="https://github.com/hoyacom/jige.git"
INSTALL_DIR="$HOME/.jige"
BIN_TARGET="/usr/local/bin/jige"

if [ "$(uname -s)" = "Darwin" ] && ! xcode-select -p >/dev/null 2>&1; then
  # command -v git은 CLT 미설치 상태에서도 /usr/bin/git 스텁이 있어서 그냥 통과해버림 —
  # 실제로 쓰려고 하면 그제서야 GUI 팝업이 뜨고 이 스크립트는 조용히 실패하게 됨.
  # xcode-select -p로 미리 감지해서 먼저 알려줌.
  echo "이 Mac엔 아직 Xcode Command Line Tools(git·python3 포함)가 없습니다." >&2
  echo "터미널에 아래 명령을 먼저 실행해서 설치를 끝낸 뒤, 이 jige 설치 명령을 다시 실행해주세요:" >&2
  echo "  xcode-select --install" >&2
  exit 1
fi

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
