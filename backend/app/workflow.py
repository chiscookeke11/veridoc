"""
Workflow — the orchestrator (04 · SEQUENCE DIAGRAM, 05 · UML CLASS DIAGRAM).

process_case(paths) walks: OCR each doc -> LLM extract fields per doc ->
registry lookup on the certificate's cert_no -> rule-based verify ->
LLM drafts a memo -> persists Case/Documents/RiskFlags to SQLite ->
returns a CaseResult for screens 3-4.

save_decision(case_id, officer_id, action) is the only other public method —
it's called after the human-in-the-loop step and writes the audit entry.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.models import (
    Case,
    Document,
    RiskFlagRow,
    Decision,
    CaseStatus,
    DecisionAction,
    DocType,
)
from app.schemas import CaseResult, ExtractedFields
from app.services.ocr_service import OCRService
from app.services.llm_service import LLMService
from app.services.registry_service import RegistryService
from app.services.verifier import Verifier

# Map a filename/path hint to a DocType. In production the officer picks
# the slot on upload (screen 1's three drop zones); this is a convenience
# fallback for scripts/tests that just pass a flat list of paths.
_DOC_TYPE_ORDER = [DocType.APPLICATION_FORM, DocType.CERTIFICATE, DocType.ID_DOCUMENT]


class Workflow:
    def __init__(
        self,
        session: Session,
        ocr: OCRService | None = None,
        llm: LLMService | None = None,
    ):
        self.session = session
        self.ocr = ocr or OCRService()
        self.llm = llm or LLMService()
        self.registry = RegistryService(session)
        self.verifier = Verifier()

    def process_case(
        self,
        doc_paths: dict[
            str, str
        ],  # {"application_form": path, "certificate": path, "id_document": path}
        officer_id: str | None = None,
    ) -> CaseResult:
        case = Case(officer_id=officer_id, status=CaseStatus.OPEN)
        self.session.add(case)
        self.session.flush()  # get case.case_id before we attach children

        per_doc_fields: dict[str, ExtractedFields] = {}

        for doc_type_str, path in doc_paths.items():
            raw_text = self.ocr.extract(path)
            fields = self.llm.extract_fields(raw_text)
            per_doc_fields[doc_type_str] = fields

            self.session.add(
                Document(
                    case_id=case.case_id,
                    doc_type=DocType(doc_type_str),
                    file_path=str(path),
                    raw_text=raw_text,
                )
            )

        # Primary fields shown on screen 2 come from the certificate first,
        # falling back to the application form for anything missing.
        primary = self._merge_fields(
            per_doc_fields.get("certificate"),
            per_doc_fields.get("application_form"),
            per_doc_fields.get("id_document"),
        )
        case.candidate_name = primary.candidate_name
        case.date_of_birth = _safe_date(primary.date_of_birth)
        case.institution = primary.institution
        case.cert_no = primary.cert_no
        case.status = CaseStatus.EXTRACTED

        registry_result = self.registry.lookup(primary.cert_no)
        flags = self.verifier.verify(per_doc_fields, registry_result)

        for f in flags:
            self.session.add(
                RiskFlagRow(
                    case_id=case.case_id,
                    level=f.level,
                    code=f.code,
                    reason=f.reason,
                )
            )
        case.status = CaseStatus.VERIFIED

        memo = self.llm.generate_memo(
            self._summarize_for_memo(primary, registry_result, flags)
        )

        self.session.flush()

        return CaseResult(
            case_id=case.case_id,
            fields=primary,
            registry=registry_result,
            flags=flags,
            memo=memo,
        )

    def save_decision(self, case_id: str, officer_id: str, action: str) -> Decision:
        decision = Decision(
            case_id=case_id, officer_id=officer_id, action=DecisionAction(action)
        )
        self.session.add(decision)

        case = self.session.get(Case, case_id)
        if case:
            case.status = CaseStatus.DECIDED

        self.session.flush()
        return decision

    @staticmethod
    def _merge_fields(*sources: ExtractedFields | None) -> ExtractedFields:
        merged: dict = {}
        for source in sources:
            if source is None:
                continue
            for k, v in source.model_dump().items():
                if not merged.get(k) and v:
                    merged[k] = v
        return ExtractedFields(**merged)

    @staticmethod
    def _summarize_for_memo(fields: ExtractedFields, registry, flags) -> str:
        flag_lines = (
            "\n".join(f"- [{f.level}] {f.code}: {f.reason}" for f in flags) or "- none"
        )
        return (
            f"Candidate: {fields.candidate_name}\n"
            f"Institution: {fields.institution}\n"
            f"Certificate: {fields.cert_no} (registry found={registry.found}, status={registry.status})\n"
            f"Risk flags:\n{flag_lines}"
        )


def _safe_date(value: str | None):
    if not value:
        return None
    from datetime import datetime

    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None
