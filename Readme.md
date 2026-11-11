# CivicVerify AI hgh

**The AI flags. The officer decides.**

CivicVerify AI is an offline document-verification assistant for government and education offices. An officer uploads an applicant's application form, academic certificate and ID document. The app reads them, extracts the key fields, checks the certificate against a local registry, raises risk flags, drafts a short memo, and records the officer's decision in an audit log.

Everything runs on the officer's own laptop. **No cloud APIs, no document ever leaves the machine.** All AI inference (OCR and language model) runs locally through the [QVAC SDK](https://docs.qvac.tether.io/) by Tether.

---

## How QVAC is used

QVAC powers **both AI steps** in the pipeline. Nothing else in the app calls a model.

| Step                                | What it does                                                                                            | QVAC feature                   | Model                                |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------ | ------------------------------------ |
| **1. OCR**                          | Reads text from each uploaded image or PDF page                                                         | `ocr_stream` (GGML OCR engine) | `OCR_LATIN` (English / Latin script) |
| **2. Field extraction**             | Turns noisy OCR text into structured fields (name, institution, certificate no., dates, ID no.) as JSON | `completion` at temperature 0  | Qwen3 1.7B Q4 (`QWEN3_1_7B_INST_Q4`) |
| **3. Officer memo**                 | Writes a 2-4 sentence plain-language summary of the case and its risk flags                             | `completion`                   | same Qwen3 model                     |
| **4. Applicant reply** _(optional)_ | Drafts a polite reply to the applicant in English, Pidgin or Yoruba                                     | `completion`                   | same Qwen3 model                     |

Models are managed with `load_model` (downloaded once, then cached on disk and kept in memory) and released with `unload_model` when the app exits.

### Where the AI stops and the rules begin

The language model **never decides** whether a document is genuine. Verification is done by a deterministic rule engine (`app/services/verifier.py`) with no model calls:

- names compared across the three documents
- certificate number looked up in the local SQLite registry (not found, or revoked)
- ID expiry date cross-checked against the other documents
- missing certificate number

QVAC reads and explains; rules flag; the officer approves, rejects or escalates.

### Pipeline

```
 Application form ─┐
 Certificate ──────┼─▶ OCR (QVAC ocr_stream) ──▶ raw text per document
 ID document ──────┘                                   │
                                                       ▼
                                      Field extraction (QVAC completion → JSON)
                                                       │
                              ┌────────────────────────┴───────────────────────┐
                              ▼                                                ▼
                   Registry lookup (SQLite)                          Merged candidate fields
                              │                                                │
                              └────────────────▶ Rule-based verifier ◀─────────┘
                                                       │  risk flags
                                                       ▼
                                      Officer memo (QVAC completion)
                                                       │
                                                       ▼
                              Officer reviews ─▶ approve / reject / escalate
                                                       │
                                                       ▼
                                             Audit log (SQLite)
```

### How the QVAC integration is built

- **`app/services/qvac_runtime.py`**: the only file that talks to the QVAC SDK. The SDK is asyncio-based while the rest of the app is synchronous, so this module runs one event loop on a background thread, keeps one QVAC client connected, loads the OCR and LLM models lazily on first use, and exposes simple blocking methods: `ocr_text(path)` and `chat(system, user, ...)`.
- **`app/services/ocr_service.py`**: `OCRService.extract(path)` returns raw text. PDFs are rasterised page by page, then each page goes through QVAC OCR. OCR blocks are sorted into reading order using their bounding boxes, so a label and its value stay on the same line.
- **`app/services/llm_service.py`**: `LLMService` has three methods (`extract_fields`, `generate_memo`, `generate_applicant_reply`), all routed through one `_chat()` call into the runtime. Small local models do not always return clean JSON, so the output is parsed tolerantly (`_parse_json_loose`) and unknown or illegible fields come back as `null` rather than being invented.
- **Swap points**: `Workflow`, the verifier, the database and the UI depend only on "text in, text out". Replacing the OCR engine or the model touches only the two service files and the runtime.

---

## Tools and stack

| Area                           | Tool                                                                      |
| ------------------------------ | ------------------------------------------------------------------------- |
| Local AI inference (OCR + LLM) | **QVAC SDK for Python** (`tetherto-qvac-sdk`)                             |
| OCR model                      | QVAC GGML OCR, `OCR_LATIN`                                                |
| Language model                 | Qwen3 1.7B, 4-bit quantised, from the QVAC model registry                 |
| UI                             | Streamlit                                                                 |
| Storage                        | SQLite via SQLAlchemy (cases, documents, risk flags, decisions, registry) |
| Data models                    | Pydantic                                                                  |
| PDF input                      | `pdf2image` (needs [Poppler](https://poppler.freedesktop.org/) installed) |
| Image handling                 | Pillow                                                                    |
| Tests                          | pytest plus end-to-end scripts                                            |

---

## Running it

### Requirements

- Windows, macOS or Linux (the QVAC bundled wheel ships for win32-x64, darwin-arm64, linux-x64, linux-arm64)
- Python 3.10 or newer (the QVAC SDK requirement; `.python-version` pins the version this project was developed on)
- Internet **once**, to download the models (about 100 MB for OCR and about 1 GB for the language model)
- 8 GB RAM minimum; 16 GB recommended
- Poppler on your PATH if you want to upload PDFs

### Install

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate      macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` installs the QVAC bundled wheel from the matching GitHub release (it includes the QVAC worker, so no separate Node.js install is needed).

Using `uv`? Add this to `pyproject.toml`, then sync:

```toml
[tool.uv]
find-links = ["https://github.com/tetherto/qvac/releases/expanded_assets/sdk-v0.23.0"]
```

```bash
uv add tetherto-qvac-sdk==0.23.0
```

### Check that QVAC works

```bash
python test_qvac_smoke.py
```

This OCRs a sample certificate, runs a chat completion, extracts fields and drafts a memo. The first run downloads the models, so it is slow; later runs use the cache.

### Seed the registry (optional)

```bash
python scripts/seed_registry.py path/to/registry.csv
```

Expected columns: `certificate_number, candidate_name, institution, issue_date, status`.

### Start the app

```bash
python -m streamlit run streamlit_app.py
```

Open the address it prints (usually http://localhost:8501). Use `streamlit run`, not `python streamlit_app.py`.

### Officer screens

1. **Upload**: application form, certificate, ID document
2. **Extract**: review and edit the extracted fields
3. **Verify and decide**: risk flags and the drafted memo
4. **Decision**: approve, reject or escalate
5. **Audit log**: every case and decision

---

## Offline use

QVAC downloads models from its registry the first time they are needed and caches them locally. After that, OCR and the language model run entirely on the device.

To confirm on your machine:

1. Run the app (or `python test_qvac_smoke.py`) once with internet so the models are cached.
2. Disconnect from the network.
3. Run it again and process a case.

To control where models are stored (for example, to copy them to another laptop), set an absolute path:

```bash
# Windows
set QVAC_CACHE_DIR=C:\qvac-cache
```

If the registry download is unreliable on your network, download the model file yourself and point the app at it with `CIVICVERIFY_MODEL_PATH` (see below).

---

## Configuration

All optional, set as environment variables.

| Variable                 | Default              | Purpose                                                                          |
| ------------------------ | -------------------- | -------------------------------------------------------------------------------- |
| `CIVICVERIFY_QVAC_MODEL` | `QWEN3_1_7B_INST_Q4` | Name of any model constant from `tetherto.qvac_sdk.models`                       |
| `CIVICVERIFY_MODEL_PATH` | unset                | Path to a local `.gguf` file, used instead of the registry download              |
| `CIVICVERIFY_N_CTX`      | `4096`               | Context window size                                                              |
| `CIVICVERIFY_NO_THINK`   | `1`                  | Skip Qwen3's reasoning preamble, which speeds up extraction and keeps JSON clean |
| `QVAC_CACHE_DIR`         | QVAC default         | Absolute path where QVAC stores downloaded models                                |

---

## Performance

Measured on a 16 GB laptop with an integrated Intel GPU (QVAC offloads only part of the model to the GPU there):

| Step                                   | Time                                        |
| -------------------------------------- | ------------------------------------------- |
| Field extraction (per document)        | about 18 s                                  |
| Memo generation                        | about 9 s                                   |
| Full case (3 documents, cached models) | to be recorded with `test_full_pipeline.py` |

Speed varies with hardware and background load. Faster machines with more GPU memory will be quicker.

---

## Tests

```bash
python -m pytest tests/test_verifier.py   # rule engine, no models needed
python test_qvac_smoke.py                 # QVAC OCR + LLM sanity check
python test_full_pipeline.py              # synthetic documents end to end
python test_real_dataset.py               # compares flags with the dataset ground truth
```

---

## Project structure

```
backend/
├── streamlit_app.py          # Officer UI (5 screens)
├── app/
│   ├── pipeline.py           # Flat entry points: process_case, verify_case, generate_memo, ...
│   ├── workflow.py           # Orchestrator: OCR → extract → registry → verify → memo → persist
│   ├── models.py, db.py      # SQLite tables and session
│   ├── schemas.py            # Pydantic data classes
│   └── services/
│       ├── qvac_runtime.py   # QVAC SDK connection, model loading, blocking helpers
│       ├── ocr_service.py    # OCR via QVAC
│       ├── llm_service.py    # Extraction, memo and applicant reply via QVAC
│       ├── registry_service.py  # Certificate registry lookup (SQLite)
│       └── verifier.py       # Deterministic risk rules (no AI)
├── scripts/seed_registry.py  # Load registry.csv into SQLite
├── test_docs/                # Sample documents
├── tests/                    # pytest unit tests
└── packaging/                # Windows installer files
```
