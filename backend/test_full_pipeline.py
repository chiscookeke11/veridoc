"""
End-to-end test: OCR -> extract -> registry lookup -> verify -> memo -> persist.
Generates synthetic document images (no real scanned docs needed yet) so
Tesseract has to actually do OCR work, not just read clean input text.
"""

import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.db import init_db, get_session
from app.models import Registry
from app.pipeline import process_case

TEST_DIR = Path("test_docs")
TEST_DIR.mkdir(exist_ok=True)


def _font(size=28):
    # Falls back to PIL's tiny default bitmap font if no system font is
    # found — that font is hard for Tesseract to read reliably, so this
    # tries a real system font first.
    for candidate in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_doc(filename: str, lines: list[str]) -> str:
    img = Image.new("RGB", (900, 500), color="white")
    draw = ImageDraw.Draw(img)
    font = _font()
    y = 30
    for line in lines:
        draw.text((30, y), line, fill="black", font=font)
        y += 50
    path = TEST_DIR / filename
    img.save(path)
    return str(path)


def main():
    init_db()

    # Seed a matching registry entry so this case comes back "found, valid"
    with get_session() as session:
        if session.get(Registry, "ABC-2024-001") is None:
            session.add(
                Registry(
                    cert_no="ABC-2024-001",
                    candidate_name="Musa Ibrahim",
                    institution="University of Nigeria",
                    status="valid",
                )
            )

    paths = {
        "application_form": make_doc(
            "application_form.png",
            [
                "APPLICATION FORM",
                "Name: Musa Ibrahim",
                "Date of Birth: 1997-03-15",
                "Institution: University of Nigeria",
            ],
        ),
        "certificate": make_doc(
            "certificate.png",
            [
                "CERTIFICATE",
                "Name: Musa Ibrahim",
                "Certificate No: ABC-2024-001",
                "Institution: University of Nigeria",
                "Issue Date: 2020-06-01",
            ],
        ),
        "id_document": make_doc(
            "id_document.png",
            [
                "NATIONAL ID",
                "Name: Musa Ibrahim",
                "ID Number: NIN-778899",
                "Expiry Date: 2030-01-01",
            ],
        ),
    }

    print("Running process_case()...")
    start = time.time()
    result = process_case(paths, officer_id="officer-demo-1")
    elapsed = time.time() - start

    print(f"\n--- process_case took {elapsed:.1f}s total ---\n")
    print("Fields:  ", result.fields)
    print("Registry:", result.registry)
    print("Flags:   ", result.flags)
    print("Risk:    ", result.overall_risk)
    print("Memo:    ", result.memo)


if __name__ == "__main__":
    main()
