# jige (지게)

**brew 없이도, port 없이도 Mac에 맞는 앱을 찾아서 설치해주는 도구.**

🔗 [hoyacom.github.io/jige](https://hoyacom.github.io/jige/) · [한국어](https://hoyacom.github.io/jige/ko/) · [日本語](https://hoyacom.github.io/jige/ja/) · [변경 기록](CHANGELOG.md)

지게는 짐을 지고 어디든 날라다 주는 한국 전통 운반 도구입니다.

## 설치

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/hoyacom/jige/main/install.sh)"
```

`~/.jige`에 받고, `jige` 명령과 탭 자동완성(zsh/bash)을 연결합니다.
셸 설정 파일을 건드리지 않으려면 앞에 `JIGE_NO_MODIFY_RC=1`을 붙이세요.

## 사용법

```console
$ jige search hop
이름                   종류  분류  버전      설명
hop                    💻    brew *0.5.1     View and edit HWP documents
hopenpgp-tools         🔧    brew  0.26.1    Command-line tools for OpenPGP-related operations...

$ jige install hop
```

| 명령 | brew / port에서는 |
|---|---|
| `jige search <검색어>` | `search` |
| `jige install <이름>` | `install` |
| `jige info <이름>` | `info` |
| `jige upgrade [이름]` | `upgrade` |
| `jige list` | `list` / `installed` |
| `jige uninstall <이름> [--zap]` | `uninstall` |
| `jige update` | `update` / `selfupdate` |
| `jige config mas on\|off` | Mac App Store 검색 켜기/끄기 (기본 꺼짐) |

기호: `💻` GUI 앱(**jim**, 짐) · `🔧` CLI 도구(**dogu**, 도구) · `*` 설치됨 · `▼` 이 macOS용 대체판(`jige info`로 자세히)

## 어디서 가져오나

이미 있는 공개 데이터를 읽기만 합니다. 이 기기에 brew·port가 없어도 됩니다.

- **Homebrew** — `formulae.brew.sh` 공개 API, Homebrew-Cask git 기록(최신판이 이 macOS를 지원하지 않을 때 과거 버전 찾기)
- **MacPorts** — `ports.macports.org` 공개 API (검색만)
- **Mac App Store** — Apple 공개 검색 API, 설치는 `mas` 필요
- **이 저장소** — 위 어디에도 없는 것만 `recipes/`에

다운로드한 파일은 레시피의 sha256으로 검증한 뒤 설치합니다.

## 한계

- 설치는 GUI 앱(jim)만 됩니다. CLI 도구(dogu)와 MacPorts는 아직 검색만 됩니다.
- 과거 버전은 Homebrew가 기록해둔 버전 중에서만 찾습니다(벤더의 모든 패치가 있지는 않음).

## 라이선스

[GPLv3](LICENSE)

jige는 Homebrew·MacPorts 프로젝트와 관계없는 별도 도구입니다. Homebrew의 레시피 데이터는
[BSD-2-Clause](https://github.com/Homebrew/homebrew-cask/blob/master/LICENSE)로 공개된 것을 읽어서 씁니다.
