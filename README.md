# CivicVerify AI

Offline document verification agent for African government offices. Runs on an 8 GB laptop, no internet required.

Built for the [Africa Deep Tech Challenge 2026](https://africadeeptech.org/challenge-2026/) — Autonomous AI Agents track.

## What it does

An officer uploads a candidate's application form, certificate, and ID. CivicVerify AI:

- Runs OCR and extracts key fields into structured JSON
- Cross-checks fields across documents
- Looks up the certificate in a local mock registry
- Flags missing, mismatched, duplicate, or suspicious cases
- Drafts an officer memo and applicant reply (English or Pidgin/Yoruba)
- Logs the officer's final decision to a local audit trail

The AI flags. The officer decides.

## Stack

Python 3.11 · llama.cpp (3B–4B GGUF, Q4_K_M) · Tesseract · SQLite · Pydantic · Streamlit · pytest

## Getting started

**Prerequisites:** Python 3.11+, Tesseract OCR, and a GGUF model in `models/`.

```bash
git clone https://github.com/<your-username>/civicverify-ai.git
cd civicverify-ai
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```
civicverify-ai/
├── app.py              # Streamlit entry point
├── src/
│   ├── ocr.py
│   ├── preprocess.py
│   ├── extraction.py
│   ├── verifier.py
│   ├── registry.py
│   ├── memo_generator.py
│   ├── schemas.py
│   └── audit_log.py
├── data/
│   ├── registry.csv
│   ├── cases.csv
│   └── samples/
├── tests/
├── models/             # GGUF weights (gitignored)
├── requirements.txt
├── REPORT.md
└── README.md
```

## Module contract

```python
process_case(document_paths)                     -> CaseResult
lookup_registry(certificate_number)              -> RegistryResult
verify_case(extracted_fields, registry_result)   -> list[RiskFlag]
generate_memo(case_result)                       -> str
save_decision(case_id, officer_decision)         -> None
```

## Targets

| Metric | Target |
|---|---|
| Field extraction (clean cases) | ≥ 80% |
| Missing-document detection | ≥ 90% |
| Mismatch detection | ≥ 85% |
| Registry lookup | ≥ 95% |
| Workflow time per case | < 60 s |
| Peak RAM | < 7 GB |
| External network calls | 0 |

## Notes

- All data is synthetic. No real applicants.
- Decision support only — not automated decision-making.
- Full design notes, benchmarks, and limitations in [`REPORT.md`](REPORT.md).

## License

MIT
