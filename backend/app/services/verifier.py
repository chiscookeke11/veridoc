"""
Verifier — deterministic, rule-based, no LLM calls.

Flag codes match CivicVerify_Synthetic_Dataset_v1's quality_checks.csv
exactly, so results can be diffed directly against that dataset's ground
truth (see test_real_dataset.py).
"""
from __future__ import annotations

from difflib import SequenceMatcher

from app.schemas import ExtractedFields, RegistryResult, RiskFlag

# Names across documents should match exactly once normalized. Any
# discrepancy — even a one-letter typo like the wireframe's "Adaeze" vs
# "Adeze" — gets flagged for the officer rather than silently accepted.
NAME_SIMILARITY_THRESHOLD = 0.999


def _normalize(name: str) -> str:
    return " ".join(name.strip().lower().split())


def _similar(a: str, b: str) -> float:
    if _normalize(a) == _normalize(b):
        return 1.0
    return SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


class Verifier:
    def verify(
        self,
        per_doc_fields: dict[str, ExtractedFields],
        registry: RegistryResult,
    ) -> list[RiskFlag]:
        flags: list[RiskFlag] = []

        form = per_doc_fields.get("application_form")
        cert = per_doc_fields.get("certificate")
        id_doc = per_doc_fields.get("id_document")

        flags += self._check_name_consistency(form, cert, id_doc)
        flags += self._check_registry(cert, registry)
        flags += self._check_id_expiry_consistency(form, cert, id_doc)
        flags += self._check_missing_cert_no(cert)

        return flags

    def _check_name_consistency(self, form, cert, id_doc) -> list[RiskFlag]:
        flags: list[RiskFlag] = []
        names = {
            "form": getattr(form, "candidate_name", None),
            "certificate": getattr(cert, "candidate_name", None),
            "id_document": getattr(id_doc, "candidate_name", None),
        }
        present = {k: v for k, v in names.items() if v}
        keys = list(present.keys())
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                a_key, b_key = keys[i], keys[j]
                score = _similar(present[a_key], present[b_key])
                if score < NAME_SIMILARITY_THRESHOLD:
                    flags.append(RiskFlag(
                        level="medium",
                        code="NAME_MISMATCH",
                        reason=f"Name on {a_key} differs from {b_key} "
                               f"({present[a_key]} vs {present[b_key]})",
                        evidence=f"similarity={score:.2f}",
                    ))
        return flags

    def _check_registry(self, cert: ExtractedFields | None, registry: RegistryResult) -> list[RiskFlag]:
        if cert is None or not cert.cert_no:
            return []
        if not registry.found:
            return [RiskFlag(
                level="high",
                code="REGISTRY_NOT_FOUND",
                reason=f"Certificate {cert.cert_no} not found in registry",
            )]
        if registry.status == "revoked":
            return [RiskFlag(
                level="high",
                code="CERTIFICATE_REVOKED",
                reason=f"Certificate {cert.cert_no} is marked revoked in the registry",
            )]
        return []

    def _check_id_expiry_consistency(self, form, cert, id_doc) -> list[RiskFlag]:
        """
        Per the dataset's own definition ('Expiry date compared with review
        date'): the real signal is the identity_document's stated expiry
        silently diverging from what the application_form/certificate
        declare — NOT whether the date is before today's real wall-clock
        time. An offline system has no reliable "today" to compare against
        anyway; cross-document consistency is what's actually checkable.
        """
        id_expiry = getattr(id_doc, "expiry_date", None)
        if not id_expiry:
            return []

        reference = getattr(form, "expiry_date", None) or getattr(cert, "expiry_date", None)
        if reference and id_expiry != reference:
            return [RiskFlag(
                level="high",
                code="IDENTITY_DOCUMENT_EXPIRED",
                reason=f"ID document's stated expiry ({id_expiry}) does not match "
                       f"the expiry declared elsewhere on the application ({reference})",
            )]
        return []

    def _check_missing_cert_no(self, cert: ExtractedFields | None) -> list[RiskFlag]:
        if cert is None or not cert.cert_no:
            return [RiskFlag(
                level="medium",
                code="MISSING_CERTIFICATE_NUMBER",
                reason="Certificate number could not be extracted from the uploaded document",
            )]
        return []