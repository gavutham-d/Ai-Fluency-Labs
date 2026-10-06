# AI Fluency Lab 3: ReAct Agents and Context Limits

This lab builds a simple ReAct-style college assistant that can read web pages or local files and perform arithmetic. It then demonstrates how large tool observations and repeated tool calls can cause problems, and adds guards to limit those risks.

## Files

- `my_agent.py` — baseline ReAct agent. It parses model-generated tool calls and stops after a maximum number of steps, but intentionally has no repeat-call, observation-size, or total-context guard.
- `my_agent_fixed.py` — guarded version with repeated-call detection, a maximum tool-result size, and a total character budget.
- `my_tools.py` — calculator and page-reading tools. The calculator evaluates basic arithmetic expressions; the reader supports HTTP(S) pages and local HTML or text files.
- `notice.html` — sample fee notice used by the agent exercises.
- `make_big_page.py` — generates `big.html`, a large attendance-register page for testing context limits.
- `big.html` — generated large-page sample, containing 3,000 student rows.
- `requirements.txt` — dependencies for the LLM client, environment configuration, and HTTP page reader.

## Requirements and setup

- Python 3.10 or newer
- Ollama running locally, or credentials for a supported hosted provider

Create a virtual environment and install the dependencies from this directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The agents import the shared client, model, and provider settings from `lab-1/config.py`. Configure the provider and model using the setup instructions in [lab-1/README.md](../lab-1/README.md). The shared config defaults to Ollama at `http://localhost:11434/v1` with model `qwen2.5:1.5b`.

## Generate the large test page

From this directory, run:

```bash
python make_big_page.py
```

This overwrites `big.html` in the current directory with a page containing 3,000 generated attendance rows.

## Agent demos

The intended comparison is to run the baseline and guarded agents with the same requests: read `notice.html` to answer a fee question, try a missing file, and inspect `big.html`. The guarded agent should constrain repeated calls and large observations.

**Current path issue:** the agent scripts still refer to folders named `Day_1` and `Day_3`, but this repository uses `lab-1` and `lab-3`. As written, the agents cannot import `config`; their example questions also use `Day_3/...` paths that do not match these files. Update those references to the actual folder/file paths before running `my_agent.py` or `my_agent_fixed.py`.

## What to observe

- `read_webpage` strips HTML tags and script/style contents, normalizes whitespace, and limits each result to 2,000 characters by default.
- The calculator evaluates arithmetic with a restricted AST rather than executing arbitrary Python code.
- The baseline can keep sending oversized or repeated observations until it reaches its step limit.
- The guarded agent truncates individual observations, stops repeated identical tool calls, and enforces a character budget for message content.