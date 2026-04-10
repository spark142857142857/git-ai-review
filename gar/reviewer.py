"""Gemini API를 이용한 코드 리뷰어."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = "gemini-2.0-flash-lite"

SYSTEM_PROMPT = """\
You are an expert code reviewer. Analyze the provided git diff and respond in Korean \
using ONLY the section format below. Omit any section that has no issues.
If there are absolutely no issues across all sections, respond with exactly one line: ✅ 문제 없음

## 🐛 버그/잠재적 오류
(버그, 예외 미처리, 경계값 오류 등 — 문제 없으면 이 섹션 생략)

## ⚡ 성능
(불필요한 연산, 비효율적 자료구조, N+1 쿼리 등 — 문제 없으면 이 섹션 생략)

## 🔒 보안
(인젝션, 민감 정보 노출, 권한 검사 누락 등 — 문제 없으면 이 섹션 생략)

## 💡 개선 제안
(가독성, 네이밍, 중복 제거, 더 나은 대안 등 — 문제 없으면 이 섹션 생략)

## ✅ 총평
(한두 줄 요약 — 항상 포함)
"""

REVIEW_TEMPLATE = """\
다음 파일의 변경 사항을 리뷰해줘.

**파일**: `{path}`

```diff
{diff}
```
"""


@dataclass
class ReviewResult:
    path: str
    review: str
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


def _get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY가 설정되지 않았습니다. "
            ".env 파일 또는 환경변수를 확인하세요."
        )
    return genai.Client(api_key=api_key)


def review_file(
    file_diff,
    client: genai.Client | None = None,
) -> ReviewResult:
    """단일 파일 diff를 Gemini에 보내고 리뷰를 받는다."""
    if client is None:
        client = _get_client()

    prompt = REVIEW_TEMPLATE.format(
        path=file_diff.path,
        diff=file_diff.diff_text[:8000],  # 토큰 초과 방지
    )

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )
        return ReviewResult(path=file_diff.path, review=response.text)
    except Exception as exc:  # noqa: BLE001
        return ReviewResult(path=file_diff.path, review="", error=str(exc))


def review_all(file_diffs: list) -> list[ReviewResult]:
    """여러 파일을 병렬로 리뷰하되 입력 순서를 유지한다."""
    client = _get_client()
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(review_file, fd, client) for fd in file_diffs]
    return [f.result() for f in futures]
