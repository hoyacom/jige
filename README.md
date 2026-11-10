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
jige install hop
```

1. `sw_vers`/`uname -m`으로 이 기기의 macOS 코드네임·아키텍처를 확인
2. `recipes/<token>.json`이 있으면 그걸, 없으면
   `https://formulae.brew.sh/api/cask/<token>.json`을 읽음
3. 이 기기에 맞는 다운로드 URL·sha256을 레시피에서 고름
4. 다운로드(`~/Library/Caches/jige/downloads/`에 캐시) 후 sha256 검증
5. DMG를 마운트해서 `.app`을 `/Applications`로 복사, 마운트 해제
6. 설치 전/후 버전을 `Info.plist`에서 확인해서 출력

## 현재 범위 / 다음에 할 일

- DMG 안에 `.app`이 바로 들어있는 Cask만 지원합니다(pkg, zip, 중첩 폴더 등은 아직 미지원).
- `recipes/`는 아직 예시가 없습니다 — Homebrew-Cask에 없는 앱이 생기면 추가합니다.
- `jige list` / `jige search` 같은 보조 명령은 필요해지면 추가합니다(지금은 없음).
