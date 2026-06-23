"""CLI for pdf2md-ai."""

from __future__ import annotations

import argparse
import tempfile
import time
from pathlib import Path

import pdfplumber
from rich.console import Console
from rich.progress import (
	BarColumn,
	Progress,
	SpinnerColumn,
	TaskProgressColumn,
	TextColumn,
	TimeElapsedColumn,
)

from pdf2md_ai.converter import DEFAULT_MODEL, convert_pdf, require_api_key
from pdf2md_ai.pages import (
	default_output_path,
	extract_pages,
	page_range_label,
	parse_page_ranges,
	pdf_page_count,
)


console = Console(stderr=True)


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog="pdf2md-ai",
		description=(
			"Convert PDF pages to Markdown using MarkItDown and OpenAI vision OCR for embedded images and scans."
		),
	)
	parser.add_argument(
		"input_pdf",
		type=Path,
		help="Path to the source PDF",
	)
	parser.add_argument(
		"-o",
		"--output",
		type=Path,
		default=None,
		help="Output markdown file or directory (default: next to input PDF)",
	)
	parser.add_argument(
		"-p",
		"--pages",
		default="all",
		help='Page selection: "all", "3", "1-3", or "1,3,5-7" (default: all)',
	)
	parser.add_argument(
		"-m",
		"--model",
		default=DEFAULT_MODEL,
		help=f"OpenAI vision model (default: {DEFAULT_MODEL})",
	)
	parser.add_argument(
		"--text-only",
		action="store_true",
		help="Skip OCR plugin; extract copyable PDF text only",
	)
	return parser


def page_stats(pdf_path: Path) -> tuple[int, int]:
	with pdfplumber.open(pdf_path) as doc:
		text_len = sum(len(page.extract_text() or "") for page in doc.pages)
		image_count = sum(len(getattr(page, "images", []) or []) for page in doc.pages)
	return text_len, image_count


def main(argv: list[str] | None = None) -> int:
	args = build_parser().parse_args(argv)
	input_pdf: Path = args.input_pdf.expanduser().resolve()

	if not input_pdf.is_file():
		console.print(f"[red]Missing PDF:[/red] {input_pdf}")
		return 1

	if not args.text_only:
		try:
			require_api_key()
		except RuntimeError as exc:
			console.print(f"[red]{exc}[/red]")
			return 1

	total_pages = pdf_page_count(input_pdf)
	try:
		page_numbers = parse_page_ranges(args.pages, total_pages)
	except ValueError as exc:
		console.print(f"[red]{exc}[/red]")
		return 1

	output_path = default_output_path(
		input_pdf,
		args.output.expanduser().resolve() if args.output else None,
		page_numbers,
	)
	output_path.parent.mkdir(parents=True, exist_ok=True)

	console.rule("[bold]pdf2md-ai")
	console.print(f"Input:  {input_pdf}")
	console.print(f"Pages:  {page_range_label(page_numbers)} ({len(page_numbers)} page(s))")
	console.print(f"Model:  {args.model}")
	console.print(f"Mode:   {'text-only' if args.text_only else 'OCR'}")
	console.print(f"Output: {output_path}")

	progress = Progress(
		SpinnerColumn(),
		TextColumn("[progress.description]{task.description}"),
		BarColumn(),
		TaskProgressColumn(),
		TimeElapsedColumn(),
		console=console,
		transient=False,
	)

	with progress:
		task = progress.add_task("[cyan]Slicing PDF", total=100)
		with tempfile.TemporaryDirectory(prefix="pdf2md-ai-") as tmpdir:
			slice_pdf = Path(tmpdir) / f"{input_pdf.stem}_{page_range_label(page_numbers)}.pdf"
			extract_pages(input_pdf, page_numbers, slice_pdf)
			progress.update(task, completed=100)

			text_len, image_count = page_stats(slice_pdf)
			console.print(f"[green]Slice ready:[/green] {text_len} text chars, {image_count} embedded image(s)")
			if not args.text_only and image_count:
				console.print(f"[yellow]Expect up to {image_count} OpenAI vision OCR call(s).[/yellow]")

			task = progress.add_task("[cyan]Converting to Markdown", total=100)
			started = time.time()
			markdown = convert_pdf(
				slice_pdf,
				model=args.model,
				text_only=args.text_only,
				console=console,
			)
			progress.update(
				task,
				completed=100,
				description=f"[green]Converted in {time.time() - started:.1f}s",
			)

	output_path.write_text(markdown, encoding="utf-8")
	console.print(f"[green]Done:[/green] {len(markdown):,} chars → {output_path} (total {time.time() - started:.1f}s)")

	console.rule("Preview (first 40 lines)")
	preview = markdown.splitlines()[:40]
	console.print("\n".join(preview) if preview else "[yellow](empty output)[/yellow]")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
