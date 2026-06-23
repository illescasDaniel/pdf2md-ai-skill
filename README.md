# pdf2md-ai

Convert PDF pages to Markdown with **MarkItDown** and **OpenAI vision OCR** for embedded images (screenshots, code blocks, scanned regions).

Fast, local slicing; cloud OCR only when needed.

## Requirements

- Python 3.11+
- [pipx](https://pipx.pypa.io/)
- `OPENAI_API_KEY` environment variable

## Install

The install script sets up both the global `pdf2md-ai` CLI (via pipx) and the Cursor agent skill.

Clone the repo, then run the install script from the repo root:

```bash
git clone <repo-url>
cd pdf2md-ai-skill
bash skill/pdf2md-ai/scripts/install.sh
```

After install, set your API key:

```bash
export OPENAI_API_KEY='your-key-here'
```

Upgrade after pulling changes — re-run the install script (handles first install and upgrade; refreshes the pipx CLI and skill copy).

### Manual install

If you prefer not to use the script:

```bash
# CLI only (from repo root)
pipx install .

# Cursor skill only (from repo root)
mkdir -p ~/.cursor/skills
cp -r skill/pdf2md-ai ~/.cursor/skills/
```

## Usage

```bash
# Single page
pdf2md-ai document.pdf -p 3 -o ./docs/output.md

# Page range
pdf2md-ai document.pdf -p 1-3 -o ./docs/

# Multiple ranges
pdf2md-ai document.pdf -p "1,3,5-7" -o ./docs/chapter.md

# All pages (default)
pdf2md-ai document.pdf -o ./docs/full.md

# Text-only (no OCR, no API calls)
pdf2md-ai document.pdf -p 3 --text-only -o ./docs/page3_text.md

# Different model
pdf2md-ai document.pdf -p 3 -m gpt-5.4-mini
```

### Arguments

| Argument | Description |
|----------|-------------|
| `input_pdf` | Source PDF path |
| `-o`, `--output` | Output `.md` file or directory |
| `-p`, `--pages` | `all`, `3`, `1-3`, or `1,3,5-7` |
| `-m`, `--model` | OpenAI vision model (default: `gpt-5.4-mini`) |
| `--text-only` | Skip OCR; extract copyable text only |

If `-o` is omitted, markdown is written next to the PDF as `{name}_pageN.md` or `{name}_pages1-3.md`.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
./scripts/quality/checks.sh --fix   # autofix locally
./scripts/quality/checks.sh         # verify clean
```

Steps: Ruff (lint + format, tabs) → ShellCheck + shfmt → basedpyright. CI runs the same `./scripts/quality/checks.sh` on push and pull requests.

## How it works

1. Slice selected PDF pages with `pypdf`
2. Extract copyable text with MarkItDown
3. OCR embedded images via `markitdown-ocr` + OpenAI vision (`OPENAI_API_KEY`)
4. Write combined markdown output

## License

MIT
