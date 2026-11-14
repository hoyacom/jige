#!/usr/bin/env bash
# jige 부트스트랩 설치기 — brew.sh의 한 줄 설치와 같은 역할.
#   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/hoyacom/jige/main/install.sh)"
#
# 셸 설정 파일(~/.zshrc 등)을 건드리지 말았으면 하면 앞에 JIGE_NO_MODIFY_RC=1 을 붙임
# (rustup의 --no-modify-path, nvm의 PROFILE=/dev/null 과 같은 역할 — 넣을 줄만 안내함):
#   JIGE_NO_MODIFY_RC=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/hoyacom/jige/main/install.sh)"
set -euo pipefail

REPO_URL="https://github.com/hoyacom/jige.git"
INSTALL_DIR="$HOME/.jige"
BIN_TARGET="/usr/local/bin/jige"

if [ "$(uname -s)" = "Darwin" ] && ! xcode-select -p >/dev/null 2>&1; then
  # command -v git은 CLT 미설치 상태에서도 /usr/bin/git 스텁이 있어서 그냥 통과해버림 —
  # 실제로 쓰려고 하면 그제서야 GUI 팝업이 뜨고 이 스크립트는 조용히 실패하게 됨.
  # xcode-select -p로 미리 감지해서 먼저 알려줌.
  echo "이 Mac엔 아직 Xcode Command Line Tools(git·python3 포함)가 없습니다."
  if [ -t 0 ]; then
    # Homebrew의 install.sh도 같은 상황에서 이렇게 함: GUI 팝업 띄우고 키 입력까지 대기.
    echo "GUI 설치창을 띄웁니다 — 설치가 끝나면 이 터미널로 돌아와서 아무 키나 눌러주세요."
    xcode-select --install 2>/dev/null || true
    read -n 1 -s -r -p "설치 완료 후 아무 키나 누르세요..."
    echo
    if ! xcode-select -p >/dev/null 2>&1; then
      echo "아직 설치가 안 끝난 것 같습니다 — 설치 끝내고 이 명령을 다시 실행해주세요." >&2
      exit 1
    fi
  else
    echo "터미널에 아래 명령을 먼저 실행해서 설치를 끝낸 뒤, 이 jige 설치 명령을 다시 실행해주세요:" >&2
    echo "  xcode-select --install" >&2
    exit 1
  fi
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

# ---------------------------------------------------------------------------
# 탭 자동완성 연결 — 셸 설정 파일에 source 한 줄만 추가(이미 있으면 건너뜀).
#  - 아래 /usr/local/bin 연결이 권한 문제로 멈춰도(새 Apple Silicon Mac에서 흔함)
#    자동완성은 이미 걸려 있도록 그보다 먼저 함.
#  - 매번 jige를 실행해서 스크립트를 뽑는 eval 방식이 아니라 셸 시작이 안 느려짐.
#  - 경로는 $HOME 그대로 적음 — dotfiles를 여러 Mac에 동기화해 쓰는 사람도 그대로 동작.
#  - jige를 지워도 [ -f ] 검사 덕에 이 줄은 조용히 무시됨(오류 안 남).
# Homebrew는 여기까지 안 해주고 문서(docs.brew.sh/Shell-Completion)로 안내만 하는데,
# jige는 설치 대상이 brew조차 없는 초보 사용자라 한 줄 설치에서 끝까지 해줌.
# ---------------------------------------------------------------------------
add_completion_line() {
  # $1: 설정 파일, $2: 넣을 줄
  local rc="$1" line="$2"
  if [ -f "$rc" ] && grep -qF "jige/completions/jige." "$rc"; then
    return 0
  fi
  case "${JIGE_NO_MODIFY_RC:-}" in
    ""|0|false|no) ;;
    *)
      echo "탭 자동완성: JIGE_NO_MODIFY_RC 설정됨 — $rc 는 건드리지 않음. 원하면 직접 넣으세요:"
      echo "  $line"
      return 0 ;;
  esac
  # dotfiles 관리 도구(nix 등)가 읽기 전용으로 링크해둔 경우도 있음 — 그땐 설치를
  # 멈추지 말고 직접 넣으라고 안내만
  if { printf '\n%s\n' "$line" >> "$rc"; } 2>/dev/null; then
    echo "탭 자동완성 추가: $rc"
  else
    echo "탭 자동완성: $rc 에 쓸 수 없어서, 아래 줄을 직접 넣어주세요:"
    echo "  $line"
  fi
}

ZSH_LINE='[ -f "$HOME/.jige/completions/jige.zsh" ] && source "$HOME/.jige/completions/jige.zsh"  # jige 탭 자동완성'
BASH_LINE='[ -n "$BASH_VERSION" ] && [ -f "$HOME/.jige/completions/jige.bash" ] && source "$HOME/.jige/completions/jige.bash"  # jige 탭 자동완성'

case "$(basename "${SHELL:-}")" in
  zsh)
    add_completion_line "${ZDOTDIR:-$HOME}/.zshrc" "$ZSH_LINE" ;;
  bash)
    if [ "$(uname -s)" = "Darwin" ]; then
      # macOS 터미널의 bash는 로그인 셸 — .bash_profile > .bash_login > .profile 중
      # 처음 있는 것 "하나만" 읽음. .profile만 쓰던 사람에게 .bash_profile을 새로
      # 만들어버리면 .profile이 안 읽히게 되니, 이미 있는 파일에 넣음(Homebrew 안내와 같음).
      if   [ -f "$HOME/.bash_profile" ]; then rc="$HOME/.bash_profile"
      elif [ -f "$HOME/.bash_login" ];   then rc="$HOME/.bash_login"
      elif [ -f "$HOME/.profile" ];      then rc="$HOME/.profile"   # sh도 읽는 파일이라 BASH_VERSION 검사 포함
      else rc="$HOME/.bash_profile"; fi
    else
      rc="$HOME/.bashrc"
    fi
    add_completion_line "$rc" "$BASH_LINE" ;;
  *)
    echo "탭 자동완성: zsh/bash만 지원 — 지금 셸(${SHELL:-알 수 없음})은 건너뜀" ;;
esac

BIN_DIR="$(dirname "$BIN_TARGET")"
if [ -w "$BIN_DIR" ]; then
  ln -sf "$INSTALL_DIR/jige" "$BIN_TARGET"
else
  echo
  echo "$BIN_DIR 에 쓰기 권한이 없어서, 아래 명령을 직접 한 번 실행해주세요:"
  echo "  sudo mkdir -p \"$BIN_DIR\" && sudo ln -sf \"$INSTALL_DIR/jige\" \"$BIN_TARGET\""
  exit 1
fi

echo
echo "설치 완료: $(command -v jige)"
echo "(탭 자동완성은 새 터미널 창부터 적용 — 지금 창에선 'exec \$SHELL' 로 바로 적용)"
"$BIN_TARGET" --help
