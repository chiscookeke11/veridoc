# CivicVerify AI

CivicVerify AI is an offline, human-in-the-loop document verification prototype for African public-sector and education offices. It helps officers review an applicant's application form, academic certificate, and ID document without sending sensitive records to a cloud service.

Built for the [Africa Deep Tech Challenge 2026](https://africadeeptech.org/challenge-2026/) — Autonomous AI Agents track.

## What it does

An officer uploads three documents for one candidate. CivicVerify AI then:

- extracts text from images or PDFs with local Tesseract OCR;
- uses a local `llama.cpp`/GGUF model to convert noisy OCR text into structured fields;
- checks certificate details against a local SQLite registry;
- applies deterministic fraud and quality rules for mismatches, revoked or missing registry entries, missing certificate numbers, and ID expiry inconsistencies;
- drafts a short officer memo with a local LLM;
- lets the officer approve, reject, or escalate the case; and
- stores the case, documents, risk flags, and decision history in a local audit database.

The AI flags. The officer decides.

## Current implementation status

This repository currently contains a working Python backend and Streamlit officer UI under [`backend/`](backend/). The core public API is intentionally small:

```python
process_case(document_paths, officer_id=None)       -> CaseResult
lookup_registry(certificate_number)                -> RegistryResult
verify_case(extracted_fields, registry_result)     -> list[RiskFlag]
generate_memo(case_result)                         -> str
save_decision(case_id, officer_decision)           -> None
```

The implementation is local-first by design: OCR runs through Tesseract, the language model is loaded from a local GGUF file, and the registry/audit trail are stored in SQLite.

## Tech stack

- **App/UI:** Streamlit
- **Language:** Python
- **OCR:** Tesseract via `pytesseract`; PDF support via `pdf2image`/Poppler
- **LLM runtime:** `llama-cpp-python` with a local GGUF model
- **Database:** SQLite with SQLAlchemy ORM
- **Data validation:** Pydantic v2
- **Tests/checks:** pytest plus script-style pipeline checks

## Repository layout

```text
CivicVerify-AI/
├── README.md
├── benchmark.md
├── CivicVerify_AI_Diagrams_A3.pdf
├── CivicVerify_AI_National_Architecture_A3 (1).pdf
├── CivicVerify AI Pitch Deck v4.pptx
└── backend/
    ├── streamlit_app.py              # Streamlit officer workflow
    ├── pyproject.toml                # Project metadata/dependencies for uv-style installs
    ├── requirements.txt              # pip-compatible dependency list
    ├── uv.lock
    ├── app/
    │   ├── db.py                     # SQLite engine/session helpers
    │   ├── models.py                 # SQLAlchemy data model
    │   ├── pipeline.py               # Public flat function API
    │   ├── schemas.py                # Pydantic DTOs
    │   ├── workflow.py               # OCR -> extract -> registry -> verify -> memo orchestration
    │   └── services/
    │       ├── llm_service.py        # Local llama.cpp extraction and memo generation
    │       ├── ocr_service.py        # Image/PDF OCR
    │       ├── registry_service.py   # SQLite registry lookup
    │       └── verifier.py           # Deterministic risk flag rules
    ├── scripts/
    │   └── seed_registry.py          # Load synthetic registry CSV into SQLite
    ├── packaging/                    # Windows launcher/installer assets
    ├── test_docs/                    # Sample/generated document images
    ├── tests/test_verifier.py        # pytest verifier tests
    └── test_*.py                     # script-style smoke and dataset checks
```

## Prerequisites

Install these system tools before running the full OCR pipeline:

1. **Python** compatible with the backend dependency set.
   - `backend/pyproject.toml` currently declares `requires-python = ">=3.14"`.
   - If you install from `requirements.txt`, use a modern Python version supported by the listed packages.
2. **Tesseract OCR** available on `PATH`.
3. **Poppler** if you need PDF uploads through `pdf2image`.
4. A **local GGUF model** for `llama-cpp-python`.

The default model path is:

```text
backend/models/model.Q4_K_M.gguf
```

You can override it with:

```bash
export CIVICVERIFY_MODEL_PATH=/absolute/path/to/model.gguf
```

Useful optional runtime variables:

```bash
export CIVICVERIFY_DB_PATH=civicverify.db
export CIVICVERIFY_N_CTX=4096
export CIVICVERIFY_N_THREADS=4
export CIVICVERIFY_TESSERACT_CMD=/path/to/tesseract
```

## Quick start

From a fresh checkout:

```bash
git clone https://github.com/<your-org-or-user>/CivicVerify-AI.git
cd CivicVerify-AI/backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Add or point to a GGUF model:

```bash
mkdir -p models
# copy your model to models/model.Q4_K_M.gguf
# or set CIVICVERIFY_MODEL_PATH=/path/to/your-model.gguf
```

Start the officer UI:

```bash
streamlit run streamlit_app.py
```

The app will create the SQLite tables automatically on startup.

## Seeding the local registry

If you have the synthetic dataset registry CSV, load it into the local SQLite database before running dataset cases:

```bash
cd backend
python scripts/seed_registry.py /path/to/CivicVerify_Synthetic_Dataset_v1/registry.csv
```

Expected columns are:

```text
certificate_number,candidate_name,institution,issue_date,status
```

## Running checks

Run the deterministic verifier tests:

```bash
cd backend
pytest tests/test_verifier.py -v
```

Run the generated-image end-to-end smoke test, which requires Tesseract and a configured GGUF model:

```bash
cd backend
python test_full_pipeline.py
```

Run a real synthetic dataset case after seeding the registry:

```bash
cd backend
python test_real_dataset.py /path/to/CivicVerify_Synthetic_Dataset_v1 CASE-001
```

Other script checks in `backend/test_extraction.py`, `backend/test_memo.py`, and `backend/test_timing.py` exercise the local LLM service directly.

## Officer workflow

1. **Upload:** officer uploads application form, certificate, and ID document.
2. **Extract:** OCR and LLM extraction produce editable structured fields.
3. **Verify:** deterministic checks raise human-readable risk flags.
4. **Decide:** officer reviews the memo and chooses approve, reject, or escalate.
5. **Audit:** recent cases can be viewed and exported to CSV.

## Risk checks currently implemented

- `NAME_MISMATCH` — candidate names differ across submitted documents.
- `REGISTRY_NOT_FOUND` — certificate number is not in the local registry.
- `CERTIFICATE_REVOKED` — registry status marks the certificate as revoked.
- `IDENTITY_DOCUMENT_EXPIRED` — ID expiry value conflicts with the expiry value declared elsewhere in the submitted documents.
- `MISSING_CERTIFICATE_NUMBER` — certificate number could not be extracted from the certificate document.

## Design targets

| Metric | Target |
| --- | --- |
| Field extraction on clean cases | ≥ 80% |
| Missing-document detection | ≥ 90% |
| Mismatch detection | ≥ 85% |
| Registry lookup | ≥ 95% |
| Workflow time per case | < 60 seconds after model load |
| Peak RAM | < 7 GB |
| External network calls | 0 |

## Notes and limitations

- All included/sample data is synthetic. Do not commit real applicant data.
- The project is decision support only; it should not make automatic eligibility decisions.
- LLM quality depends heavily on the local GGUF model you provide.
- Full PDF OCR requires Poppler in addition to Tesseract.
- Duplicate certificate scenarios are noted by the registry seeder, but representing duplicate registry rows requires a future schema change because certificate number is currently the registry primary key.

## License

MIT
