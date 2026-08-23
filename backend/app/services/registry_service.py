"""
RegistryService — lookup(cert_no) -> RegistryResult.

Pure SQLite read, no network. This is what makes fake certs impossible to
slip through per the architecture doc: "cert numbers not in the registry
are flagged automatically."

Seed the `registry` table from your synthetic dataset via `seed_registry.py`.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Registry
from app.schemas import RegistryResult


class RegistryService:
    def __init__(self, session: Session):
        self.session = session

    def lookup(self, cert_no: str | None) -> RegistryResult:
        if not cert_no:
            return RegistryResult(found=False, status="not_found")

        row = self.session.get(Registry, cert_no)
        if row is None:
            return RegistryResult(found=False, cert_no=cert_no, status="not_found")

        return RegistryResult(
            found=True,
            cert_no=row.cert_no,
            status=row.status,
            candidate_name=row.candidate_name,
            institution=row.institution,
        )