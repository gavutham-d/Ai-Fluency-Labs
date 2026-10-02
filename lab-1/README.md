# AI Fluency - Day 1

A small Python lab for comparing three ways to build an AI-powered college fee assistant:

1. A plain LLM chatbot with no access to private course data.
2. A rule-based workflow with predictable, hard-coded behavior.
3. An LLM agent that can call tools to look up fees and perform calculations.

The examples use the OpenAI-compatible API format, so they can run with a local Ollama model or with a cloud provider.

## Requirements

- Python 3.9 or newer
- An OpenAI-compatible model provider:
  - [Ollama](https://ollama.com/) running locally, or
  - A Groq API key, or
  - A Hugging Face access token

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project directory. The default configuration uses Ollama:

```dotenv
PROVIDER=ollama
MODEL=qwen2.5:1.5b
```

Start Ollama and download the model before running the setup check:

```bash
ollama serve
ollama pull qwen2.5:1.5b
```

### Cloud providers

To use Groq instead:

```dotenv
PROVIDER=groq
GROQ_API_KEY=your-groq-api-key
MODEL=openai/gpt-oss-20b
```

To use Hugging Face instead:

```dotenv
PROVIDER=huggingface
HF_TOKEN=your-hugging-face-token
MODEL=openai/gpt-oss-20b
```

Keep `.env` private. It is ignored by Git, and API keys should never be committed to the repository.

## Verify the setup

Run the connection check:

```bash
python check_setup.py
```

A successful run prints the selected provider and model, followed by:

```text
Model replied  : SETUP OK
```

## Run the examples

Run the plain chatbot. It sends questions to the model but does not expose the private course fee data:

```bash
python chatbot.py
```

Run the deterministic workflow. It uses regular expressions and fixed rules without calling an LLM:

```bash
python workflow.py
```

Run the tool-using agent. It can call `get_course_fee` for course lookups and `calculator` for arithmetic:

```bash
python agent.py
```

Run the challenge question, which compares the rule-based workflow and the agent on a question neither was explicitly designed for:

```bash
python challenge.py
```

You can also inspect the tools directly:

```bash
python tools.py
```

## What to observe

- **Chatbot:** The model can answer naturally, but it has no reliable way to know the private fees in `config.py`.
- **Workflow:** Known patterns are predictable and do not require a model, but unsupported question formats fall through to a fixed response.
- **Agent:** The model decides when to call tools, while Python performs the data lookup and arithmetic. The loop stops after six tool-calling steps by default.

The sample course fees are:

| Course | Fee |
| --- | ---: |
| CS101 | Rs. 12,000 |
| AI202 | Rs. 18,000 |
| DS303 | Rs. 15,000 |

## Project structure

| File | Purpose |
| --- | --- |
| `config.py` | Loads environment variables, creates the API client, and stores sample course data and questions. |
| `check_setup.py` | Checks Python configuration and verifies that the selected model responds. |
| `chatbot.py` | System 1: a plain LLM chatbot. |
| `workflow.py` | System 2: a rule-based fee workflow. |
| `agent.py` | System 3: an LLM agent with a tool-calling loop. |
| `tools.py` | Defines the fee lookup, safe calculator, and tool schemas. |
| `challenge.py` | Compares the workflow and agent on an additional budget question. |
| `requirements.txt` | Python dependencies. |

## Notes

- The project uses an OpenAI-compatible client for all three provider choices.
- The calculator intentionally supports only numbers, parentheses, and `+`, `-`, `*`, and `/`; it does not use `eval()`.
- The sample course data is local demonstration data. Update `COURSE_FEES` in `config.py` to experiment with other values.