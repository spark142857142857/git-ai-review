"""reviewer 모듈 단위 테스트 (Gemini API mock)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from gar.git_utils import FileDiff
from gar.reviewer import ReviewResult, review_all, review_file


def _make_file_diff(path: str = "foo.py", hunk: str = "@@ -1 +1 @@\n+line") -> FileDiff:
    return FileDiff(path=path, old_path=None, hunks=[hunk])


def _mock_client(text: str = "리뷰 내용") -> MagicMock:
    response = MagicMock()
    response.text = text
    client = MagicMock()
    client.models.generate_content.return_value = response
    return client


# ---------------------------------------------------------------------------
# review_file
# ---------------------------------------------------------------------------

def test_review_file_returns_review_result():
    fd = _make_file_diff()
    client = _mock_client("좋은 코드입니다.")
    result = review_file(fd, client=client)
    assert isinstance(result, ReviewResult)
    assert result.path == "foo.py"
    assert result.review == "좋은 코드입니다."
    assert result.ok


def test_review_file_passes_path_to_prompt():
    fd = _make_file_diff(path="src/main.py")
    client = _mock_client()
    review_file(fd, client=client)
    call_kwargs = client.models.generate_content.call_args
    contents = call_kwargs.kwargs.get("contents") or call_kwargs[1].get("contents") or call_kwargs[0][1]
    assert "src/main.py" in contents


def test_review_file_captures_api_error():
    fd = _make_file_diff()
    client = MagicMock()
    client.models.generate_content.side_effect = Exception("API timeout")
    result = review_file(fd, client=client)
    assert not result.ok
    assert "API timeout" in result.error


# ---------------------------------------------------------------------------
# review_all
# ---------------------------------------------------------------------------

def test_review_all_returns_one_result_per_file():
    fds = [_make_file_diff(f"file{i}.py") for i in range(3)]
    with patch("gar.reviewer._get_client", return_value=_mock_client()):
        results = review_all(fds)
    assert len(results) == 3


def test_review_all_preserves_file_order():
    fds = [_make_file_diff(f"file{i}.py") for i in range(3)]
    with patch("gar.reviewer._get_client", return_value=_mock_client()):
        results = review_all(fds)
    for i, result in enumerate(results):
        assert result.path == f"file{i}.py"


# ---------------------------------------------------------------------------
# _get_client (환경변수)
# ---------------------------------------------------------------------------

def test_get_client_raises_without_api_key():
    from gar.reviewer import _get_client
    import os
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("GEMINI_API_KEY", None)
        with pytest.raises(EnvironmentError, match="GEMINI_API_KEY"):
            _get_client()
