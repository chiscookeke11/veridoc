"""
OCRService — extract(path) -> raw text.

Default engine: pytesseract (offline, no API calls — required for the
"no cloud APIs" constraint). PDFs are rasterized page-by-page first.

Swap point: if you later move to a different OCR engine, only this file
changes — Workflow and everything downstream only depend on raw text in.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytesseract
from PIL import Image

# Packaged/installed version points this at a bundled portable Tesseract
# via launcher.pyw; unset in normal dev, where Tesseract is just on PATH.
if os.getenv("CIVICVERIFY_TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.environ["CIVICVERIFY_TESSERACT_CMD"]


class OCRService:
    def __init__(self, lang: str = "eng"):
        self.lang = lang

    def extract(self, path: str) -> str:
        """Return raw OCR text for a single document (image or PDF)."""
        suffix = Path(path).suffix.lower()

        if suffix == ".pdf":
            return self._extract_pdf(path)
        return self._extract_image(path)

    def _extract_image(self, path: str) -> str:
        with Image.open(path) as img:
            return pytesseract.image_to_string(img, lang=self.lang).strip()

    def _extract_pdf(self, path: str) -> str:
        # Local import — pdf2image needs poppler, only pull it in when needed.
        from pdf2image import convert_from_path

        pages = convert_from_path(path, dpi=200)
        texts = []
        for page in pages:
            texts.append(pytesseract.image_to_string(page, lang=self.lang))
        return "\n\n".join(t.strip() for t in texts if t.strip())
