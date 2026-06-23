"""Parse page range specs and slice PDFs."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter


def parse_page_ranges(spec: str | None, total_pages: int) -> list[int]:
	"""Parse ranges like '3', '1-3', '1,3,5-7', or 'all'."""
	if not spec or spec.strip().lower() == "all":
		return list(range(1, total_pages + 1))

	pages: set[int] = set()
	for part in spec.split(","):
		part = part.strip()
		if not part:
			continue
		if "-" in part:
			start_str, end_str = part.split("-", 1)
			start, end = int(start_str), int(end_str)
			if start > end:
				start, end = end, start
			pages.update(range(start, end + 1))
		else:
			pages.add(int(part))

	selected = sorted(p for p in pages if 1 <= p <= total_pages)
	if not selected:
		raise ValueError(f"No valid pages in {spec!r} (PDF has {total_pages} pages)")
	invalid = sorted(p for p in pages if p < 1 or p > total_pages)
	if invalid:
		raise ValueError(f"Page(s) out of range: {invalid} (PDF has {total_pages} pages)")
	return selected


def pdf_page_count(pdf_path: Path) -> int:
	return len(PdfReader(str(pdf_path)).pages)


def extract_pages(src: Path, page_numbers: list[int], dst: Path) -> None:
	reader = PdfReader(str(src))
	writer = PdfWriter()
	for page_num in page_numbers:
		writer.add_page(reader.pages[page_num - 1])
	dst.parent.mkdir(parents=True, exist_ok=True)
	with dst.open("wb") as handle:
		writer.write(handle)


def page_range_label(page_numbers: list[int]) -> str:
	if len(page_numbers) == 1:
		return f"page{page_numbers[0]}"
	if page_numbers == list(range(page_numbers[0], page_numbers[-1] + 1)):
		return f"pages{page_numbers[0]}-{page_numbers[-1]}"
	return "pages_" + "_".join(str(p) for p in page_numbers)


def default_output_path(input_pdf: Path, output: Path | None, page_numbers: list[int]) -> Path:
	suffix = page_range_label(page_numbers)
	stem = input_pdf.stem
	if output is None:
		return input_pdf.with_name(f"{stem}_{suffix}.md")
	if output.is_dir() or str(output).endswith("/"):
		return Path(output) / f"{stem}_{suffix}.md"
	return output
