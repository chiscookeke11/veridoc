"""
Verifier is pure and deterministic (no LLM, no network) — it should be the
easiest part of this pipeline to get full coverage on. Run with:
    pytest tests/test_verifier.py -v
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas import ExtractedFields, RegistryResult
from app.services.verifier import Verifier


def test_name_mismatch_flagged():
    v = Verifier()
    docs = {
        "application_form": ExtractedFields(candidate_name="Adaeze Okafor"),
        "certificate": ExtractedFields(candidate_name="Adeze Okafor", cert_no="MFP-2019-987"),
    }
    registry = RegistryResult(found=True, cert_no="MFP-2019-987", status="valid",
                               candidate_name="Adeze Okafor", institution="Fed. Polytechnic")
    flags = v.verify(docs, registry)
    codes = [f.code for f in flags]
    assert "NAME_MISMATCH" in codes


def test_cert_not_in_registry_is_high_risk():
    v = Verifier()
    docs = {"certificate": ExtractedFields(candidate_name="Chika Eze", cert_no="FAKE-0001")}
    registry = RegistryResult(found=False, status="not_found")
    flags = v.verify(docs, registry)
    assert any(f.code == "REGISTRY_NOT_FOUND" and f.level == "high" for f in flags)


def test_id_expiry_mismatch_flagged():
    v = Verifier()
    docs = {
        "application_form": ExtractedFields(expiry_date="2027-11-23"),
        "id_document": ExtractedFields(expiry_date="2019-03-07"),
    }
    registry = RegistryResult(found=False, status="not_found")
    flags = v.verify(docs, registry)
    assert any(f.code == "IDENTITY_DOCUMENT_EXPIRED" for f in flags)


def test_id_expiry_consistent_not_flagged():
    v = Verifier()
    docs = {
        "application_form": ExtractedFields(expiry_date="2024-08-16"),
        "certificate": ExtractedFields(expiry_date="2024-08-16"),
        "id_document": ExtractedFields(expiry_date="2024-08-16"),
    }
    registry = RegistryResult(found=False, status="not_found")
    flags = v.verify(docs, registry)
    assert not any(f.code == "IDENTITY_DOCUMENT_EXPIRED" for f in flags)


def test_clean_case_no_flags_except_expected():
    v = Verifier()
    docs = {
        "application_form": ExtractedFields(candidate_name="Musa Ibrahim"),
        "certificate": ExtractedFields(candidate_name="Musa Ibrahim", cert_no="ABC-123"),
        "id_document": ExtractedFields(candidate_name="Musa Ibrahim", expiry_date="2030-01-01"),
    }
    registry = RegistryResult(found=True, cert_no="ABC-123", status="valid",
                               candidate_name="Musa Ibrahim", institution="UNN")
    flags = v.verify(docs, registry)
    assert flags == []