"""
SQLAlchemy models — mirrors the ER diagram (03 · ENTITY-RELATIONSHIP DIAGRAM).

CASE is the hub. OFFICER makes many DECISIONs (1:N). Every DOCUMENT and
RISK_FLAG references a CASE. REGISTRY is the mock credential source of truth
that the Verifier checks candidate certs against.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, Date, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base

Base = declarative_base()


def _uuid() -> str:
    return str(uuid.uuid4())


class CaseStatus(str, enum.Enum):
    OPEN = "open"
    EXTRACTED = "extracted"
    VERIFIED = "verified"
    DECIDED = "decided"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DecisionAction(str, enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"


class DocType(str, enum.Enum):
    APPLICATION_FORM = "application_form"
    CERTIFICATE = "certificate"
    ID_DOCUMENT = "id_document"


class Officer(Base):
    __tablename__ = "officer"

    officer_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="reviewer")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    cases: Mapped[list["Case"]] = relationship("Case", back_populates="officer")
    decisions: Mapped[list["Decision"]] = relationship(
        "Decision", back_populates="officer"
    )


class Registry(Base):
    """Mock national/state credential registry — what the Verifier checks against."""

    __tablename__ = "registry"

    cert_no: Mapped[str] = mapped_column(String, primary_key=True)
    candidate_name: Mapped[str] = mapped_column(String, nullable=False)
    institution: Mapped[str] = mapped_column(String, nullable=False)
    issue_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="valid"
    )  # valid | revoked | unknown


class Case(Base):
    __tablename__ = "case"

    case_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    officer_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("officer.officer_id"), nullable=True
    )
    candidate_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    institution: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cert_no: Mapped[Optional[str]] = mapped_column(
        ForeignKey("registry.cert_no"), nullable=True
    )
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus), default=CaseStatus.OPEN, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    officer: Mapped[Optional["Officer"]] = relationship(
        "Officer", back_populates="cases"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="case", cascade="all, delete-orphan"
    )
    risk_flags: Mapped[list["RiskFlagRow"]] = relationship(
        "RiskFlagRow", back_populates="case", cascade="all, delete-orphan"
    )
    decisions: Mapped[list["Decision"]] = relationship(
        "Decision", back_populates="case", cascade="all, delete-orphan"
    )


class Document(Base):
    __tablename__ = "document"

    doc_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("case.case_id"), nullable=False)
    doc_type: Mapped[DocType] = mapped_column(Enum(DocType), nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    raw_text: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # OCR output, cached

    case: Mapped["Case"] = relationship("Case", back_populates="documents")


class RiskFlagRow(Base):
    __tablename__ = "risk_flag"

    flag_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("case.case_id"), nullable=False)
    level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), nullable=False)
    code: Mapped[str] = mapped_column(
        String, nullable=False
    )  # e.g. "NAME_MISMATCH", "ID_EXPIRED"
    reason: Mapped[str] = mapped_column(
        String, nullable=False
    )  # human-readable explanation

    case: Mapped["Case"] = relationship("Case", back_populates="risk_flags")


class Decision(Base):
    __tablename__ = "decision"

    decision_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("case.case_id"), nullable=False)
    officer_id: Mapped[str] = mapped_column(
        ForeignKey("officer.officer_id"), nullable=False
    )
    action: Mapped[DecisionAction] = mapped_column(Enum(DecisionAction), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped["Case"] = relationship("Case", back_populates="decisions")
    officer: Mapped["Officer"] = relationship("Officer", back_populates="decisions")
