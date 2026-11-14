# 변경 기록

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
