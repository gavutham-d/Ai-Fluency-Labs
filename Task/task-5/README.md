# Task 5: Model Serving and Prompt Defaults

This example uses a camping helper called TrailMate. Ollama is not installed in the current environment, so `groq_demo.py` runs the prompts using the Groq credentials in `.env` and records real request timings. The `Modelfile` is retained as an Ollama configuration example, but Groq does not load it or expose local model-residency information; see `analysis.md` for the distinction and measured results.

## Run with Groq

The task `.env` should contain `PROVIDER=groq`, `GROQ_API_KEY`, and optionally `MODEL`. The script loads that file directly and never prints the key. Install dependencies and run from this directory:

```sh
python -m pip install -r requirements.txt
python groq_demo.py
```

The script makes a non-streaming request, streams three prompts, repeats one prompt, and tests a different system prompt. It reports completion tokens per second, streaming time to first token (TTFT), and total wall time. The Groq-hosted service does not expose Ollama `/api/ps` or `load_duration` data, so local residency and cold/warm loading cannot be measured in this run.

For a non-streaming response, token delivery is buffered, so TTFT is reported as not available. Streaming TTFT is measured from before the HTTP request until the first non-empty text arrives. Streaming completion-token usage is requested from Groq; token throughput is calculated over time after TTFT. Very short responses can make this rate sensitive to timing precision.

## Analysis

`analysis.md` contains the concepts, the measured Groq comparison table, the interpretation of TTFT and repeated-run timings, and the explanation of why PagedAttention and continuous batching suit shared vLLM deployments. It also records which requested Ollama observations remain unavailable from Groq.
