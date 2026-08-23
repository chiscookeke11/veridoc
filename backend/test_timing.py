# test_timing.py — replace with this
import time
from app.services.llm_service import LLMService, _get_llm

# Force model load first, outside the timer
print("Loading model...")
load_start = time.time()
_get_llm()
print(f"Model load took {time.time() - load_start:.1f}s (one-time cost)")

svc = LLMService()

# Now time actual inference, isolated
start = time.time()
svc.extract_fields("Name: Musa Ibrahim. Certificate No: ABC-123. Institution: UNN.")
print(f"extract_fields (1st inference) took {time.time() - start:.1f}s")

start = time.time()
svc.extract_fields("Name: Chika Eze. Certificate No: XYZ-999. Institution: LASU.")
print(f"extract_fields (2nd inference) took {time.time() - start:.1f}s")
