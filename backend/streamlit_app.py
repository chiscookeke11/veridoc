"""
Streamlit entry point — `streamlit run streamlit_app.py`.

Deliberately named streamlit_app.py, NOT app.py — a file called app.py
sitting next to the app/ package directory creates an import collision.
Rename the package instead of this file if you want `app.py` for the
README command to match literally.

Implements the 5 officer screens from your user-flow diagram:
1. Upload      2. Extract (editable)      3-4. Verify & decide      5. Audit
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import select

from app.db import init_db, get_session
from app.models import Case
from app.pipeline import process_case, verify_case, generate_memo, save_decision
from app.schemas import CaseResult, ExtractedFields

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="CivicVerify AI", layout="centered")
init_db()

if "case_result" not in st.session_state:
    st.session_state.case_result = None
if "screen" not in st.session_state:
    st.session_state.screen = "upload"


def go(screen: str):
    st.session_state.screen = screen


def sidebar_nav():
    st.sidebar.title("CivicVerify AI")
    st.sidebar.caption("The AI flags. The officer decides.")
    st.sidebar.button(
        "① New case", on_click=go, args=("upload",), use_container_width=True
    )
    st.sidebar.button(
        "⑤ Audit log", on_click=go, args=("audit",), use_container_width=True
    )


# ---------------------------------------------------------------- Screen 1
def screen_upload():
    st.header("1 · Upload")
    st.caption("Drop application, certificate, and ID for one candidate.")

    officer_id = st.text_input("Officer ID", value="officer-demo-1")
    application_form = st.file_uploader(
        "Application form", type=["png", "jpg", "jpeg", "pdf"]
    )
    certificate = st.file_uploader(
        "Academic certificate", type=["png", "jpg", "jpeg", "pdf"]
    )
    id_document = st.file_uploader("ID document", type=["png", "jpg", "jpeg", "pdf"])

    if st.button(
        "Extract & verify",
        type="primary",
        disabled=not (application_form and certificate and id_document),
    ):
        if application_form is None or certificate is None or id_document is None:
            st.error("Please upload all three documents.")
            return

        paths = {}

        for slot, upload in [
            ("application_form", application_form),
            ("certificate", certificate),
            ("id_document", id_document),
        ]:
            dest = UPLOAD_DIR / f"{slot}_{upload.name}"

            with dest.open("wb") as f:
                shutil.copyfileobj(upload, f)

            paths[slot] = str(dest)

        # Process the case here
        result = process_case(paths)

        st.session_state.case_result = result
        go("extract")
        st.rerun()


# ---------------------------------------------------------------- Screen 2
def screen_extract():
    result: CaseResult = st.session_state.case_result
    st.header("2 · Extracted fields")
    st.caption(f"Case #{result.case_id[:8]} · tap a field to edit before verifying")

    f = result.fields
    candidate_name = st.text_input("Candidate name", value=f.candidate_name or "")
    date_of_birth = st.text_input(
        "Date of birth (YYYY-MM-DD)", value=f.date_of_birth or ""
    )
    institution = st.text_input("Institution", value=f.institution or "")
    cert_no = st.text_input("Certificate no.", value=f.cert_no or "")
    issue_date = st.text_input("Issue date (YYYY-MM-DD)", value=f.issue_date or "")
    id_number = st.text_input("ID number", value=f.id_number or "")

    col1, col2 = st.columns(2)
    with col1:
        st.button("Back", on_click=go, args=("upload",))
    with col2:
        if st.button("Verify", type="primary"):
            edited = ExtractedFields(
                candidate_name=candidate_name or None,
                date_of_birth=date_of_birth or None,
                institution=institution or None,
                cert_no=cert_no or None,
                issue_date=issue_date or None,
                id_number=id_number or None,
            )
            # Re-verify against the edited fields. Simplification: we only
            # kept the merged field set (not per-document OCR output) past
            # screen 2, so this treats the edited values as the certificate
            # doc for cross-checking purposes. Good enough for the officer
            # to correct an OCR typo and re-run; if you need true per-doc
            # re-verification, extend CaseResult to carry per_doc_fields.
            new_flags = verify_case({"certificate": edited}, result.registry)
            result.fields = edited
            result.flags = new_flags
            result.memo = generate_memo(result)
            st.session_state.case_result = result
            go("verify")
            st.rerun()


# ---------------------------------------------------------------- Screens 3-4
def screen_verify():
    result: CaseResult = st.session_state.case_result
    st.header("3-4 · Verify & decide")
    st.caption(f"Risk: {result.overall_risk}")

    if not result.flags:
        st.success("No risk flags raised.")
    for flag in result.flags:
        icon = {"low": "ℹ️", "medium": "⚠️", "high": "🛑"}[flag.level]
        st.write(f"{icon} **{flag.code}** — {flag.reason}")

    if result.registry.found:
        st.info(
            f"Registry: cert {result.registry.cert_no} found, status = {result.registry.status}"
        )
    else:
        st.error(f"Registry: certificate not found")

    st.text_area("Draft memo", value=result.memo, height=100, disabled=True)

    action = st.radio(
        "Decision", ["approve", "escalate", "reject"], horizontal=True, index=1
    )
    col1, col2 = st.columns(2)
    with col1:
        st.button("Cancel", on_click=go, args=("extract",))
    with col2:
        if st.button("Save decision", type="primary"):
            save_decision(
                result.case_id,
                {
                    "officer_id": st.session_state.get("officer_id", "officer-demo-1"),
                    "action": action,
                },
            )
            st.session_state.case_result = None
            go("upload")
            st.success(f"Case {result.case_id[:8]} saved as '{action}'.")
            st.rerun()


# ---------------------------------------------------------------- Screen 5
def screen_audit():
    st.header("5 · Audit log")
    with get_session() as session:
        cases = (
            session.execute(select(Case).order_by(Case.created_at.desc()).limit(200))
            .scalars()
            .all()
        )
        rows = []
        for c in cases:
            latest = (
                sorted(c.decisions, key=lambda d: d.timestamp, reverse=True)[0]
                if c.decisions
                else None
            )
            rows.append(
                {
                    "Case": c.case_id[:8],
                    "Candidate": c.candidate_name,
                    "Institution": c.institution,
                    "Status": c.status,
                    "Decision": latest.action if latest else "—",
                    "Created": c.created_at,
                }
            )

    st.caption(f"{len(rows)} cases")
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if not df.empty:
        st.download_button(
            "Export CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="civicverify_audit.csv",
            mime="text/csv",
        )
    st.button("New case", on_click=go, args=("upload",))


# ---------------------------------------------------------------- Router
sidebar_nav()
screen = st.session_state.screen
if screen == "upload":
    screen_upload()
elif screen == "extract":
    screen_extract()
elif screen == "verify":
    screen_verify()
elif screen == "audit":
    screen_audit()
