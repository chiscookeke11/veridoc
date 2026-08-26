"""
Measures raw generation throughput (tokens/sec) — the actual metric ADTC's
Sperf score uses, distinct from our earlier end-to-end process_case()
timing (which includes OCR, not just LLM generation).

Run: uv run python tps_benchmark.py
"""
import time
from app.services.llm_service import _get_llm

llm = _get_llm()  # excluded from timing — one-time load cost, not generation speed

prompt = "Summarize in one sentence why offline document verification matters."

start = time.time()
response = llm.create_chat_completion(
    messages=[{"role": "user", "content": prompt}],
    max_tokens=200,
    temperature=0.4,
)
elapsed = time.time() - start

completion_tokens = response.get("usage", {}).get("completion_tokens")
if completion_tokens:
    tps = completion_tokens / elapsed
    print(f"Generated {completion_tokens} tokens in {elapsed:.2f}s")
    print(f"Throughput: {tps:.2f} tokens/sec")
else:
    print(f"Elapsed: {elapsed:.2f}s (token count not reported by this llama-cpp-python version)")
    print("Response:", response["choices"][0]["message"]["content"])