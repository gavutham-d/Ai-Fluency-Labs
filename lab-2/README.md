# Lab 2: Exploring AI Assistants

This folder contains small Python programs that show different ways an AI assistant can answer questions.

The examples use a college course-fee scenario with three courses:

- `CS101`: Rs. 12,000
- `AI202`: Rs. 18,000
- `DS303`: Rs. 15,000

You can compare a plain chatbot, fixed rules, an AI agent with tools, and a few reasoning techniques.

## What You Need

- Python 3.9 or newer
- An internet connection if you use Groq or Hugging Face
- Or Ollama installed locally if you want to run a local model

## Setup

1. Open a terminal in this directory.
2. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   On Windows, activate it with:

   ```bat
   .venv\\Scripts\\activate
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a file named `.env` in this directory. Choose one provider below.

### Option A: Groq

```dotenv
PROVIDER=groq
GROQ_API_KEY=put_your_groq_key_here
MODEL=openai/gpt-oss-20b
```

### Option B: Hugging Face

```dotenv
PROVIDER=huggingface
HF_TOKEN=put_your_huggingface_token_here
MODEL=openai/gpt-oss-20b
```

### Option C: Ollama

Install and start Ollama, then download a model such as `qwen2.5:1.5b`:

```bash
ollama pull qwen2.5:1.5b
```

Use this `.env` configuration:

```dotenv
PROVIDER=ollama
MODEL=qwen2.5:1.5b
```

Never share API keys or commit them to source control. Keep real keys only in `.env`.

## Check Your Setup

Run this first:

```bash
python check_setup.py
```

A successful check prints your Python version, provider, model, and a response from the model.

## Run the Examples

Run any example from the terminal:

```bash
python chatbot.py
python workflow.py
python agent.py
python cot_compare.py
python self_consistency.py
python react_trace.py
python challenge.py
```

The programs do the following:

| File | Purpose |
| --- | --- |
| `check_setup.py` | Checks Python, configuration, and model access. |
| `config.py` | Loads settings and stores the example course data and questions. |
| `chatbot.py` | Sends questions to a plain LLM without course-data tools. |
| `workflow.py` | Uses fixed Python rules without an LLM. |
| `agent.py` | Lets an LLM choose tools for looking up fees and doing arithmetic. |
| `tools.py` | Defines the fee lookup and safe calculator used by the agent. |
| `cot_compare.py` | Compares direct answers with step-by-step prompts. |
| `self_consistency.py` | Repeats a reasoning prompt and selects the most common answer. |
| `react_trace.py` | Shows the agent's actions and tool results. |
| `challenge.py` | Tests a question that the fixed workflow was not designed to answer. |

## Main Ideas

- A plain LLM may not know private or local data.
- A rule-based workflow is predictable but can only handle cases that were programmed.
- An agent can use tools to retrieve data and calculate answers.
- Repeating an answer can help compare consistency, but it does not guarantee correctness.

## Common Problems

- **Missing API key:** Check that the selected provider's key is present in `.env`.
- **Unknown provider:** Use exactly `ollama`, `groq`, or `huggingface` for `PROVIDER`.
- **Ollama connection error:** Make sure Ollama is running and the model named in `MODEL` is installed.
- **Model not found:** Check that the model name is supported by your selected provider.
- **Unexpected answers:** LLM responses can vary. The rule-based workflow and tool outputs are easier to inspect.
