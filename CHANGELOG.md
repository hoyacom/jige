# 변경 기록

## 0.5.2 (2026-11-17)

고친 것
- `raw.githubusercontent.com`에서 과거 커밋 정보를 받아오는 두 요청(legacy 커밋 찾기, .rb
  직접 파싱)이 자체 User-Agent를 지정하고 있어서, 맨 위에서 503 회피용으로 설정해둔 전역
  User-Agent를 그 두 곳에서만 조용히 무력화하고 있던 문제 수정

새 기능
- README에 사용자 레포지토리(`jige user-repo`) 기능 노출 (v0.5.0에서 추가됐는데 문서에
  전혀 안 보였음)

내부
- `tests/`에 unittest 53개 추가 — 순수 함수 회귀 테스트
- 단일 파일이던 `jige`에서 i18n/GitHub 링크/터미널 표시 부분을 `jigelib/` 패키지로 분리
  시작(동작 변화 없음, 나머지 섹션은 다음에 이어서 분리 예정)

## 0.5.1 (2026-11-17)

고친 것
- install.sh: Xcode CLT는 있는데(`xcode-select -p` 성공) Xcode 라이선스 동의가
  안 된 상태(예: Xcode.app은 깔려있는데 한 번도 안 열어본 경우)를 못 잡아서,
  안내 없이 git clone 하다가 Apple의 긴 라이선스 텍스트가 갑자기 튀어나오던
  문제 — Big Sur에서 실제로 겪음(페이저 끝까지 못 보고 agree 입력 못 한 채 종료).
  `git --version`으로 조용히 먼저 확인해서, 문제면 `sudo xcodebuild -license
  accept`를 안내하고 멈춤(페이저 자체가 아예 안 뜨게 됨).

## 0.5.0 (2026-11-17)

새 기능
- **사용자 레포지토리** — 집 NAS·회사 서버 등 사용자가 직접 등록하는 저장소.
  `jige user-repo add/remove/list`로 관리, `jige user-repo scan`으로 "버전 폴더 안에
  아키텍처별 파일" 구조를 자동으로 훑어 카탈로그 생성, `jige user-repo add-file`로 파일
  하나씩 등록. local path / http(s) / ssh 지원(SMB·WebDAV는 Finder로 이미 마운트된
  local path로 사용). 인증은 jige가 저장하지 않고 `~/.netrc`(Basic)나 등록 시 지정한
  환경변수(Bearer)를 그때그때 읽음. 각 파일에 platform/arch/min_os를 적어두면(생략 시
  전부 지원으로 간주) 설치할 때 이 머신에 맞는 걸 자동으로 고름
- `--brew`/`--port`를 하나의 `--repo <이름>`으로 통합 — brew/port뿐 아니라 등록한 사용자
  레포 이름도 지정 가능. 사용자 레포지토리끼리 토큰이 겹치면 등록 순서로 조용히 해결하지만,
  brew/port ↔ 사용자 레포처럼 서로 다른 생태계가 겹치면 여전히 자동 선택 안 하고 물어봄
  (버전+설명을 같이 보여줌)
- 설치 상태(`installed.json`)에 어느 소스로 설치했는지(`source`) 기록

## 0.4.0 (2026-11-16)

새 기능
- `install`/`info`에 `--brew`/`--port` 옵션 추가. 토큰이 Homebrew(cask/formula)와 MacPorts에
  동시에 정확히 일치하면(예: `mole` — brew formula는 Mac 클리너, MacPorts port는 ssh 터널
  도구로 서로 다른 프로그램) 자동으로 아무거나 고르지 않고 어느 쪽인지 명시하게 함
- `info`가 이제 Homebrew formula·MacPorts port의 상세(버전/홈페이지/설명)도 보여줌
  (전엔 cask·로컬 레시피·Mac App Store만 봐서 formula/port는 아예 조회가 안 됐음)

## 0.3.0 (2026-11-14)

새 기능
- 탭 자동완성 (zsh, bash). 설치할 때 자동으로 연결되고, `JIGE_NO_MODIFY_RC=1`이면 설정 파일을 건드리지 않음.
  `jige completion zsh|bash`로 스크립트 출력
- 설치를 "포장 풀기 → 설치" 두 단계로 정리: zip·tar.gz·tar.xz·겹친 포장 앱, 앱 폴더(suite),
  설치 프로그램(installer)도 설치됨. 앱 레시피 기준 설치 가능 범위 약 64% → 96%
- uninstall이 레시피의 제거 단계(앱 종료, 로그인 항목, launchctl, pkgutil 기록 기반 파일 삭제 등)를
  Homebrew와 같은 순서로 실행 — `.pkg`로 설치한 앱도 제거됨
- 테스트용 `JIGE_APPDIR` (앱 설치 위치 바꾸기, brew `--appdir`와 같음)

고친 것
- 다운로드가 `.pkg` 파일 하나인 앱(Tailscale 등) 설치가 실패하던 문제
- `--zap`이 와일드카드(`*`) 경로를 처리하지 못하던 문제
- 설치 실패 시 Python 오류(traceback) 대신 이유를 한 줄로 안내
- Homebrew 인덱스를 압축 없이 매일 통째로 받던 것 → gzip + 바뀌었을 때만 받기 (19.4MB → 2.1MB)

## 0.2.1

- search: 띄어쓴 검색어 에러, 공백·하이픈을 무시한 매칭이 안 되던 문제 수정

## 0.2.0

- `.pkg` 방식 앱 설치
- 최신판이 이 macOS를 지원하지 않으면 Homebrew-Cask git 기록에서 과거 버전을 찾아 설치

## 0.1.0

- 첫 공개
