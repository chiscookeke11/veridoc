"""
LLMService - local-only, via the QVAC SDK (see qvac_runtime.py). No network
calls at inference time, matching the "External network calls: 0" target.

The model is loaded once and reused across requests (qvac_runtime keeps it
resident) - loading per call would blow through the <60s-per-case target.

Two required calls into the model per case, per your README:
1. extract_fields(text)              -> ExtractedFields
2. generate_memo(case_summary)       -> str
Plus one optional one your README mentions as a feature:
3. generate_applicant_reply(...)     -> str (English / Pidgin / Yoruba)

Swap point: everything model-specific lives in _chat() and qvac_runtime.py.
"""

from __future__ import annotations

import json

from app.schemas import ExtractedFields
from app.services.qvac_runtime import get_runtime

_EXTRACTION_SYSTEM = """You extract structured candidate fields from noisy OCR text \
of Nigerian academic/ID documents. Respond with ONLY a JSON object, nothing else — \
no markdown fences, no explanation, no leading or trailing text. Exact shape:

{"candidate_name": string or null, "date_of_birth": string or null (ISO YYYY-MM-DD if you can tell), \
"institution": string or null, "cert_no": string or null, "issue_date": string or null (ISO date), \
"id_number": string or null, "expiry_date": string or null (ISO date, only for ID documents)}

If a field is missing or illegible, use null. Never invent a value you don't see in the text."""

_MEMO_SYSTEM = """You draft a short, neutral officer memo (2-4 sentences) summarizing a \
document verification case for a Nigerian civil service / education officer. State what \
was checked, list the risk flags plainly, and suggest a next step for the applicant if \
relevant. Output only the memo text — no preamble, no sign-off."""

_REPLY_SYSTEM_TEMPLATE = """You draft a short, polite reply to a job/school applicant in \
{language}, explaining what needs clarifying about their submitted documents based on the \
case summary given. 2-3 sentences. Respectful, plain language, no jargon. Output only the \
reply text."""


def _get_llm():
    """Warm the model (kept so test_timing.py can still pre-load before timing)."""
    return get_runtime().warmup_llm()


class LLMService:
    def extract_fields(self, text: str) -> ExtractedFields:
        if not text.strip():
            return ExtractedFields()

        raw = self._chat(
            _EXTRACTION_SYSTEM, text[:4000], max_tokens=300, temperature=0.0
        )
        data = _parse_json_loose(raw)
        return ExtractedFields(
            **{k: v for k, v in data.items() if k in ExtractedFields.model_fields}
        )

    def generate_memo(self, case_summary: str) -> str:
        return self._chat(
            _MEMO_SYSTEM, case_summary, max_tokens=200, temperature=0.4
        ).strip()

    def generate_applicant_reply(
        self, case_summary: str, language: str = "English"
    ) -> str:
        system = _REPLY_SYSTEM_TEMPLATE.format(language=language)
        return self._chat(system, case_summary, max_tokens=200, temperature=0.4).strip()

    def _chat(self, system: str, user: str, max_tokens: int, temperature: float) -> str:
        return get_runtime().chat(
            system, user, max_tokens=max_tokens, temperature=temperature
        )


def _parse_json_loose(raw: str) -> dict:
    """
    Small local models are less reliable than a hosted API about sticking to
    'JSON only' instructions. Try a straight parse first; if that fails,
    find the first balanced {...} block by brace-counting and parse that.
    """
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    start = raw.find("{")
    if start == -1:
        return {}

    depth = 0
    for i in range(start, len(raw)):
        if raw[i] == "{":
            depth += 1
        elif raw[i] == "}":
            depth -= 1
            if depth == 0:
                candidate = raw[start : i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    return {}
    return {}