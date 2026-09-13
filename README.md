# CivicVerify AI

CivicVerify AI is a local-first document verification platform for public-sector, education, and other high-trust workflows. It helps authorized officers review application forms, academic certificates, and identity documents while keeping sensitive records on their own infrastructure.

The platform extracts document data with OCR, structures it with a local language model, compares certificate details with a local registry, and applies deterministic checks to identify inconsistencies and potential fraud. It then produces a concise review memo so officers can make an informed decision to approve, reject, or escalate a case.

CivicVerify AI is designed as decision-support software: automation highlights risk, while people retain responsibility for every final outcome. Its local architecture supports privacy-conscious deployments by avoiding external network calls and storing case records, verification results, and decision history in a local audit database.

## Key capabilities

- OCR for image and PDF documents
- Local AI-assisted extraction of structured document fields
- Certificate registry lookups and fraud-risk checks
- Officer review, approval, rejection, and escalation workflows
- Auditable local storage of cases, documents, risk flags, and decisions

## Technology

The project includes a Python and Streamlit verification application powered by Tesseract OCR, a local GGUF model through `llama.cpp`, SQLite, SQLAlchemy, and Pydantic. It also contains a Next.js frontend for presenting the CivicVerify AI product experience.
