# git-ai-review (`gar`)

git diff를 자동으로 읽어서 Gemini AI로 코드 리뷰를 출력하는 CLI 도구.

## 빠른 시작

```bash
# 1. 가상환경 생성 및 활성화
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2. 패키지 설치 (편집 가능 모드)
pip install -e ".[dev]"

# 3. 환경변수 설정
cp .env.example .env
# .env 파일을 열어 GEMINI_API_KEY 값을 입력

# 4. 리뷰 실행
gar review
```

## 사용법

```
gar review [OPTIONS]

Options:
  -s, --staged              staged 변경사항만 리뷰 (git diff --staged)
  -c, --commit TEXT         특정 커밋 해시 리뷰 (예: abc1234)
  -o, --output [terminal|md]  출력 형식 (기본: terminal)
  -f, --output-file PATH    마크다운 저장 경로 (--output md 시 사용)
  -r, --repo PATH           git 리포지터리 경로 (기본: 현재 디렉토리)
  -V, --version             버전 출력
  --help                    도움말
```

## 예시

```bash
# 현재 변경사항 리뷰 (git diff HEAD)
gar review

# staged 변경사항만 리뷰
gar review --staged

# 특정 커밋 리뷰
gar review --commit abc1234

# 마크다운 파일로 저장
gar review --output md

# 저장 경로 직접 지정
gar review --output md --output-file my_review.md
```

## 개발

```bash
# 테스트 실행
pytest

# 특정 파일만 테스트
pytest tests/test_git_utils.py -v
```

## 환경변수

| 변수 | 설명 |
|------|------|
| `GEMINI_API_KEY` | Google AI Studio API 키 (필수) |

API 키는 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급받을 수 있습니다.
