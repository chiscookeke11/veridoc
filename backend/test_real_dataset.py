"""
Runs process_case() against real cases from CivicVerify_Synthetic_Dataset_v1
and compares your Verifier's output against the dataset's own ground truth
(expected_label, expected_flags, risk_level in cases.csv).

Usage:
    python test_real_dataset.py <path_to_dataset_root> [case_id]

    path_to_dataset_root should be the folder that directly contains
    cases.csv, registry.csv, and the cases/ folder.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

from app.db import init_db
from app.pipeline import process_case

FILENAME_TO_SLOT = {
    "application_form.jpg": "application_form",
    "academic_certificate.jpg": "certificate",
    "identity_document.jpg": "id_document",
}


def load_case_row(dataset_root: Path, case_id: str) -> dict:
    with open(dataset_root / "cases.csv", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["case_id"] == case_id:
                return row
    raise ValueError(f"{case_id} not found in cases.csv")


def build_doc_paths(dataset_root: Path, case_row: dict) -> dict[str, str]:
    doc_paths = {}
    for rel_path in case_row["document_paths"].split("|"):
        rel_path = rel_path.strip()
        if not rel_path:
            continue
        filename = Path(rel_path).name
        slot = FILENAME_TO_SLOT.get(filename)
        if slot is None:
            print(f"  (skipping unrecognized document type: {filename})")
            continue
        full_path = dataset_root / rel_path
        if not full_path.exists():
            print(f"  WARNING: expected file missing: {full_path}")
            continue
        doc_paths[slot] = str(full_path)
    return doc_paths


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    dataset_root = Path(sys.argv[1])
    case_id = sys.argv[2] if len(sys.argv) > 2 else "CASE-001"

    if not (dataset_root / "cases.csv").exists():
        print(f"cases.csv not found directly inside {dataset_root}")
        print("Check for a nested folder — list what's actually there:")
        for p in dataset_root.iterdir():
            print(" ", p.name)
        sys.exit(1)

    init_db()

    case_row = load_case_row(dataset_root, case_id)
    doc_paths = build_doc_paths(dataset_root, case_row)

    print(f"=== {case_id} ===")
    print(f"Dataset says: anomaly_type={case_row['anomaly_type']!r}, "
          f"expected_label={case_row['expected_label']!r}, "
          f"expected_flags={case_row['expected_flags']!r}, "
          f"risk_level={case_row['risk_level']!r}")
    print(f"Documents found: {list(doc_paths.keys())}")

    if len(doc_paths) < 2:
        print("Not enough documents present to run process_case meaningfully.")
        sys.exit(1)

    start = time.time()
    result = process_case(doc_paths, officer_id="officer-demo-1")
    elapsed = time.time() - start

    print(f"\n--- Your pipeline's output (took {elapsed:.1f}s) ---")
    print("Fields:  ", result.fields)
    print("Registry:", result.registry)
    print("Flags:   ", [f.code for f in result.flags])
    print("Risk:    ", result.overall_risk)
    print("Memo:    ", result.memo)

    print("\n--- Comparison ---")
    expected_flags = set(case_row["expected_flags"].split(",")) if case_row["expected_flags"] else set()
    expected_flags.discard("")
    got_flags = {f.code for f in result.flags}
    if expected_flags == got_flags:
        print(f"MATCH: flags exactly match expected {expected_flags or '(none)'}")
    else:
        missed = expected_flags - got_flags
        extra = got_flags - expected_flags
        if missed:
            print(f"MISSED (dataset expected, Verifier didn't catch): {missed}")
        if extra:
            print(f"EXTRA (Verifier flagged, dataset didn't expect): {extra}")


if __name__ == "__main__":
    main()