"""Typer CLI 진입점."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from gar import __version__
from gar.formatter import print_all_reviews, save_markdown
from gar.git_utils import parse_diff, run_git_diff
from gar.reviewer import review_all

MAX_FILES = 20

app = typer.Typer(
    name="gar",
    help="git diff를 자동으로 읽어서 Gemini AI로 코드 리뷰를 출력하는 CLI 도구.",
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)


class OutputFormat(str, Enum):
    terminal = "terminal"
    md = "md"


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"gar {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-V", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    pass


@app.command()
def review(
    staged: Annotated[
        bool,
        typer.Option("--staged", "-s", help="staged 변경사항만 리뷰 (git diff --staged)"),
    ] = False,
    commit: Annotated[
        Optional[str],
        typer.Option("--commit", "-c", help="특정 커밋 해시 리뷰 (예: abc1234)"),
    ] = None,
    output: Annotated[
        OutputFormat,
        typer.Option("--output", "-o", help="출력 형식: terminal(기본) 또는 md(파일 저장)"),
    ] = OutputFormat.terminal,
    output_file: Annotated[
        Optional[Path],
        typer.Option("--output-file", "-f", help="마크다운 저장 경로 (--output md 시 사용)"),
    ] = None,
    repo: Annotated[
        Optional[Path],
        typer.Option("--repo", "-r", help="git 리포지터리 경로 (기본: 현재 디렉토리)"),
    ] = None,
) -> None:
    """git diff를 읽어서 Gemini AI로 코드 리뷰를 실행한다."""
    # 1. git diff 실행
    try:
        raw = run_git_diff(staged=staged, commit=commit, repo_path=repo)
    except RuntimeError as exc:
        err_console.print(f"[bold red]오류:[/bold red] {exc}")
        raise typer.Exit(1) from exc

    if not raw.strip():
        console.print("[yellow]변경된 파일이 없습니다.[/yellow]")
        raise typer.Exit()

    # 2. diff 파싱
    file_diffs = parse_diff(raw)
    if not file_diffs:
        console.print("[yellow]파싱 가능한 diff가 없습니다.[/yellow]")
        raise typer.Exit()

    # 파일 수 제한
    if len(file_diffs) > MAX_FILES:
        console.print(
            f"[yellow]⚠ 파일이 {len(file_diffs)}개입니다. "
            f"처음 {MAX_FILES}개만 리뷰합니다.[/yellow]"
        )
        file_diffs = file_diffs[:MAX_FILES]

    console.print(f"[dim]리뷰 대상: {len(file_diffs)}개 파일[/dim]")

    # 3. Gemini 리뷰 (스피너)
    if len(file_diffs) == 1:
        spinner_label = file_diffs[0].path
    else:
        spinner_label = f"{len(file_diffs)}개 파일"

    try:
        with console.status(f"[bold cyan]🔍 Gemini 리뷰 중... ({spinner_label})[/bold cyan]"):
            results = review_all(file_diffs)
    except EnvironmentError as exc:
        err_console.print(f"[bold red]환경 설정 오류:[/bold red] {exc}")
        raise typer.Exit(1) from exc

    # 4. 출력
    if output == OutputFormat.md:
        path = save_markdown(results, output_file)
        console.print(f"[green]마크다운 저장 완료:[/green] {path}")
    else:
        print_all_reviews(results)
