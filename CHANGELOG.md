# 변경 기록

## 다음 버전 (아직 안 나옴)

- 탭 자동완성 (zsh, bash). 설치할 때 자동으로 연결되고, `JIGE_NO_MODIFY_RC=1`이면 설정 파일을 건드리지 않음
- `jige completion zsh|bash` 추가
- Homebrew 인덱스를 gzip으로 받고, 바뀌지 않았으면 다시 받지 않음 (cask 인덱스 19.4MB → 2.1MB)

## 0.2.1

- search: 띄어쓴 검색어 에러, 공백·하이픈을 무시한 매칭이 안 되던 문제 수정

## 0.2.0

- `.pkg` 방식 앱 설치
- 최신판이 이 macOS를 지원하지 않으면 Homebrew-Cask git 기록에서 과거 버전을 찾아 설치

## 0.1.0

- 첫 공개
