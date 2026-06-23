"""MarkItDown + OpenAI vision OCR conversion."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

from markitdown import MarkItDown
from openai import OpenAI
from rich.console import Console

DEFAULT_MODEL = "gpt-5.4-mini"


def require_api_key() -> str:
    import os

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Export your OpenAI API key before running pdf2md-ai."
        )
    return api_key


def install_ocr_progress_hooks(
    model: str,
    on_start: Callable[[int], None],
    on_finish: Callable[[int, float, int, str | None], None],
) -> None:
    from markitdown_ocr._ocr_service import LLMVisionOCRService

    if getattr(install_ocr_progress_hooks, "_patched", False):
        return

    original = LLMVisionOCRService.extract_text
    counter = {"n": 0}

    def extract_text(self, image_stream, prompt=None, stream_info=None, **kwargs):
        counter["n"] += 1
        call_id = counter["n"]
        on_start(call_id)
        started = time.time()
        result = original(self, image_stream, prompt, stream_info, **kwargs)
        on_finish(call_id, time.time() - started, len(result.text or ""), result.error)
        return result

    LLMVisionOCRService.extract_text = extract_text
    install_ocr_progress_hooks._patched = True


def convert_pdf(
    pdf_path: Path,
    *,
    model: str = DEFAULT_MODEL,
    text_only: bool = False,
    console: Console | None = None,
) -> str:
    log = console or Console(stderr=True)

    if text_only:
        md = MarkItDown()
        result = md.convert(str(pdf_path))
        return result.text_content or ""

    api_key = require_api_key()
    client = OpenAI(api_key=api_key, timeout=120.0)

    def on_start(call_id: int) -> None:
        log.print(f"[cyan]→ OCR call #{call_id} started[/cyan]")

    def on_finish(
        call_id: int, elapsed: float, chars: int, error: str | None
    ) -> None:
        err = f" error={error}" if error else ""
        log.print(
            f"[green]✓ OCR call #{call_id} finished in {elapsed:.1f}s "
            f"({chars} chars){err}[/green]"
        )

    install_ocr_progress_hooks(model, on_start, on_finish)
    md = MarkItDown(enable_plugins=True, llm_client=client, llm_model=model)
    result = md.convert(str(pdf_path))
    return result.text_content or ""
