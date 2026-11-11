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
이름             종류  분류  버전    설명
-----------------------------------------------------------
virtualbox       💻    brew ▼🆕7.2.22  Virtualiser for arm64 hardware
virtualbox@6     💻    brew  6.1.50  Virtualiser for x86 hardware

설치: jige install <이름>
      (Homebrew Cask는 지금 설치 가능, 나머지는 추후 지원)
  ▼ 이 macOS에 맞춘 대체판 — 자세히: jige info <이름>

$ jige info virtualbox            # ▼가 뜬 이유·근거 자료는 search가 아니라 여기서
이름       : Oracle VirtualBox
...
대체판     : 7.1.12,169651 (이 Mac에서 동작 확인됨 — 그 커밋의 depends_on macos: 선언으로 확인)
신뢰도     : 🆕 방금 등록됨 (공식 문서로 확인, 다른 사용자 확인 아직 없음)
근거       : https://raw.githubusercontent.com/Homebrew/homebrew-cask/6f1edd4b.../Casks/v/virtualbox.rb

$ jige install virtualbox
macOS 코드네임: monterey / 아키텍처: x86_64
레시피: ['Oracle VirtualBox'] (Homebrew-Cask 공개 레시피, 등록 버전 7.2.22,175245)

참고: 이 Mac은 macOS monterey(12.7.6)입니다.

  최신판   7.2.22,175245
  대체판   7.1.12,169651  (근거: depends_on, 신뢰도: 🆕 방금 등록됨 ...)

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

### macOS 호환 과거 버전은 어디서 오나 — Homebrew git 기록을 "라이브"로

최신판이 이 macOS를 더 이상 지원 안 할 수도 있는데, Homebrew-Cask의 `depends_on.macos`가
비어있는 경우가 많아서(실제로 VirtualBox도 비어있음) "최신판이 언제부터 이 macOS를 지원
안 했는지"는 AI가 추측할 수 없습니다. 그래서 jige는 **Homebrew-Cask 저장소 자체의 git
커밋 기록**을 직접 뒤져서, 과거 어느 시점 cask 정의가 이 macOS에서 통했는지 기계적으로
찾아냅니다(AI 판단 없음):

1. 그 시점 cask가 `depends_on macos:`를 선언해뒀으면 그 값으로 판단
2. 안 해놨으면(VirtualBox가 이 경우) 그 버전의 실제 설치 파일을 받아서 `Info.plist`의
   `LSMinimumSystemVersion`을 직접 읽어 판단 — AI의 판단이 아니라 파일 자체의 사실

찾아낸 커밋의 raw URL(`https://raw.githubusercontent.com/Homebrew/homebrew-cask/<커밋SHA>/
Casks/v/virtualbox.rb` 형태)을 brew가 `brew install --cask <url>`로 하는 것과 똑같이 바로
설치에 씁니다 — url/sha256은 그 커밋에 적힌 값을 그대로 쓰고, 체크섬은 직접 재계산합니다.

`jige install <토큰>`을 돌리면:
- `recipes/legacy/<token>.json`에 이 macOS 메이저 버전용 커밋이 이미 저장돼 있으면 바로 씀
- 없고 최신판이 이 macOS를 못 쓴다고 이미 알려져 있으면(`depends_on.macos` 기준) 그 자리에서
  git 기록을 뒤져서 즉석으로 찾음 (`--find-legacy`로 강제 검색도 가능)
- 찾으면 "최신판 X / 대체판 Y, 어느 걸 설치할까요?"로 한 번만 물어보고, 그다음은 자동 진행
- 한 번 찾은 결과는 `~/Library/Caches/jige/legacy_discoveries.json`에 로컬 저장해서
  같은 토큰을 다시 설치할 때 매번 git 기록을 다시 안 뒤짐

`recipes/legacy/<token>.json` 스키마는 아주 단순합니다 — macOS 메이저 버전별로 커밋 URL
하나씩(예시: [recipes/legacy/virtualbox.json](recipes/legacy/virtualbox.json)):

```json
{
  "12": {
    "commit_url": "https://raw.githubusercontent.com/Homebrew/homebrew-cask/<커밋SHA>/Casks/v/virtualbox.rb",
    "found_by": "depends_on 또는 info_plist",
    "confirmations": []
  }
}
```

이 기기가 직접 찾아낸 값을 저장소에도 올릴 수 있게, 커밋 URL을 그대로 쓰거나
`tools/legacy_finder.py <토큰> --target-macos <번호>`로 미리 찾아볼 수 있습니다. 단,
**Homebrew 자체가 벤더의 모든 패치 릴리스를 따라가진 않아서**(예: VirtualBox는 Homebrew가
7.1.12에서 7.2.0으로 건너뛰어 7.1.18 커밋이 아예 없음) 벤더가 낸 최신 호환 패치가 아니라
"Homebrew가 추적한 범위 안에서 가장 가까운 버전"을 찾아준다는 한계가 있습니다.

`recipes/legacy/<token>.json`은 이 저장소에 로컬로 있으면 그걸 우선 쓰고, 없으면
`raw.githubusercontent.com`의 `main` 브랜치 버전을 Homebrew 인덱스와 똑같은 24시간
캐시로 받아옵니다 — PR이 머지되면 `jige update` 없이도 하루 안에 모든 사용자에게 퍼집니다.

대체판으로 설치하면 `jige list`에도 그 사실과 최신판 정보가 남습니다
(`audacity   3.6.4 (대체판, 최신판은 4.0.2)`) — macOS를 업그레이드하고 `jige upgrade`를
다시 돌리면 그때는 최신판이 설치됩니다.

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
