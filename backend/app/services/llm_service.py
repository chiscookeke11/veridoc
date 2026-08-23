"""
LLMService — local-only, via llama-cpp-python. No network calls, matching
the "External network calls: 0" target in your README.

The model is loaded once (module-level cache) and reused across requests —
loading a 3-4B GGUF per call would blow through your <60s-per-case and
<7GB-RAM targets fast.

Two required calls into the model per case, per your README:
1. extract_fields(text)              -> ExtractedFields
2. generate_memo(case_summary)       -> str
Plus one optional one your README mentions as a feature:
3. generate_applicant_reply(...)     -> str (English / Pidgin / Yoruba)

Chat templating is handled by llama-cpp-python's create_chat_completion(),
which reads the chat template baked into the GGUF's metadata.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from llama_cpp import Llama

from app.schemas import ExtractedFields

MODEL_PATH = os.getenv("CIVICVERIFY_MODEL_PATH", "models/model.Q4_K_M.gguf")
N_CTX = int(os.getenv("CIVICVERIFY_N_CTX", "4096"))  # short context, per README
N_THREADS = int(os.getenv("CIVICVERIFY_N_THREADS", str(os.cpu_count() or 4)))

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


@lru_cache(maxsize=1)
def _get_llm() -> Llama:
    model_path = Path(MODEL_PATH)
    if not model_path.exists():
        raise FileNotFoundError(
            f"GGUF model not found at '{MODEL_PATH}'. Set CIVICVERIFY_MODEL_PATH or drop "
            f"a 3-4B Q4_K_M model into models/ (see README)."
        )
    return Llama(
        model_path=str(model_path),
        n_ctx=N_CTX,
        n_threads=N_THREADS,
        n_gpu_layers=0,  # CPU-only — matches the offline/8GB-laptop constraint
        verbose=False,
    )


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
        llm = _get_llm()
        response = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False,  # explicit: guarantees the dict form, not the streaming iterator
        )

        # response is always the dict form here since stream=False; Pylance's
        # static type is still the union of both possible return types, so we
        # silence the index-on-iterator warning rather than importing internal
        # llama_cpp response types that might not be stable across versions.
        message = response["choices"][0]["message"]  # type: ignore[index]
        return message.get("content") or ""


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
