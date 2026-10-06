# AI Fluency Lab 6: Reliable Tool Use

Lab 6 explores how to make LLM tool calling more reliable. It demonstrates strict argument validation, defensive handling of malformed tool calls, retry limits, and structured JSON output.

## Files

- `robust_agent.py` — runs a college-fee assistant that validates tool calls, handles failures, detects repeated calls, and limits the number of steps.
- `tools_v2.py` — defines the course-fee and arithmetic tools, their JSON schemas, and the functions they call.
- `validate.py` — checks tool arguments against required fields, types, allowed values, and extra-argument rules. It also includes a small validation demo.
- `inject_faults.py` — sends deliberately malformed and invalid tool calls through the defensive handler without calling an LLM.
- `structured_demo.py` — compares free-text, JSON mode, and JSON Schema constrained responses from the configured model.
- `requirements.txt` — Python packages used by the lab.

## Requirements

- Python 3.10 or newer
- The packages listed in `requirements.txt`
- An LLM provider configured through the shared `lab-1/config.py` for `robust_agent.py` and `structured_demo.py`

The API demos use the provider configuration in Lab 1. By default this is Ollama at `http://localhost:11434/v1`; alternatively, configure Groq or Hugging Face in a `.env` file in the `lab-6` directory. The selected provider must support the API features used by the demo; `structured_demo.py` reports when a response format is unsupported.

## Setup

From this directory, create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The default Ollama configuration uses the `qwen2.5:1.5b` model. Start Ollama and ensure that model is available before running the API demos. To use a hosted provider, create `.env` in this directory instead. For Groq:

```env
PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
MODEL=openai/gpt-oss-20b
```

For Hugging Face, use `PROVIDER=huggingface`, set `HF_TOKEN`, and optionally set `MODEL`. The model name defaults to `openai/gpt-oss-20b`. These settings are read by the shared configuration in `lab-1`.

## Run the demos

Run the following commands from the `lab-6` directory with the virtual environment active.

### Local validation and fault handling

These demos do not make model API calls:

```bash
python validate.py
python inject_faults.py
```

`validate.py` prints validation results for sample argument objects. `inject_faults.py` tests malformed JSON, unknown tools, missing or incorrectly typed arguments, invalid values, unexpected arguments, unknown course codes, and unsafe calculator expressions. The handler returns error strings instead of raising for those cases.

### Model-backed demos

These commands require the configured provider to be reachable:

```bash
python robust_agent.py
python structured_demo.py
```

`robust_agent.py` exercises validated tool calls and bounded retry behavior. `structured_demo.py` sends the same question using unconstrained output, JSON mode, and strict JSON Schema mode; support for these modes depends on the provider and model.

## Notes

- Course fees and supported course codes are example data defined in `tools_v2.py`.
- The calculator accepts basic arithmetic only; it does not evaluate arbitrary Python expressions.
- API credentials should be kept in `.env` and not committed to version control.