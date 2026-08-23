"""
Module contract — flat functions, matching your README exactly:

    process_case(document_paths)                     -> CaseResult
    lookup_registry(certificate_number)              -> RegistryResult
    verify_case(extracted_fields, registry_result)   -> list[RiskFlag]
    generate_memo(case_result)                       -> str
    save_decision(case_id, officer_decision)         -> None

These are thin wrappers over workflow.py's class-based services — the classes
still exist underneath (so OCR/LLM/Registry/Verifier stay independently
swappable and unit-testable), this module is just the calling surface the
rest of the app (Streamlit UI, grading scripts, tests) imports from.
"""
from __future__ import annotations

from app.db import get_session
from app.schemas import CaseResult, ExtractedFields, RegistryResult, RiskFlag
from app.services.llm_service import LLMService
from app.services.registry_service import RegistryService
from app.services.verifier import Verifier
from app.workflow import Workflow


def process_case(document_paths: dict[str, str], officer_id: str | None = None) -> CaseResult:
    """
    document_paths: {"application_form": path, "certificate": path, "id_document": path}
    Runs OCR -> extract -> registry lookup -> verify -> memo -> persists to SQLite.
    """
    with get_session() as session:
        return Workflow(session).process_case(document_paths, officer_id=officer_id)


def lookup_registry(certificate_number: str) -> RegistryResult:
    with get_session() as session:
        return RegistryService(session).lookup(certificate_number)


def verify_case(
    extracted_fields: dict[str, ExtractedFields],
    registry_result: RegistryResult,
) -> list[RiskFlag]:
    """
    extracted_fields keyed by doc type: {"application_form": ..., "certificate": ..., "id_document": ...}
    Pure, deterministic, no I/O — safe to call outside a session.
    """
    return Verifier().verify(extracted_fields, registry_result)


def generate_memo(case_result: CaseResult) -> str:
    summary = Workflow._summarize_for_memo(case_result.fields, case_result.registry, case_result.flags)
    return LLMService().generate_memo(summary)


def save_decision(case_id: str, officer_decision: dict) -> None:
    """
    officer_decision: {"officer_id": str, "action": "approve" | "reject" | "escalate"}
    """
    with get_session() as session:
        Workflow(session).save_decision(
            case_id, officer_decision["officer_id"], officer_decision["action"]
        )
