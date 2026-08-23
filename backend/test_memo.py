# test_memo.py, same folder as test_extraction.py
from app.services.llm_service import LLMService

svc = LLMService()
summary = (
    "Candidate: Adaeze Okafor\n"
    "Institution: Federal Polytechnic\n"
    "Certificate: MFP-2019-987 (registry found=True, status=valid)\n"
    "Risk flags:\n"
    "- [medium] NAME_MISMATCH: Name on certificate differs from application_form (Adaeze Okafor vs Adeze Okafor)"
)
print(svc.generate_memo(summary))
