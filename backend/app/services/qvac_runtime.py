"""
QvacRuntime - one place that owns the QVAC SDK connection for CivicVerify.

Why this file exists
--------------------
The QVAC Python SDK is asyncio-native, but CivicVerify's pipeline (Workflow,
LLMService, OCRService, Streamlit) is plain synchronous code. This module runs
ONE asyncio event loop on a background thread, keeps ONE QVAC Client alive, and
exposes small blocking methods:

    get_runtime().ocr_blocks(image_path) -> list of OCR blocks
    get_runtime().ocr_text(image_path)   -> str  (blocks in reading order)
    get_runtime().chat(system, user, max_tokens=..., temperature=...) -> str

Models are loaded lazily on first use and then reused, exactly like the old
lru_cache'd llama-cpp model (loading per call would blow the 60 s target).

Environment variables (all optional)
------------------------------------
CIVICVERIFY_QVAC_MODEL   Name of a model constant in tetherto.qvac_sdk.models
                         (default: QWEN3_1_7B_INST_Q4)
CIVICVERIFY_MODEL_PATH   Path to a local .gguf. If it exists it is used instead
                         of the registry download (handy when the registry times
                         out on your network). See the note in _ensure_llm().
CIVICVERIFY_N_CTX        Context size (default 4096)
CIVICVERIFY_NO_THINK     "1" (default) appends Qwen3's /no_think switch so the
                         model skips its reasoning preamble. "0" disables it.
QVAC_CACHE_DIR           Absolute path where QVAC stores downloaded models.
"""

from __future__ import annotations

import asyncio
import atexit
import logging
import os
import re
import threading
from pathlib import Path
from typing import Any

log = logging.getLogger("civicverify.qvac")

LLM_CONSTANT = os.getenv("CIVICVERIFY_QVAC_MODEL", "QWEN3_1_7B_INST_Q4")
LOCAL_MODEL_PATH = os.getenv("CIVICVERIFY_MODEL_PATH", "")
N_CTX = int(os.getenv("CIVICVERIFY_N_CTX", "4096"))
NO_THINK = os.getenv("CIVICVERIFY_NO_THINK", "1") != "0"

# Copied from the QVAC OCR docs example (English / Latin script).
OCR_CONFIG: dict[str, Any] = {
    "langList": ["en"],
    "magRatio": 1.5,
    "defaultRotationAngles": [90, 180, 270],
    "contrastRetry": False,
    "lowConfidenceThreshold": 0.5,
    "recognizerBatchSize": 1,
}

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def _strip_think(text: str) -> str:
    """Remove <think>...</think> blocks (and a dangling unclosed one)."""
    text = _THINK_RE.sub("", text)
    if "<think>" in text:
        text = text.split("<think>")[0]
    return text.strip()


def _progress_logger():
    last = {"pct": -1}

    def _cb(p) -> None:
        try:
            pct = int(p.percentage)
        except Exception:
            return
        if pct != last["pct"]:
            last["pct"] = pct
            log.info("QVAC model download %d%%", pct)

    return _cb


# --------------------------------------------------------------------------
# OCR block ordering
# --------------------------------------------------------------------------
def _geometry(block) -> tuple[float, float, float] | None:
    """Return (top_y, left_x, height) or None if the block has no usable bbox.

    Handles either a flat [x1, y1, x2, y2] box or a list of corner points.
    Run test_qvac_smoke.py once and check the printed bbox matches this.
    """
    bbox = getattr(block, "bbox", None)
    if not bbox:
        return None
    try:
        if isinstance(bbox[0], (list, tuple)):
            xs = [float(p[0]) for p in bbox]
            ys = [float(p[1]) for p in bbox]
            x0, y0, y1 = min(xs), min(ys), max(ys)
        else:
            x0, y0, _x1, y1 = (float(v) for v in bbox[:4])
        return (y0, x0, abs(y1 - y0))
    except Exception:
        return None


def blocks_to_text(blocks: list) -> str:
    """Join OCR blocks into text, top-to-bottom then left-to-right.

    Blocks on the same visual line are joined with a space so that a label and
    its value ("Name:" "ADEBAYO ...") stay together for the LLM extractor.
    If geometry is unavailable we fall back to the order the engine returned.
    """
    texts = [(b, (getattr(b, "text", "") or "").strip()) for b in blocks]
    texts = [(b, t) for b, t in texts if t]
    if not texts:
        return ""

    geo = [(_geometry(b), t) for b, t in texts]
    if any(g is None for g, _ in geo):
        return "\n".join(t for _, t in texts)

    heights = sorted(g[2] for g, _ in geo if g[2] > 0)
    median_h = heights[len(heights) // 2] if heights else 10.0
    tol = max(median_h * 0.6, 5.0)

    ordered = sorted(geo, key=lambda item: (item[0][0], item[0][1]))
    lines: list[list[tuple[float, str]]] = []
    line_y = None
    for (y, x, _h), t in ordered:
        if line_y is None or abs(y - line_y) > tol:
            lines.append([])
            line_y = y
        lines[-1].append((x, t))
    return "\n".join(" ".join(t for _, t in sorted(line)) for line in lines)


# --------------------------------------------------------------------------
# The runtime
# --------------------------------------------------------------------------
class QvacRuntime:
    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._loop.run_forever, name="qvac-loop", daemon=True
        )
        self._thread.start()

        self._client: Any = None
        self._t: Any = None  # client.transport
        self._llm_id: str | None = None
        self._ocr_id: str | None = None
        self._llm_name = LLM_CONSTANT
        self._gen_params_ok = True

        # asyncio locks must be created on the loop that uses them
        self._load_lock: asyncio.Lock
        self._infer_lock: asyncio.Lock
        self._run(self._make_locks())

        atexit.register(self.close)

    # ---- plumbing ---------------------------------------------------------
    async def _make_locks(self) -> None:
        self._load_lock = asyncio.Lock()
        self._infer_lock = asyncio.Lock()

    def _run(self, coro, timeout: float | None = None):
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result(timeout)

    async def _connect(self) -> None:
        if self._t is not None:
            return
        from tetherto.qvac_sdk import Client

        self._client = Client()
        await self._client.__aenter__()
        self._t = self._client.transport
        log.info("QVAC client connected")

    # ---- model loading ----------------------------------------------------
    async def _ensure_llm(self) -> str:
        async with self._load_lock:
            await self._connect()
            if self._llm_id is None:
                from tetherto.qvac_sdk import load_model

                kwargs: dict[str, Any] = {
                    "model_config": {"ctx_size": N_CTX},
                    "on_progress": _progress_logger(),
                }
                local = Path(LOCAL_MODEL_PATH) if LOCAL_MODEL_PATH else None
                if local and local.exists():
                    # UNVERIFIED: a plain path needs an explicit model type.
                    # "llamacpp-completion" is the canonical name the SDK prints
                    # in its own error messages for llama.cpp text models.
                    log.info("Loading local model %s", local)
                    self._llm_id = await load_model(
                        self._t,
                        model_src=str(local),
                        model_type="llamacpp-completion",
                        **kwargs,
                    )
                    self._llm_name = local.name
                else:
                    from tetherto.qvac_sdk import models

                    constant = getattr(models, LLM_CONSTANT)  # AttributeError = typo in name
                    log.info("Loading registry model %s", LLM_CONSTANT)
                    self._llm_id = await load_model(self._t, model_src=constant, **kwargs)
                    self._llm_name = LLM_CONSTANT
            return self._llm_id

    async def _ensure_ocr(self) -> str:
        async with self._load_lock:
            await self._connect()
            if self._ocr_id is None:
                from tetherto.qvac_sdk import load_model
                from tetherto.qvac_sdk.models import OCR_LATIN

                log.info("Loading OCR model")
                self._ocr_id = await load_model(
                    self._t,
                    model_src=OCR_LATIN,
                    model_config=OCR_CONFIG,
                    on_progress=_progress_logger(),
                )
            return self._ocr_id

    # ---- OCR ----------------------------------------------------------------
    async def _ocr_blocks(self, image_path: str) -> list:
        from tetherto.qvac_sdk import OcrStreamRequest, ocr_stream

        model_id = await self._ensure_ocr()
        request = OcrStreamRequest.model_validate(
            {
                "type": "ocrStream",
                "modelId": model_id,
                "image": {"type": "filePath", "value": image_path},
                "options": {"paragraph": False},
            }
        )
        blocks: list = []
        async with self._infer_lock:
            async for response in ocr_stream(self._t, request):
                blocks.extend(response.blocks or [])
        return blocks

    def ocr_blocks(self, image_path: str) -> list:
        return self._run(self._ocr_blocks(str(Path(image_path).resolve())))

    def ocr_text(self, image_path: str) -> str:
        return blocks_to_text(self.ocr_blocks(image_path))

    # ---- LLM ----------------------------------------------------------------
    def _start_completion(self, history: list[dict], max_tokens: int, temperature: float):
        from tetherto.qvac_sdk import completion

        if self._gen_params_ok:
            try:
                # UNVERIFIED kwarg name. The JS SDK calls it generationParams
                # ({ temp, predict }); the Python wrapper should be
                # generation_params. If your SDK version differs we fall back to
                # defaults and say so in the log. Check the real signature with:
                #   python -c "import inspect, tetherto.qvac_sdk as q; print(inspect.signature(q.completion))"
                return completion(
                    self._t,
                    model_id=self._llm_id,
                    history=history,
                    generation_params={"temp": temperature, "predict": max_tokens},
                )
            except Exception as exc:  # noqa: BLE001
                self._gen_params_ok = False
                log.warning(
                    "completion() rejected generation_params (%s). Using SDK defaults; "
                    "temperature/max_tokens are NOT applied.",
                    exc,
                )
        return completion(self._t, model_id=self._llm_id, history=history)

    async def _chat(self, system: str, user: str, max_tokens: int, temperature: float) -> str:
        await self._ensure_llm()
        if NO_THINK and self._llm_name.upper().startswith("QWEN3"):
            user = f"{user}\n\n/no_think"
        history = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        parts: list[str] = []
        async with self._infer_lock:
            run = self._start_completion(history, max_tokens, temperature)
            async for event in run.events:
                if event.type == "contentDelta":
                    parts.append(event.text)
        return _strip_think("".join(parts))

    def chat(self, system: str, user: str, *, max_tokens: int = 256, temperature: float = 0.2) -> str:
        return self._run(self._chat(system, user, max_tokens, temperature))

    def warmup_llm(self) -> str:
        return self._run(self._ensure_llm())

    def warmup_ocr(self) -> str:
        return self._run(self._ensure_ocr())

    # ---- shutdown -----------------------------------------------------------
    async def _close(self) -> None:
        if self._t is None:
            return
        from tetherto.qvac_sdk import unload_model

        for mid in (self._llm_id, self._ocr_id):
            if mid:
                try:
                    await unload_model(self._t, mid)
                except Exception:  # noqa: BLE001
                    pass
        try:
            await self._client.__aexit__(None, None, None)
        except Exception:  # noqa: BLE001
            pass
        self._t = None

    def close(self) -> None:
        try:
            self._run(self._close(), timeout=15)
        except Exception:  # noqa: BLE001
            pass


_runtime: QvacRuntime | None = None
_runtime_lock = threading.Lock()


def get_runtime() -> QvacRuntime:
    global _runtime
    with _runtime_lock:
        if _runtime is None:
            _runtime = QvacRuntime()
        return _runtime