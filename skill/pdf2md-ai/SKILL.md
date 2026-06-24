---
name: pdf2md-ai
description: >-
  Convert PDF pages to Markdown with OpenAI vision OCR for embedded images and
  scans. Use when extracting text from PDFs, converting PDFs to markdown,
  OCRing PDF images, or when the user mentions pdf2md-ai, markitdown OCR, or
  PDF page extraction.
---

# pdf2md-ai

Convert PDF pages to Markdown using the `pdf2md-ai` CLI (MarkItDown + OpenAI vision OCR).

## Prerequisites

1. **`pdf2md-ai` on PATH** — verify with `command -v pdf2md-ai`
2. **`OPENAI_API_KEY`** exported in the environment (never hardcode keys in files or commands logged to git)

## When to use

- User wants PDF content as markdown for reading, search, or agent context
- PDF has **embedded images with text** (screenshots, diagrams, code blocks)
- User asks for specific **pages** or **page ranges**
- User wants a fast **text-only** pass without OCR (`--text-only`)

## Default workflow

1. Confirm `pdf2md-ai` is available (`command -v pdf2md-ai`).
2. Confirm `OPENAI_API_KEY` is set (`test -n "$OPENAI_API_KEY"`).
3. Choose pages (`-p`) and output path (`-o`).
4. Run `pdf2md-ai`.
5. Read the generated `.md` file and summarize or continue the task.

## Commands

```bash
# Single page → explicit output file
pdf2md-ai "/path/to/file.pdf" -p 3 -o "/path/to/output.md"

# Page range → output directory (auto-named .md inside)
pdf2md-ai "/path/to/file.pdf" -p 1-5 -o "/path/to/docs/"

# Multiple pages
pdf2md-ai "/path/to/file.pdf" -p "1,3,5-7" -o "/path/to/output.md"

# All pages
pdf2md-ai "/path/to/file.pdf" -o "/path/to/full.md"

# Text-only (no API calls)
pdf2md-ai "/path/to/file.pdf" -p 3 --text-only -o "/path/to/page3_text.md"
```

Default model: **`gpt-5.4-mini`**. Override with `-m` if the user requests another OpenAI vision model.

## Page syntax

| `-p` value | Meaning |
|------------|---------|
| `all` | Every page (default) |
| `3` | Page 3 only |
| `1-5` | Pages 1 through 5 |
| `1,3,5-7` | Pages 1, 3, 5, 6, 7 |

## Output naming

If `-o` is a directory (or omitted), the tool writes `{pdf_stem}_pageN.md` or `{pdf_stem}_pages1-3.md`.

## OCR behavior

- Copyable PDF text is extracted directly.
- Embedded images trigger OpenAI vision OCR calls (one call per image).
- Failed OCR calls are skipped silently by MarkItDown; check CLI logs for `OCR call #N finished` lines and verify image blocks appear as `*[Image OCR] ... [End OCR]*` in the markdown.

## Do not

- Commit or write API keys into repo files, skills, or shell history in docs
- Use local Ollama for this skill (OpenAI-only tool)
- Assume OCR ran correctly without opening the output markdown
