# jige bash 탭 자동완성. (macOS 기본 bash 3.2에서도 동작하게 mapfile 등은 안 씀)
#   ~/.bash_profile(macOS) 또는 ~/.bashrc 에:  source ~/.jige/completions/jige.bash
#   (install.sh가 알아서 넣어줌. 수동 설치라면 위 한 줄, 또는 source <(jige completion bash))
#
# 앱 이름 후보는 캐시 파일을 셸이 직접 읽음 — pyenv shim 등으로 python 기동만 0.5초 넘게
# 걸리는 기기가 있어서, 탭마다 python을 띄우지 않고 캐시가 낡았을 때만 jige를 부름.

_JIGE_INDEX_DIR="$HOME/Library/Caches/jige/index"
_JIGE_STATE_FILE="$HOME/Library/Application Support/jige/installed.json"

# 접두어로 시작하는 줄만 (대소문자 무시, 정규식 특수문자 안전)
_jige_filter() {
  awk -v p="$1" 'BEGIN { p = tolower(p) } index(tolower($0), p) == 1'
}

_jige() {
  # (IFS는 기본값 그대로 — brew/port 이름엔 공백이 없고, compgen -W 목록도 공백 구분이라)
  local cur cmd jige_bin tok
  cur=${COMP_WORDS[COMP_CWORD]}
  jige_bin=${COMP_WORDS[0]}
  COMPREPLY=()

  if [ "$COMP_CWORD" -eq 1 ]; then
    COMPREPLY=($(compgen -W "install search info uninstall remove list installed upgrade update config completion --help --version" -- "$cur"))
    return
  fi

  cmd=${COMP_WORDS[1]}
  case "$cur" in
    -*)
      case "$cmd" in
        install)          COMPREPLY=($(compgen -W "--mas --latest --find-legacy --help" -- "$cur")) ;;
        search)           COMPREPLY=($(compgen -W "--mas --help" -- "$cur")) ;;
        uninstall|remove) COMPREPLY=($(compgen -W "--zap --help" -- "$cur")) ;;
        upgrade)          COMPREPLY=($(compgen -W "--latest --help" -- "$cur")) ;;
        *)                COMPREPLY=($(compgen -W "--help" -- "$cur")) ;;
      esac
      return
      ;;
  esac

  case "$cmd" in
    install|info)
      [ "$COMP_CWORD" -eq 2 ] || return
      tok="$_JIGE_INDEX_DIR/tokens.txt"
      if [ ! -s "$tok" ] || [ "$_JIGE_INDEX_DIR/cask.json" -nt "$tok" ] || [ "$_JIGE_INDEX_DIR/formula.json" -nt "$tok" ]; then
        "$jige_bin" __complete tokens >/dev/null 2>&1   # tokens.txt 다시 뽑기
      fi
      [ -r "$tok" ] && COMPREPLY=($(_jige_filter "$cur" < "$tok"))
      ;;
    uninstall|remove|upgrade)
      [ "$COMP_CWORD" -eq 2 ] || return
      # installed.json 최상위 키 — jige가 indent=2로 저장함
      [ -r "$_JIGE_STATE_FILE" ] && COMPREPLY=($(sed -n 's/^  "\([^"]*\)": {.*/\1/p' "$_JIGE_STATE_FILE" | _jige_filter "$cur"))
      ;;
    config)
      if [ "$COMP_CWORD" -eq 2 ]; then
        COMPREPLY=($(compgen -W "mas" -- "$cur"))
      elif [ "$COMP_CWORD" -eq 3 ] && [ "${COMP_WORDS[2]}" = "mas" ]; then
        COMPREPLY=($(compgen -W "on off" -- "$cur"))
      fi
      ;;
    completion)
      [ "$COMP_CWORD" -eq 2 ] && COMPREPLY=($(compgen -W "zsh bash" -- "$cur"))
      ;;
  esac
}

complete -F _jige jige
