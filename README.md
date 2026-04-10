# git-ai-review (`gar`)

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Model](https://img.shields.io/badge/model-gemini--2.5--flash--lite-orange)

A CLI tool that reads your `git diff` and delivers AI-powered code reviews via the Gemini API.

---

## Features

- Automatic `git diff` capture — unstaged, staged, or a specific commit
- Per-file reviews structured into **Bugs**, **Performance**, **Security**, **Suggestions**, and **Summary** sections
- Parallel Gemini API calls (up to 3 files at once) for fast turnaround
- Rich terminal output with panels and spinners
- Export reviews to a Markdown file with `--output md`
- First-commit safe (`git show` instead of `git diff HEAD^`)
- Binary file detection (skips gracefully with a note)

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/spark142857142857/git-ai-review.git
cd git-ai-review

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install in editable mode (includes dev dependencies)
pip install -e ".[dev]"
```

---

## Environment Setup

Copy the example env file and add your API key:

```bash
cp .env.example .env
```

Open `.env` and set:

```
GEMINI_API_KEY=your_api_key_here
```

Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

---

## Usage

```
gar review [OPTIONS]

Options:
  -s, --staged                  Review only staged changes (git diff --staged)
  -c, --commit TEXT             Review a specific commit hash (e.g. abc1234)
  -o, --output [terminal|md]    Output format — terminal (default) or md
  -f, --output-file PATH        Markdown output path (used with --output md)
  -r, --repo PATH               Path to the git repository (default: cwd)
  -V, --version                 Show version and exit
  --help                        Show this message and exit
```

### Examples

```bash
# Review current working-tree changes (git diff HEAD)
gar review

# Review only staged changes
gar review --staged

# Review a specific commit
gar review --commit abc1234

# Save the review to a Markdown file (auto-named with timestamp)
gar review --output md

# Save to a specific path
gar review --output md --output-file reviews/sprint42.md

# Review a repository in another directory
gar review --repo ../other-project
```

---

## Development

```bash
# Run the full test suite
pytest

# Run with verbose output
pytest -v

# Run a specific test module
pytest tests/test_git_utils.py -v
```

---

## Contributing

1. Fork the repository and create a feature branch.
2. Make your changes and add tests where appropriate.
3. Ensure `pytest` passes with no failures.
4. Open a pull request with a clear description of the change.

Please keep pull requests focused — one concern per PR.
