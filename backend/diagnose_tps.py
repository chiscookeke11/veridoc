"""
Diagnostic run — verbose=True shows llama.cpp's own startup banner, which
reports whether it actually compiled with AVX2/AVX/FMA support and how
many threads it's using. A generic (non-SIMD) build or wrong thread count
would fully explain a 1-3 TPS result.

Run: uv run python diagnose_tps.py
Watch the FULL output, especially any line mentioning AVX, FMA, or "n_threads".
"""
import os
import time
from pathlib import Path
from llama_cpp import Llama

MODEL_PATH = os.getenv("CIVICVERIFY_MODEL_PATH", "models/model.Q4_K_M.gguf")

print(f"CPU count reported by Python: {os.cpu_count()}")
print(f"Loading model from: {MODEL_PATH}")
print("=" * 60)

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,
    n_threads=os.cpu_count(),
    n_gpu_layers=0,
    verbose=True,  # <-- the important change from normal operation
)

print("=" * 60)
print("Model loaded. Running generation...")

start = time.time()
response = llm.create_chat_completion(
    messages=[{"role": "user", "content": "Count from 1 to 20."}],
    max_tokens=100,
    temperature=0.0,
)
elapsed = time.time() - start

tokens = response.get("usage", {}).get("completion_tokens", "?")
print(f"\nGenerated {tokens} tokens in {elapsed:.2f}s")
if isinstance(tokens, int):
    print(f"TPS: {tokens/elapsed:.2f}")