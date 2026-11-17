"""i18n — 완벽한 번역은 아니고, 표제부(헤더/명령어 설명)만 한/영/일 지원.
나머지 내부 메시지는 한국어 그대로 둠.
"""
from __future__ import annotations

import os
import platform
import subprocess

STRINGS = {
    "col_name": {"ko": "이름", "en": "Name", "ja": "名前"},
    "col_kind": {"ko": "종류", "en": "Kind", "ja": "種類"},
    "col_source": {"ko": "분류", "en": "Source", "ja": "分類"},
    "col_version": {"ko": "버전", "en": "Version", "ja": "バージョン"},
    "col_desc": {"ko": "설명", "en": "Description", "ja": "説明"},
    "no_results": {
        "ko": "'{q}' 검색 결과 없음 (Homebrew / MacPorts / 자체 레포지토리 전부).",
        "en": "No results for '{q}' (checked Homebrew, MacPorts, and the local repo).",
        "ja": "'{q}' の検索結果なし(Homebrew / MacPorts / ローカルリポジトリすべて)。",
    },
    "install_hint": {
        # 터미널이 좁아도 예측 못 한 중간 지점에서 꺾이지 않도록 줄바꿈을 직접 넣고,
        # 내용도 짧게 줄임(80컬럼 터미널에서도 여유 있게 들어가도록)
        "ko": "설치: jige install <이름>\n      (Homebrew Cask는 지금 설치 가능, 나머지는 추후 지원)",
        "en": "Install: jige install <name>\n         (Homebrew Cask installs now, the rest comes later)",
        "ja": "インストール: jige install <名前>\n           (Homebrew Caskは今すぐ対応、残りは今後対応)",
    },
    "app_description": {
        "ko": "brew 없이도 Homebrew·MacPorts·Mac App Store 공개 레시피를 읽어서 이 기기에 맞는 앱을 찾아 설치",
        "en": "Find and install apps for this machine by reading Homebrew/MacPorts/Mac App Store's own public recipes — no brew required",
        "ja": "brewなしでHomebrew・MacPorts・Mac App Storeの公開レシピを読み、このマシンに合うアプリを探してインストール",
    },
    "help_install": {
        "ko": "앱 설치/업데이트 (brew install / port install)",
        "en": "Install or update an app (like brew install / port install)",
        "ja": "アプリのインストール/更新 (brew install / port install 相当)",
    },
    "help_search": {
        "ko": "통합 검색 (brew search / port search)",
        "en": "Search across all sources (like brew search / port search)",
        "ja": "統合検索 (brew search / port search 相当)",
    },
    "help_info": {
        "ko": "상세 정보, 설치 안 함 (brew info / port info)",
        "en": "Show details without installing (like brew info / port info)",
        "ja": "詳細情報を表示(インストールはしない、brew info / port info 相当)",
    },
    "help_uninstall": {
        "ko": "제거, 휴지통행 (brew uninstall/remove)",
        "en": "Uninstall, moved to Trash (like brew uninstall/remove)",
        "ja": "アンインストール(ゴミ箱へ移動、brew uninstall/remove 相当)",
    },
    "help_list": {
        "ko": "jige로 설치한 목록 (brew list / port installed)",
        "en": "List apps jige has installed (like brew list / port installed)",
        "ja": "jigeでインストールした一覧 (brew list / port installed 相当)",
    },
    "help_upgrade": {
        "ko": "설치된 앱 최신판으로 재설치 (brew upgrade / port upgrade)",
        "en": "Reinstall installed apps at the latest version (like brew upgrade / port upgrade)",
        "ja": "インストール済みアプリを最新版に (brew upgrade / port upgrade 相当)",
    },
    "help_update": {
        "ko": "jige 자체를 최신 코드로 갱신 (brew update / port selfupdate)",
        "en": "Update jige itself to the latest code (like brew update / port selfupdate)",
        "ja": "jige自体を最新コードに更新 (brew update / port selfupdate 相当)",
    },
    "help_config": {
        "ko": "jige 설정 보기/변경 (예: Mac App Store 켜기/끄기)",
        "en": "View/change jige settings (e.g. turn Mac App Store search on/off)",
        "ja": "jigeの設定を表示/変更(例: Mac App Store検索のON/OFF)",
    },
    "help_completion": {
        "ko": "탭 자동완성 스크립트 출력 (예: source <(jige completion zsh))",
        "en": "Print the shell tab-completion script (e.g. source <(jige completion zsh))",
        "ja": "タブ補完スクリプトを出力 (例: source <(jige completion zsh))",
    },
}


def detect_lang() -> str:
    env = os.environ.get("JIGE_LANG")
    if env in ("ko", "en", "ja"):
        return env
    locale_str = ""
    if platform.system() == "Darwin":
        try:
            locale_str = subprocess.check_output(
                ["defaults", "read", "-g", "AppleLocale"], text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except Exception:
            pass
    if not locale_str:
        locale_str = os.environ.get("LANG", "")
    locale_str = locale_str.lower()
    if locale_str.startswith("ko"):
        return "ko"
    if locale_str.startswith("ja"):
        return "ja"
    return "en"


LANG = detect_lang()


def t(key: str, **kwargs) -> str:
    text = STRINGS.get(key, {}).get(LANG) or STRINGS.get(key, {}).get("en") or key
    return text.format(**kwargs) if kwargs else text
