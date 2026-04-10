"""git diff 실행 및 파싱 유틸리티."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FileDiff:
    path: str
    old_path: str | None  # 파일 rename 시 원래 경로
    hunks: list[str] = field(default_factory=list)

    @property
    def diff_text(self) -> str:
        return "\n".join(self.hunks)

    def __bool__(self) -> bool:
        return bool(self.hunks)


def run_git_diff(
    *,
    staged: bool = False,
    commit: str | None = None,
    repo_path: Path | None = None,
) -> str:
    """git diff를 실행하고 raw 출력을 반환한다.

    우선순위:
      1. commit 지정 → git show --format= <commit>  (첫 커밋도 동작)
      2. staged=True  → git diff --staged
      3. 기본         → git diff HEAD
    """
    cwd = str(repo_path) if repo_path else None

    if commit:
        cmd = ["git", "show", "--format=", commit]
    elif staged:
        cmd = ["git", "diff", "--staged"]
    else:
        cmd = ["git", "diff", "HEAD"]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"git diff 실패 (exit {result.returncode}):\n{result.stderr.strip()}"
        )

    return result.stdout


def parse_diff(raw_diff: str) -> list[FileDiff]:
    """unified diff 텍스트를 FileDiff 목록으로 파싱한다."""
    files: list[FileDiff] = []
    current: FileDiff | None = None
    current_hunk: list[str] = []

    # diff --git a/foo b/bar
    file_header_re = re.compile(r"^diff --git a/(.+?) b/(.+)$")
    # --- a/old  or  +++ b/new
    old_path_re = re.compile(r"^--- a/(.+)$")
    hunk_start_re = re.compile(r"^@@")
    binary_re = re.compile(r"^Binary files .+ differ$")

    def _flush_hunk() -> None:
        if current is not None and current_hunk:
            current.hunks.append("\n".join(current_hunk))
            current_hunk.clear()

    for line in raw_diff.splitlines():
        m = file_header_re.match(line)
        if m:
            _flush_hunk()
            old_rel, new_rel = m.group(1), m.group(2)
            old_path = old_rel if old_rel != new_rel else None
            current = FileDiff(path=new_rel, old_path=old_path)
            files.append(current)
            continue

        if current is None:
            continue

        if binary_re.match(line):
            current.hunks.append("[바이너리 파일 변경]")
            continue

        if hunk_start_re.match(line):
            _flush_hunk()
            current_hunk.append(line)
            continue

        # --- / +++ 헤더는 hunk에 포함하지 않음
        if old_path_re.match(line) or line.startswith("+++ b/"):
            continue

        if current_hunk or line.startswith(("+", "-", " ")):
            current_hunk.append(line)

    _flush_hunk()

    return [f for f in files if f]
