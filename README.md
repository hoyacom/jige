# jige (지게)

**brew 없이도, port 없이도 Mac에 맞는 앱을 찾아서 설치해주는 도구.**

지게는 짐을 등에 지고 어디든 날라다 주는 한국 전통 운반 도구입니다.
이 도구도 "패키지를 지고 이 기기로 날라다 설치한다"는 뜻으로 지었습니다.

## 설치 (새 Mac에서 딱 한 줄)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/hoyacom/jige/main/install.sh)"
```

Homebrew도 없고 MacPorts도 없는 기기여도 상관없습니다. 위 한 줄이 하는 일:
1. `jige` 저장소를 받아서 `~/.jige`에 둠
2. `jige` 스크립트를 `/usr/local/bin/jige`에 연결
3. 바로 `jige search ...` / `jige install ...` 사용 가능

## 짐(jim)과 도구(dogu)

Homebrew가 설치 대상을 **formula**(터미널용)와 **cask**(Dock에 뜨는 GUI 앱)로 나누듯,
jige는 OS에 상관없이 똑같은 질문 하나로 나눕니다:

> **"설치하면 Dock/런처에 아이콘이 생겨서 더블클릭으로 띄우는 독립 프로그램인가?"**

| jige 용어 | 뜻 | 대응하는 것 |
|---|---|---|
| **jim** (짐 — 지게에 통째로 얹는 짐) | Dock/런처 아이콘이 생기는 GUI 앱 | Homebrew의 **cask** |
| **dogu** (도구 — 지게꾼이 손에 쥐고 바로 쓰는 연장) | 터미널에서 직접 쓰는 명령/라이브러리 | Homebrew의 **formula** |

`jige search`에 "종류" 컬럼으로 바로 보여줍니다. Homebrew Cask는 전부 `jim`, Homebrew
Formula는 전부 `dogu`로 확실하게 분류되고, MacPorts 쪽은 아직 `unknown`(포트파일까지
뜯어봐야 아는 정보라 다음 단계에서 보강 예정)입니다.

## 사용법

```console
$ jige search hop
이름                   종류  분류  버전      설명
-----------------------------------------------------------------
hop                    💻    brew *0.5.1     View and edit HWP documents
hopper-disassembler    💻    brew  6.6.2     Reverse engineering tool that lets you disassemble...
hopenpgp-tools         🔧    brew  0.26.1    Command-line tools for OpenPGP-related operations...

설치: jige install <이름>
      (Homebrew Cask는 지금 설치 가능, 나머지는 추후 지원)
  * 이미 설치됨

$ jige install hop
macOS 코드네임: monterey / 아키텍처: x86_64
레시피: HOP (Homebrew-Cask 공개 레시피, 등록 버전 0.5.2)
선택된 다운로드: https://github.com/golbin/hop/releases/download/v0.5.2/HOP-macos-x64.dmg
다운로드: https://github.com/golbin/hop/releases/download/v0.5.2/HOP-macos-x64.dmg
sha256 체크섬 일치 확인됨.
/Volumes/jige-HOP.app/HOP.app -> /Applications/HOP.app

완료: HOP.app  0.3.1 -> 0.5.2

$ jige search hop --mas          # Mac App Store까지 이번만 포함
...
Hop - Endless Arcade Hopper  💻  mas   1.6       Limitless LLC

$ jige install "아스팔트: 레전드" --mas
레시피: 아스팔트: 레전드 (Mac App Store, 등록 버전 53.5.3)
mas install 1491129197 실행 중...
완료: 아스팔트: 레전드 (Mac App Store, id 1491129197, 버전 53.5.3)

$ jige search virtualbox          # macOS Monterey에서 — 최신 7.2.22는 Ventura(13) 이상이 필요
이름             종류  분류  버전         설명
--------------------------------------------------------------
virtualbox       💻    brew ▼🆕7.1.18  Virtualiser for arm64 hardware
virtualbox@6     💻    brew  6.1.50     Virtualiser for x86 hardware

설치: jige install <이름>
      (Homebrew Cask는 지금 설치 가능, 나머지는 추후 지원)
  ▼ 이 macOS에 맞춘 대체판 — 자세히: jige info <이름>

$ jige info virtualbox            # ▼가 뜬 이유·근거 자료는 search가 아니라 여기서
이름       : Oracle VirtualBox
...
대체판     : 7.1.18 (이 Mac macOS 11~14 지원)
필요한 이유 : 최신판은 macOS 13 이상 필요 — 벤더가 EOL(지원 종료) 선언함
신뢰도     : 🆕 방금 등록됨 (공식 문서로 확인, 다른 사용자 확인 아직 없음)
근거       : (...) https://docs.oracle.com/...

$ jige install virtualbox
macOS 코드네임: monterey / 아키텍처: x86_64
레시피: ['Oracle VirtualBox'] (Homebrew-Cask 공개 레시피, 등록 버전 7.2.22,175245)

참고: 이 Mac은 macOS monterey(12.7.6)입니다.

  최신판   7.2.22,175245 macOS 13 이상 필요 → 이 Mac에서 설치 안 될 가능성 높음
  대체판   7.1.18     macOS 11~14 지원, 이 Mac에서 동작 확인됨 (참고: Oracle 기준 더 이상 지원 안 하는 EOL 버전)

어느 걸 설치할까요? [1] 대체판(추천)  [2] 최신판(강행)  번호 [1]:
...
관리자 권한(sudo)이 필요합니다 — 비밀번호를 입력하세요.
```

`search` 결과의 기호: `💻` GUI 앱(jim) · `🔧` CLI 도구(dogu) · `*` 이미 설치됨 · `▼`+신뢰도
이 macOS에 맞춘 대체판(자세한 이유·근거는 `jige info <이름>`). 마커는 분류-버전 사이 기본
간격(2칸) 안에 끼워 넣어서(없으면 두 칸 공백, 있으면 그만큼 앞 공백을 줄임) 버전 숫자가
마커 유무와 상관없이 항상 같은 자리에서 시작합니다 — `*`는 ★ 대신 그냥 아스키 별표를 써서
(버전은 항상 숫자라 헷갈릴 일이 없고, 폭도 항상 정확히 1칸이라 계산이 흔들리지 않음) 유니코드
지원 여부와 무관하게 똑같이 나옵니다. UTF-8을 지원 안 하는 터미널에선 `▼`만 `v`로, `💻`/`🔧`는
`GUI`/`CLI`로 자동으로 바뀝니다. `분류` 칸은 실제 명령어 이름을 그대로 씀(Homebrew는 `brew`,
MacPorts는 `port`, Mac App Store는 `mas`).

사용자는 brew가 있는지, MacPorts인지, 어떤 아키텍처인지 몰라도 됩니다 —
`jige`가 이 기기(`sw_vers`/`uname -m`)에 맞춰 알아서 맞는 파일을 찾습니다.

### 명령어 (brew / port 둘 다 쓰는 이름과 맞춤)

| jige | 같은 뜻의 brew 명령 | 같은 뜻의 port 명령 |
|---|---|---|
| `jige search <검색어>` | `brew search` | `port search` |
| `jige install <이름>` | `brew install` | `port install` |
| `jige info <이름>` | `brew info` | `port info` |
| `jige upgrade [이름]` | `brew upgrade` | `port upgrade` |
| `jige list` (별칭 `installed`) | `brew list` | `port installed` |
| `jige config mas on\|off` | — (jige 전용, Mac App Store 검색/설치 on/off) | — |
| `jige uninstall <이름>` (별칭 `remove`) | `brew uninstall`/`remove` | `port uninstall` |

### search는 어디를 뒤지나

1. **Homebrew (Cask/Formula)** — `formulae.brew.sh`의 전체 목록을 로컬에 캐시(24시간)해서
   이름·설명으로 찾음. macOS/Linux 둘 다 커버.
2. **MacPorts** — `ports.macports.org`의 공개 검색 API(macOS에서만).
3. **Mac App Store** — `mas`가 내부적으로 쓰는 것과 같은 Apple의 공개 iTunes Search API(macOS에서만).
   `mas install`이 요구하는 숫자 ID를 몰라도, 앱 이름 그대로 검색·설치하면 됩니다.
   **기본은 꺼져 있습니다** (옛 Homebrew-Cask가 별도 tap이었던 것과 같은 자세 — mas를 안 쓰는
   사람한테 매번 검색마다 Apple 서버에 쏘는 건 낭비라서). 켜는 방법 둘:
   - `jige search <검색어> --mas` / `jige install <이름> --mas` — 이번 한 번만
   - `jige config mas on` — 계속 켜두기 (`jige config`로 현재 상태 확인, `off`로 다시 끔)
4. **자체 레포지토리** — 이 저장소의 `recipes/*.json`.

**넷 다 그냥 공개 HTTP API라서, 이 기기에 brew·port·mas가 전혀 없어도 검색은 됩니다**
(단, mas 쪽은 검색은 API로 하지만 실제 *설치*는 `mas` CLI와 로그인된 App Store 세션이 있어야 함).

### install은 어떻게 동작하나

**Homebrew-Cask·자체 레포지토리(jim)**:
1. `recipes/<token>.json`이 있으면 그걸, 없으면 Homebrew-Cask의 공개 레시피를 읽음
2. `recipes/legacy/<token>.json`에 이 기기의 macOS에서 쓸 수 있는 대체판이 큐레이션돼 있고
   최신판은 이 macOS를 지원 안 하는 걸로 돼 있으면, 안내하고 물어본 뒤 그 대체판으로 바꿈
   (비대화형 실행이면 자동으로 대체판 선택, `--latest`로 묻지 않고 최신판 강행 가능)
3. 이 기기의 macOS 코드네임·CPU 아키텍처에 맞는 다운로드 URL·sha256을 레시피에서 고름
4. 다운로드(`~/Library/Caches/jige/downloads/`에 캐시) 후 sha256 검증
5. DMG를 마운트해서 `.app`이 있으면 `/Applications`로 복사, `.pkg`(pre/postflight 스크립트가 있는
   설치 패키지)면 `sudo installer`로 그대로 설치 — 마운트 해제
6. `~/Library/Application Support/jige/installed.json`에 설치 기록 남김 (`list`/`upgrade`가 이걸 씀)

**Mac App Store**:
1. Homebrew-Cask에 없으면 iTunes Search API에서 이름이 정확히 일치하는 앱을 찾아 숫자 ID를 얻음
2. 그 ID로 `mas install <id>`를 그대로 호출 — 다운로드·인증은 로그인된 App Store 세션이 처리
   (비밀번호/Touch ID는 전부 macOS 시스템 UI가 처리, jige·mas 둘 다 credential을 다루지 않음)

### `recipes/legacy/`는 누가 채우나 — 커뮤니티, AI 아님

Homebrew-Cask의 `depends_on.macos`가 비어있는 경우가 많아서(실제로 VirtualBox도 비어있음),
"최신판이 이 macOS를 더 이상 지원 안 함"이란 지식은 AI가 자동으로 알아낼 수 없습니다 —
체크섬까지 AI가 추측하게 하면 jige의 핵심 안전장치(sha256 검증)가 무의미해지므로,
**이 정보는 항상 사람이 공식 홈페이지/문서를 직접 확인해서 등록**합니다.

`recipes/legacy/<token>.json`을 아래 형식으로 만들어서 PR 올리면 됩니다 — 실제 예시는
[recipes/legacy/virtualbox.json](recipes/legacy/virtualbox.json),
[recipes/legacy/audacity.json](recipes/legacy/audacity.json) 참고:

```json
{
  "versions": [
    {
      "version": "이 macOS에서 쓸 수 있는 구버전 번호 (예: 3.7.9)",
      "min_macos": "이 구버전이 지원하는 가장 낮은 macOS (숫자만, 예: 11)",
      "max_macos": "이 구버전이 지원하는 가장 높은 macOS (예: 12)",
      "latest_min_macos": "최신판이 요구하는 macOS (예: 13) — 이게 이 구버전이 필요한 이유",
      "vendor_status": "os_limit 또는 eol",
      "note": "근거 설명 (공식 문서·이슈 링크 포함)",
      "source": ["공식 자료 URL"],
      "confirmations": [],
      "url": "Apple Silicon(arm64)용 다운로드 URL",
      "sha256": "위 파일을 직접 받아서 shasum -a 256으로 직접 계산한 값",
      "variations": {
        "monterey": {"url": "Intel용 URL(arm64와 다르면)", "sha256": "직접 계산한 값"}
      }
    }
  ]
}
```

체크섬은 꼭 **직접 받은 파일로 직접 계산**해서 적어주세요 — 남이 적어둔 값을 베끼거나 AI가
알려준 값을 그대로 쓰면 jige의 sha256 검증이 무의미해집니다.

`recipes/legacy/<token>.json`은 이 저장소에 로컬로 있으면 그걸 우선 쓰고, 없으면
`raw.githubusercontent.com`의 `main` 브랜치 버전을 Homebrew 인덱스와 똑같은 24시간
캐시로 받아옵니다 — PR이 머지되면 `jige update` 없이도 하루 안에 모든 사용자에게 퍼집니다.

대체판으로 설치하면 `jige list`에도 그 사실과 최신판 정보가 남습니다
(`audacity   3.7.9 (대체판, 최신 4.0.2는 macOS 13+ 필요)`) — macOS를 업그레이드하고
`jige upgrade`를 다시 돌리면 그때는 최신판이 설치됩니다.

## 왜 만들었나

Mac이 여러 대(Apple Silicon, Intel+Homebrew, Intel+MacPorts)인데, 전부 Homebrew로
통일하고 싶지는 않았습니다. 그런데 Homebrew-Cask는 "어떤 OS/아키텍처에 어떤 파일을,
어떤 체크섬으로" 받아야 하는지를 이미 공개 JSON API로 정리해두고 커뮤니티가 계속
최신으로 갱신해줍니다. jige는 이 JSON만 HTTP로 읽어서 brew 바이너리 없이 같은
정보를 활용합니다 — **이미 있는 레포(Homebrew-Cask, MacPorts)는 그대로 래핑**하고,
**둘 다에 없는 것만** `recipes/`에 직접 추가합니다. 커스텀 포맷을 새로 만들지
않아서 유지보수할 게 이 작은 스크립트 하나뿐입니다.

## 라이선스

[GPLv3](LICENSE) — 누가 가져다 고치든 그 결과물도 계속 오픈소스로 남습니다.

## 현재 범위 / 다음에 할 일

- `install`은 DMG 안에 `.app`이 바로 들어있거나 `.pkg` 설치 패키지인 **Homebrew-Cask·Mac App
  Store·자체 레포지토리** 항목을 설치합니다.
- `search`로 나온 **MacPorts/Homebrew(CLI) 결과는 아직 jige가 직접 설치 안 함** — 각 패키지
  매니저 자체 기능을 그대로 쓰는 쪽(예: `sudo port install`)으로 다음에 연결할 계획.
- Linux는 Ubuntu(`apt`)·RedHat 계열(`dnf`)까지만 지원 범위로 다음에 추가합니다.
- MacPorts 결과의 `jim`/`dogu` 구분은 포트파일 상세조회로 다음에 보강합니다.
- `recipes/`는 아직 예시가 없습니다. `recipes/legacy/<token>.json`에는 예시가 하나 있습니다
  (`virtualbox.json` — 최신판이 더 이상 지원 안 하는 macOS에서 쓸 대체판 큐레이션, 스키마는
  `recipes/<token>.json`과 같은 cask 필드를 그대로 재사용).
