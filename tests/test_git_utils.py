"""git_utils 모듈 단위 테스트."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from gar.git_utils import FileDiff, parse_diff, run_git_diff

# ---------------------------------------------------------------------------
# parse_diff
# ---------------------------------------------------------------------------

SAMPLE_DIFF = """\
diff --git a/foo/bar.py b/foo/bar.py
index 1234567..abcdefg 100644
--- a/foo/bar.py
+++ b/foo/bar.py
@@ -1,5 +1,6 @@
 def hello():
-    pass
+    print("hello")
+    return True

diff --git a/README.md b/README.md
index 0000001..0000002 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,3 @@
 # Title
+New line added.
"""


def test_parse_diff_returns_correct_file_count():
    result = parse_diff(SAMPLE_DIFF)
    assert len(result) == 2


def test_parse_diff_file_paths():
    result = parse_diff(SAMPLE_DIFF)
    paths = [f.path for f in result]
    assert "foo/bar.py" in paths
    assert "README.md" in paths


def test_parse_diff_hunks_not_empty():
    result = parse_diff(SAMPLE_DIFF)
    for fd in result:
        assert fd.hunks, f"{fd.path} 에 hunk가 없음"


def test_parse_diff_empty_string():
    result = parse_diff("")
    assert result == []


def test_parse_diff_no_changes():
    # hunk 없이 헤더만 있는 경우 → FileDiff가 생성되지 않아야 함
    diff = "diff --git a/x.py b/x.py\nindex aaa..bbb 100644\n"
    result = parse_diff(diff)
    assert result == []


def test_parse_diff_binary_file():
    diff = (
        "diff --git a/image.png b/image.png\n"
        "index 1234567..abcdefg 100644\n"
        "Binary files a/image.png and b/image.png differ\n"
    )
    result = parse_diff(diff)
    assert len(result) == 1
    assert result[0].path == "image.png"
    assert result[0].hunks == ["[바이너리 파일 변경]"]


def test_parse_diff_binary_new_file():
    diff = (
        "diff --git a/image.png b/image.png\n"
        "new file mode 100644\n"
        "Binary files /dev/null and b/image.png differ\n"
    )
    result = parse_diff(diff)
    assert len(result) == 1
    assert result[0].hunks == ["[바이너리 파일 변경]"]


def test_file_diff_bool_false_when_no_hunks():
    fd = FileDiff(path="x.py", old_path=None)
    assert not fd


def test_file_diff_bool_true_when_has_hunks():
    fd = FileDiff(path="x.py", old_path=None, hunks=["@@ -1 +1 @@\n+line"])
    assert fd


# ---------------------------------------------------------------------------
# run_git_diff
# ---------------------------------------------------------------------------

def test_run_git_diff_calls_correct_command_default():
    mock_result = MagicMock(returncode=0, stdout="diff output", stderr="")
    with patch("subprocess.run", return_value=mock_result) as mock_run:
        output = run_git_diff()
        cmd = mock_run.call_args[0][0]
        assert cmd == ["git", "diff", "HEAD"]
    assert output == "diff output"


def test_run_git_diff_staged():
    mock_result = MagicMock(returncode=0, stdout="staged diff", stderr="")
    with patch("subprocess.run", return_value=mock_result) as mock_run:
        run_git_diff(staged=True)
        cmd = mock_run.call_args[0][0]
        assert "--staged" in cmd


def test_run_git_diff_commit():
    mock_result = MagicMock(returncode=0, stdout="commit diff", stderr="")
    with patch("subprocess.run", return_value=mock_result) as mock_run:
        run_git_diff(commit="abc1234")
        cmd = mock_run.call_args[0][0]
        assert cmd == ["git", "show", "--format=", "abc1234"]


def test_run_git_diff_raises_on_nonzero_exit():
    mock_result = MagicMock(returncode=128, stdout="", stderr="not a git repo")
    with patch("subprocess.run", return_value=mock_result):
        with pytest.raises(RuntimeError, match="git diff 실패"):
            run_git_diff()
