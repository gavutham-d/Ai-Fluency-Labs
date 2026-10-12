# Task 6: Reliable Tool Use and Structured Outputs

This task adapts the defensive tool-calling pattern from `lab-6` to a small home-gardening helper. Its two tools look up seasonal care notes and estimate watering volume from pot size. The example data is defined locally in `tools.py`; it does not use the earlier course-fee scenario.

## Setup

From `Task/task-6`, install the dependencies:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The scripts load this folder's `.env` before importing the shared `lab-1/config.py`. For Groq, use:

```env
PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
MODEL=qwen/qwen3.8-27b
```

The repository `.gitignore` excludes `.env`; do not commit API keys.

## Run

```sh
python validate.py
python inject_faults.py
python robust_agent.py
python structured_demo.py
```

The first two scripts need no model request. The robust agent and structured-output comparison require the configured provider to be reachable. `structured_demo.py` reports provider errors for JSON or JSON Schema modes it cannot support.

## Design

`tools.py` defines the two functions, OpenAI tool declarations, and one `SCHEMAS` dictionary. The declarations are generated from those same schemas, and `validate.py` checks tool arguments against them before execution. `robust_agent.py` parses, resolves, validates, and executes each call, returning errors as tool messages identified by `tool_call_id`. It handles all calls in a response, retries truncated replies with larger `max_tokens`, stops repeated identical calls, and enforces a step limit.

`inject_faults.py` constructs malformed calls directly, without asking a model to produce them. `structured_demo.py` asks one extraction question without constraints, in JSON mode, and in strict schema mode. The detailed observations and reliability discussion are in `analysis.md`.
