# git-ai-review (`gar`)

[English](README.md)

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Model](https://img.shields.io/badge/model-gemini--2.5--flash--lite-orange)
[![PyPI version](https://img.shields.io/pypi/v/git-ai-review)](https://pypi.org/project/git-ai-review/)
[![Python versions](https://img.shields.io/pypi/pyversions/git-ai-review)](https://pypi.org/project/git-ai-review/)

`git diff`를 자동으로 읽어서 Gemini API로 AI 코드 리뷰를 출력하는 CLI 도구.

---

## 주요 기능

- `git diff` 자동 실행 — 워킹트리, staged, 특정 커밋 모두 지원
- 파일별 리뷰를 **버그**, **성능**, **보안**, **개선 제안**, **총평** 섹션으로 구분 출력
- Gemini API 병렬 호출 (최대 3개 파일 동시 처리) 로 빠른 응답
- Rich 터미널 패널과 스피너로 깔끔한 출력
- `--output md` 옵션으로 마크다운 파일 저장
- 첫 번째 커밋도 안전하게 처리 (`git diff HEAD^` 대신 `git show` 사용)
- 바이너리 파일 자동 감지 및 안전한 스킵

---

## 설치

```bash
# 1. 레포지터리 클론
git clone https://github.com/spark142857142857/git-ai-review.git
cd git-ai-review

# 2. 가상환경 생성 및 활성화
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. 편집 가능 모드로 설치 (개발 의존성 포함)
pip install -e ".[dev]"
```

---

## 환경 설정

예제 파일을 복사하고 API 키를 입력합니다:

```bash
cp .env.example .env
```

`.env` 파일을 열어 다음을 설정합니다:

```
GEMINI_API_KEY=발급받은_API_키
```

API 키는 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 무료로 발급받을 수 있습니다.

---

## 사용법

```
gar review [OPTIONS]

Options:
  -s, --staged                  staged 변경사항만 리뷰 (git diff --staged)
  -c, --commit TEXT             특정 커밋 해시 리뷰 (예: abc1234)
  -o, --output [terminal|md]    출력 형식 — terminal (기본) 또는 md
  -f, --output-file PATH        마크다운 저장 경로 (--output md 사용 시)
  -r, --repo PATH               git 리포지터리 경로 (기본: 현재 디렉토리)
  -l, --lang TEXT               리뷰 언어: en (기본, 영어) 또는 ko (한국어)
  -V, --version                 버전 출력
  --help                        도움말
```

### 예시

```bash
# 현재 워킹트리 변경사항 리뷰 (git diff HEAD)
gar review

# staged 변경사항만 리뷰
gar review --staged

# 특정 커밋 리뷰
gar review --commit abc1234

# 한국어로 리뷰
gar review --lang ko

# 마크다운 파일로 저장 (파일명 자동 생성)
gar review --output md

# 저장 경로 직접 지정
gar review --output md --output-file reviews/sprint42.md

# 다른 디렉토리의 레포지터리 리뷰
gar review --repo ../other-project
```

---

## Pre-commit Hook

`gar`를 git pre-commit hook으로 등록하면 커밋 전마다 staged 변경사항을 자동으로 리뷰합니다.

```bash
# hook 설치
gar install-hook

# hook 제거
gar uninstall-hook
```

설치 후 `git commit` 실행 시마다 `gar review --staged`가 자동으로 실행되어 리뷰 결과를 터미널에 출력합니다. 리뷰 결과에 따라 커밋이 **차단되지는 않습니다** — 참고용 출력입니다.

기존 hook이 있는 경우 덮어쓸지 확인 프롬프트가 표시됩니다.

---

## 개발

```bash
# 전체 테스트 실행
pytest

# 상세 출력
pytest -v

# 특정 테스트 모듈만 실행
pytest tests/test_git_utils.py -v
```

---

## 기여 방법

1. 레포지터리를 포크하고 기능 브랜치를 생성합니다.
2. 변경 사항을 만들고 필요한 경우 테스트를 추가합니다.
3. `pytest`가 모두 통과하는지 확인합니다.
4. 변경 내용을 명확히 설명한 Pull Request를 열어주세요.

PR은 하나의 주제에 집중해 주세요.
