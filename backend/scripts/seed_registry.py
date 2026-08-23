"""
Seed the local `registry` table from your CivicVerify_Synthetic_Dataset_v1's
registry.csv. Matches that dataset's real column names:

    certificate_number, candidate_name, institution, issue_date, status

Usage:
    python scripts/seed_registry.py path/to/registry.csv
"""
from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import init_db, get_session
from app.models import Registry


def parse_date(value: str | None):
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def main(csv_path: str):
    init_db()
    count = 0
    skipped_duplicates = 0
    with get_session() as session, open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        seen_this_run = set()
        for row in reader:
            cert_no = (row.get("certificate_number") or "").strip()
            if not cert_no:
                continue
            if cert_no in seen_this_run:
                skipped_duplicates += 1
                continue
            seen_this_run.add(cert_no)
            existing = session.get(Registry, cert_no)
            if existing:
                continue
            session.add(Registry(
                cert_no=cert_no,
                candidate_name=(row.get("candidate_name") or "").strip(),
                institution=(row.get("institution") or "").strip(),
                issue_date=parse_date(row.get("issue_date")),
                status=(row.get("status") or "valid").strip() or "valid",
            ))
            count += 1
    print(f"Seeded {count} registry entries from {csv_path}")
    if skipped_duplicates:
        print(f"NOTE: skipped {skipped_duplicates} duplicate certificate_number rows "
              f"(this dataset uses duplicate registry entries as its DUPLICATE_CERTIFICATE_NUMBER "
              f"fraud scenario — your Registry model needs a schema change to represent both "
              f"entries once you build that check).")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])