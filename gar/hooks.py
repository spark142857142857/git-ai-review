"""Pre-commit hook installation and removal."""

from __future__ import annotations

import stat
from pathlib import Path

# Marker line so gar can identify its own hook without touching foreign hooks.
_MARKER = "# managed by git-ai-review"

_HOOK_SCRIPT = """\
#!/bin/sh
# managed by git-ai-review
gar review --staged
"""


def _hook_path(repo_path: Path | None) -> Path:
    root = repo_path or Path.cwd()
    return root / ".git" / "hooks" / "pre-commit"


def hook_exists(repo_path: Path | None = None) -> bool:
    """Return True if any pre-commit hook file already exists."""
    return _hook_path(repo_path).exists()


def is_gar_hook(repo_path: Path | None = None) -> bool:
    """Return True if the existing hook was installed by git-ai-review."""
    path = _hook_path(repo_path)
    if not path.exists():
        return False
    return _MARKER in path.read_text(encoding="utf-8")


def install_hook(repo_path: Path | None = None) -> Path:
    """Write the pre-commit hook and make it executable.

    Raises FileNotFoundError if .git/hooks does not exist.
    """
    path = _hook_path(repo_path)
    if not path.parent.exists():
        raise FileNotFoundError(
            f".git/hooks directory not found at '{path.parent}'. "
            "Make sure you are inside a git repository."
        )

    path.write_text(_HOOK_SCRIPT, encoding="utf-8")
    # chmod +x (no-op on Windows, required on Unix)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def uninstall_hook(repo_path: Path | None = None) -> Path:
    """Remove the pre-commit hook installed by git-ai-review.

    Raises FileNotFoundError if no hook exists.
    Raises PermissionError if the hook was not installed by git-ai-review.
    """
    path = _hook_path(repo_path)

    if not path.exists():
        raise FileNotFoundError("No pre-commit hook found.")

    if _MARKER not in path.read_text(encoding="utf-8"):
        raise PermissionError(
            "The existing pre-commit hook was not installed by git-ai-review. "
            "Remove it manually to avoid accidental data loss."
        )

    path.unlink()
    return path
