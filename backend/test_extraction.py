# test_extraction.py  (put this in your backend/ root, next to streamlit_app.py)
from app.services.llm_service import LLMService

svc = LLMService()
sample_text = (
    "Application for admission. Name: Adaeze Okafor. "
    "Certificate No: MFP-2019-987. Institution: Federal Polytechnic. "
    "Date of Birth: 1998-04-12."
)

result = svc.extract_fields(sample_text)
print(result)
