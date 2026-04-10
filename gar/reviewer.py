"""Code reviewer using the Gemini API."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = "gemini-2.5-flash-lite"

_SYSTEM_PROMPTS: dict[str, str] = {
    "en": """\
You are an expert code reviewer. Analyze the provided git diff and respond in English \
using ONLY the section format below. Omit any section that has no issues.
If there are absolutely no issues across all sections, respond with exactly one line: ✅ No issues found

## 🐛 Bugs / Potential Errors
(bugs, unhandled exceptions, boundary errors, etc. — omit if no issues)

## ⚡ Performance
(unnecessary computation, inefficient data structures, N+1 queries, etc. — omit if no issues)

## 🔒 Security
(injection, sensitive data exposure, missing authorization checks, etc. — omit if no issues)

## 💡 Suggestions
(readability, naming, deduplication, better alternatives, etc. — omit if no issues)

## ✅ Summary
(one or two sentence summary — always include)
""",
    "ko": """\
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
""",
}

REVIEW_TEMPLATE = """\
Review the following file changes.

**File**: `{path}`

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
            "GEMINI_API_KEY is not set. "
            "Check your .env file or environment variables."
        )
    return genai.Client(api_key=api_key)


def review_file(
    file_diff,
    client: genai.Client | None = None,
    lang: str = "en",
) -> ReviewResult:
    """Send a single file diff to Gemini and return the review."""
    if client is None:
        client = _get_client()

    system_prompt = _SYSTEM_PROMPTS.get(lang, _SYSTEM_PROMPTS["en"])
    prompt = REVIEW_TEMPLATE.format(
        path=file_diff.path,
        diff=file_diff.diff_text[:8000],  # cap to avoid token overflow
    )

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            ),
        )
        return ReviewResult(path=file_diff.path, review=response.text)
    except Exception as exc:  # noqa: BLE001
        return ReviewResult(path=file_diff.path, review="", error=str(exc))


def review_all(file_diffs: list, lang: str = "en") -> list[ReviewResult]:
    """Review multiple files in parallel while preserving input order."""
    client = _get_client()
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(review_file, fd, client, lang) for fd in file_diffs]
    return [f.result() for f in futures]
