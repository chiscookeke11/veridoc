"""
OCRService - extract(path) -> raw text, powered by QVAC OCR.

Same public contract as before: Workflow and everything downstream only depend
on raw text coming out of extract(). PDFs are still rasterized page-by-page
first (pdf2image + poppler), then each page image goes through QVAC OCR.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from PIL import Image

from app.services.qvac_runtime import get_runtime

_NATIVE = {".png", ".jpg", ".jpeg", ".bmp"}  # formats shown in the QVAC OCR docs


class OCRService:
    def __init__(self, lang: str = "eng"):
        # kept for API compatibility; the QVAC OCR model is configured in
        # qvac_runtime.OCR_CONFIG (English / Latin script).
        self.lang = lang

    def extract(self, path: str) -> str:
        """Return raw OCR text for a single document (image or PDF)."""
        suffix = Path(path).suffix.lower()
        if suffix == ".pdf":
            return self._extract_pdf(path)
        return self._extract_image(path)

    def _extract_image(self, path: str) -> str:
        if Path(path).suffix.lower() in _NATIVE:
            return get_runtime().ocr_text(path).strip()

        # TIFF / WebP / etc.: convert to a temporary PNG first
        with tempfile.TemporaryDirectory() as tmp:
            png = Path(tmp) / "page.png"
            with Image.open(path) as img:
                img.convert("RGB").save(png)
            return get_runtime().ocr_text(str(png)).strip()

    def _extract_pdf(self, path: str) -> str:
        # Local import - pdf2image needs poppler, only pull it in when needed.
        from pdf2image import convert_from_path

        pages = convert_from_path(path, dpi=200)
        texts: list[str] = []
        with tempfile.TemporaryDirectory() as tmp:
            for i, page in enumerate(pages):
                png = Path(tmp) / f"page_{i}.png"
                page.convert("RGB").save(png)
                texts.append(get_runtime().ocr_text(str(png)))
        return "\n\n".join(t.strip() for t in texts if t.strip())