"""
Smoke test for the QVAC migration. Run from the backend folder:

    python test_qvac_smoke.py

Step 1 OCR a test document and show the raw bbox shape
Step 2 plain chat completion (is the LLM alive, how fast)
Step 3 field extraction on the OCR text (does the JSON come back parsed)
Step 4 memo generation

The first run downloads the models, so it needs internet once.
"""
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from app.services.llm_service import LLMService
from app.services.qvac_runtime import blocks_to_text, get_runtime

DOC = "test_docs/certificate.png"
rt = get_runtime()


def timed(label, fn):
    t0 = time.perf_counter()
    out = fn()
    print(f"\n[{label}] {time.perf_counter() - t0:.1f}s")
    return out


print("=== 1. OCR ===")
blocks = timed("ocr", lambda: rt.ocr_blocks(DOC))
print(f"{len(blocks)} blocks")
for b in blocks[:3]:
    print("  text:", repr(getattr(b, "text", None)),
          "| bbox:", getattr(b, "bbox", None),
          "| conf:", getattr(b, "confidence", None))
text = blocks_to_text(blocks)
print("--- reading-order text ---")
print(text[:600])

print("\n=== 2. Chat ===")
print(timed("chat", lambda: rt.chat("You are concise.", "Say hello in one sentence.",
                                    max_tokens=40, temperature=0.2)))

llm = LLMService()
print("\n=== 3. Field extraction ===")
fields = timed("extract", lambda: llm.extract_fields(text))
print(fields)

print("\n=== 4. Memo ===")
print(timed("memo", lambda: llm.generate_memo(
    "Candidate: Test Candidate\nInstitution: Test University\n"
    "Certificate: ABC/123 (registry found=False, status=None)\n"
    "Risk flags:\n- [high] CERT_NOT_FOUND: certificate not in registry")))