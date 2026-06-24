# pdf2md-ai

An [agent skill](skill/pdf2md-ai/SKILL.md) and CLI for converting PDFs to Markdown with [**MarkItDown**](https://github.com/microsoft/markitdown). Use the CLI directly, or install the skill so agents in Cursor, Claude Code, Codex, and other tools can extract PDF pages on demand.

The **`pdf2md-ai`** command handles the work: MarkItDown for text, plus **OpenAI vision OCR** for embedded images (screenshots, code blocks, scanned regions). Pages are sliced locally; cloud OCR runs only when needed.

## Requirements

- Python 3.11+
- [pipx](https://pipx.pypa.io/) (CLI install)
- `OPENAI_API_KEY` environment variable
- Node.js with `npx` (skill install only)

## Install

### CLI

```bash
pipx install git+https://github.com/illescasDaniel/pdf2md-ai-skill.git --force
```

### Agent skill

Installs the skill **globally** for Cursor, Claude Code, Codex, and other agents supported by [agent-install](https://github.com/millionco/agent-install). The skill invokes the CLI, so install the CLI first.

All supported agents:

```bash
npx agent-install@latest skill add illescasDaniel/pdf2md-ai-skill/skill/pdf2md-ai -g -y -a '*'
```

Specific agents only:

```bash
npx agent-install@latest skill add illescasDaniel/pdf2md-ai-skill/skill/pdf2md-ai -g -y -a cursor
npx agent-install@latest skill add illescasDaniel/pdf2md-ai-skill/skill/pdf2md-ai -g -y -a cursor -a claude-code
```

After install, set your API key:

```bash
export OPENAI_API_KEY='your-key-here'
```

Upgrade — re-run the same install command(s).

### Uninstall

CLI:

```bash
pipx uninstall pdf2md-ai
```

Agent skill (all agents where it was installed):

```bash
npx agent-install@latest skill remove pdf2md-ai -g -y -a '*'
```

Specific agents only:

```bash
npx agent-install@latest skill remove pdf2md-ai -g -y -a cursor
```

List what is installed:

```bash
pipx list
npx agent-install@latest skill list
```


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

Install from your local clone (CLI and skill) while iterating:

```bash
pipx install . --force
npx agent-install@latest skill add ./skill/pdf2md-ai -g -y -a cursor
```

If `pipx install` fails to upgrade an existing venv, try `UV_VENV_CLEAR=1 pipx install . --force`.

Steps: Ruff (lint + format, tabs) → ShellCheck + shfmt → basedpyright → smoke (CLI `--help` and agent-install skill list). CI runs the same `./scripts/quality/checks.sh` on push and pull requests.

## How it works

1. Slice selected PDF pages with `pypdf`
2. Extract copyable text with MarkItDown
3. OCR embedded images via `markitdown-ocr` + OpenAI vision (`OPENAI_API_KEY`)
4. Write combined markdown output

## License

MIT
