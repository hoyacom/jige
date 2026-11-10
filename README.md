# jige (지게)

Homebrew 없이도 [Homebrew-Cask](https://github.com/Homebrew/homebrew-cask)의 공개 레시피를
그대로 읽어서 macOS 앱을 설치·업데이트하는 아주 작은 도구입니다.

**이름 유래**: 지게는 짐을 지고 어디든 날라다 주는 한국 전통 운반 도구입니다.
이 도구도 "패키지를 지고 이 기기로 날라다 설치한다"는 뜻으로 지었습니다.

## 왜 만들었나

Mac이 여러 대(Apple Silicon, Intel + Homebrew, Intel + MacPorts)인데, 전부 Homebrew를
설치해서 통일하고 싶지는 않았습니다. 그런데 Homebrew-Cask는 "어떤 OS/아키텍처에
어떤 파일을, 어떤 체크섬으로" 받아야 하는지를 이미 공개 JSON API로 깔끔하게 정리해
두고 커뮤니티가 계속 최신 버전으로 갱신해줍니다. `jige`는 이 JSON만 HTTP로 읽어서
brew 바이너리 없이 같은 정보를 활용합니다.

- **이미 있는 레포(Homebrew-Cask)가 있으면 그걸 그대로 래핑**해서 씁니다.
- **없는 앱만** 이 저장소의 `recipes/<token>.json`에 같은 스키마로 직접 추가합니다
  (NAS 등 어디에 올려두고 내부에서 URL만 가리키게 해도 동일하게 동작합니다).

커스텀 포맷을 새로 만들지 않아서, 유지보수할 게 이 작은 스크립트 하나뿐입니다.

## 설치

```bash
ln -sf "$(pwd)/jige" /usr/local/bin/jige
```

## 사용법

```bash
jige search dbeaver   # 어디 소속인지(Homebrew Cask/CLI, MacPorts, 자체 레포지토리) 분류해서 통합 검색
jige install hop      # 설치/업데이트
```

사용자는 brew가 있는지, MacPorts인지, 어떤 아키텍처인지 몰라도 됩니다 —
`jige`가 이 기기(`sw_vers`/`uname -m`)에 맞춰 알아서 찾습니다.

### search

세 곳을 동시에 뒤져서 한 표로 보여줍니다:

1. **Homebrew(Cask/CLI)** — `formulae.brew.sh`의 전체 목록(cask.json/formula.json)을
   로컬에 캐시(24시간)해두고 이름·설명으로 찾음. macOS/Linux 둘 다 커버.
2. **MacPorts** — `ports.macports.org`의 공개 검색 API를 그대로 호출(macOS에서만).
3. **자체 레포지토리** — 이 저장소의 `recipes/*.json`.

**셋 다 그냥 공개 HTTP API라서, 이 기기에 brew나 port 명령이 전혀 없어도 검색은 됩니다**
(Homebrew·MacPorts를 설치하지 않은 기기에서도 똑같이 동작).

### install

1. `recipes/<token>.json`이 있으면 그걸, 없으면
   `https://formulae.brew.sh/api/cask/<token>.json`을 읽음
2. 이 기기에 맞는 다운로드 URL·sha256을 레시피에서 고름
3. 다운로드(`~/Library/Caches/jige/downloads/`에 캐시) 후 sha256 검증
4. DMG를 마운트해서 `.app`을 `/Applications`로 복사, 마운트 해제
5. 설치 전/후 버전을 `Info.plist`에서 확인해서 출력

## 현재 범위 / 다음에 할 일

- `install`은 아직 DMG 안에 `.app`이 바로 들어있는 **Homebrew-Cask 항목만** 설치합니다.
- `search`로 나온 **MacPorts/Homebrew(CLI) 결과는 아직 jige가 직접 설치 안 함** — 포트/포뮬러 빌드는
  각 패키지 매니저 자체 기능을 그대로 쓰는 쪽(예: `sudo port install`)으로 다음에 연결할 계획.
  (brew/MacPorts 자체를 설치하라는 뜻이 아니라, 둘 다 없는 기기에서도 쓸 수 있게
  `recipes/`로 자체 설치를 늘려가는 쪽이 기본 방향.)
- `recipes/`는 아직 예시가 없습니다 — Homebrew-Cask/MacPorts에 둘 다 없는 앱이 생기면 추가합니다.
