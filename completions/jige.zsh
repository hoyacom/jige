#compdef jige
# jige zsh 탭 자동완성.
#   ~/.zshrc 에:  source ~/.jige/completions/jige.zsh
#   (install.sh가 알아서 넣어줌. 수동 설치라면 위 한 줄, 또는 source <(jige completion zsh))
#
# 앱 이름 후보는 캐시 파일을 셸이 직접 읽음 — pyenv shim 등으로 python 기동만 0.5초 넘게
# 걸리는 기기가 있어서, 탭마다 python을 띄우지 않고 캐시가 낡았을 때만 jige를 부름.

_JIGE_INDEX_DIR="$HOME/Library/Caches/jige/index"
_JIGE_STATE_FILE="$HOME/Library/Application Support/jige/installed.json"

# Homebrew cask+formula 이름 + 로컬 레시피 이름 (jige search가 받아둔 인덱스 기준)
_jige_tokens() {
  local tok="$_JIGE_INDEX_DIR/tokens.txt"
  if [[ ! -s $tok || $_JIGE_INDEX_DIR/cask.json -nt $tok || $_JIGE_INDEX_DIR/formula.json -nt $tok ]]; then
    $1 __complete tokens >/dev/null 2>&1   # tokens.txt 다시 뽑기
  fi
  [[ -r $tok ]] && reply=(${(f)"$(<$tok)"}) || reply=()
}

# jige로 설치한 것 (installed.json 최상위 키 — jige가 indent=2로 저장함)
_jige_installed() {
  [[ -r $_JIGE_STATE_FILE ]] || { reply=(); return }
  reply=(${(f)"$(sed -n 's/^  "\([^"]*\)": {.*/\1/p' "$_JIGE_STATE_FILE")"})
}

_jige() {
  local jige_bin=${words[1]}
  local -a cmds reply
  local cmd

  if (( CURRENT == 2 )); then
    if [[ $PREFIX == -* ]]; then
      compadd -- --help --version
    else
      # 설명(언어별)은 셸 세션당 한 번만 jige에게 받아옴
      (( ${#_JIGE_CMDS} )) || typeset -ga _JIGE_CMDS=(${(f)"$($jige_bin __complete commands 2>/dev/null)"})
      cmds=($_JIGE_CMDS)
      _describe -t commands 'jige 명령' cmds
    fi
    return
  fi

  cmd=${words[2]}
  if [[ $PREFIX == -* ]]; then
    case $cmd in
      install)          compadd -- --mas --latest --find-legacy --help ;;
      search)           compadd -- --mas --help ;;
      uninstall|remove) compadd -- --zap --help ;;
      upgrade)          compadd -- --latest --help ;;
      *)                compadd -- --help ;;
    esac
    return
  fi

  case $cmd in
    install|info)
      (( CURRENT == 3 )) || return
      _jige_tokens $jige_bin
      compadd -- $reply
      ;;
    uninstall|remove|upgrade)
      (( CURRENT == 3 )) || return
      _jige_installed
      compadd -- $reply
      ;;
    config)
      case $CURRENT in
        3) compadd -- mas ;;
        4) [[ ${words[3]} == mas ]] && compadd -- on off ;;
      esac
      ;;
    completion)
      (( CURRENT == 3 )) && compadd -- zsh bash
      ;;
  esac
}

# macOS 기본 zsh는 compinit을 안 켜둠 — compdef가 없으면 여기서 켜줌
# (oh-my-zsh 등이 이미 켰으면 건너뜀)
if (( ! $+functions[compdef] )); then
  autoload -Uz compinit && compinit -i
fi
compdef _jige jige
