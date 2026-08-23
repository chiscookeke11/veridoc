"""
Pydantic data classes — mirrors the bottom row of the UML class diagram
(05 · UML CLASS DIAGRAM): ExtractedFields, RegistryResult, RiskFlag, composed
into CaseResult.
"""

from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field


class ExtractedFields(BaseModel):
    """Output of LLMService.extract_fields() — screen 2 'Extracted fields'."""

    candidate_name: Optional[str] = None
    date_of_birth: Optional[str] = (
        None  # ISO date string; kept loose since OCR is messy
    )
    institution: Optional[str] = None
    cert_no: Optional[str] = None
    issue_date: Optional[str] = None
    id_number: Optional[str] = None
    expiry_date: Optional[str] = None  # relevant for ID documents


class RegistryResult(BaseModel):
    """Output of RegistryService.lookup()."""

    found: bool
    cert_no: Optional[str] = None
    status: Optional[str] = None  # valid | revoked | unknown | not_found
    candidate_name: Optional[str] = None
    institution: Optional[str] = None


class RiskFlag(BaseModel):
    """One line item in the 'Verify & decide' screen."""

    level: Literal["low", "medium", "high"]
    code: str
    reason: str
    evidence: Optional[str] = None


class CaseResult(BaseModel):
    """
    Composes everything the officer needs for screens 3-4:
    extracted fields, registry match, risk flags, and the drafted memo.
    """

    case_id: str
    fields: ExtractedFields
    registry: RegistryResult
    flags: list[RiskFlag] = Field(default_factory=list)
    memo: str = ""

    @property
    def overall_risk(self) -> Literal["low", "medium", "high"]:
        if any(f.level == "high" for f in self.flags):
            return "high"
        if any(f.level == "medium" for f in self.flags):
            return "medium"
        return "low"


class DecisionRequest(BaseModel):
    case_id: str
    officer_id: str
    action: Literal["approve", "reject", "escalate"]
