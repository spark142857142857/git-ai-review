"""Typer CLI entry point."""

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
    help="A CLI tool that reads git diff and delivers AI-powered code reviews via Gemini.",
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
        typer.Option("--staged", "-s", help="Review only staged changes (git diff --staged)"),
    ] = False,
    commit: Annotated[
        Optional[str],
        typer.Option("--commit", "-c", help="Review a specific commit hash (e.g. abc1234)"),
    ] = None,
    output: Annotated[
        OutputFormat,
        typer.Option("--output", "-o", help="Output format: terminal (default) or md (save to file)"),
    ] = OutputFormat.terminal,
    output_file: Annotated[
        Optional[Path],
        typer.Option("--output-file", "-f", help="Markdown output path (used with --output md)"),
    ] = None,
    repo: Annotated[
        Optional[Path],
        typer.Option("--repo", "-r", help="Path to the git repository (default: cwd)"),
    ] = None,
    lang: Annotated[
        str,
        typer.Option("--lang", "-l", help="Review language: en (default, English) or ko (Korean)"),
    ] = "en",
) -> None:
    """Read git diff and run Gemini AI code review."""
    # 1. run git diff
    try:
        raw = run_git_diff(staged=staged, commit=commit, repo_path=repo)
    except RuntimeError as exc:
        err_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(1) from exc

    if not raw.strip():
        console.print("[yellow]No changed files found.[/yellow]")
        raise typer.Exit()

    # 2. parse diff
    file_diffs = parse_diff(raw)
    if not file_diffs:
        console.print("[yellow]No parseable diff found.[/yellow]")
        raise typer.Exit()

    # file limit
    if len(file_diffs) > MAX_FILES:
        console.print(
            f"[yellow]⚠ {len(file_diffs)} files detected. "
            f"Reviewing only the first {MAX_FILES}.[/yellow]"
        )
        file_diffs = file_diffs[:MAX_FILES]

    console.print(f"[dim]Reviewing {len(file_diffs)} file(s)[/dim]")

    # 3. Gemini review (spinner)
    if len(file_diffs) == 1:
        spinner_label = file_diffs[0].path
    else:
        spinner_label = f"{len(file_diffs)} files"

    try:
        with console.status(f"[bold cyan]🔍 Reviewing with Gemini... ({spinner_label})[/bold cyan]"):
            results = review_all(file_diffs, lang=lang)
    except EnvironmentError as exc:
        err_console.print(f"[bold red]Configuration error:[/bold red] {exc}")
        raise typer.Exit(1) from exc

    # 4. output
    if output == OutputFormat.md:
        path = save_markdown(results, output_file)
        console.print(f"[green]Markdown saved:[/green] {path}")
    else:
        print_all_reviews(results)
