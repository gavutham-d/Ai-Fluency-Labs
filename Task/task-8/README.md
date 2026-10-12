# Task 8: College Helpdesk RAG Agent

This project builds a small retrieval-augmented college helpdesk from six handbook documents. It covers document ingestion, similarity search, a relevance guard, and a tool-using agent with conversation memory.

## Contents

- `data/`: the six Markdown handbook documents, including `placement_policy.md`.
- `lc_config.py`: provider, embedding, and Chroma configuration.
- `1_ingest.py`: loads the handbook files, splits them into chunks, embeds them, and rebuilds the local Chroma index.
- `2_search.py`: runs sample vector searches and prints cosine distances and source filenames.
- `task_agent.py`: runs the helpdesk agent and its tools for the five task questions.
- `results.md`: ingestion/search evidence, relevance score evidence, and the Part D answer table.
- `run_log.txt`: terminal output from running `python task_agent.py`.
- `requirements.txt`: Python package dependencies.

## Requirements

- Python 3.10 or later.
- A model provider supported by `lc_config.py`: Groq, Hugging Face, or Ollama. Ollama is optional; the example configuration below uses Groq.
- Internet access on the first FastEmbed run to download its embedding model.

## Setup

Run these commands from this directory (`Task/task-8`):

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Create a local `.env` file in this directory. Do not commit it or share its API key. For Groq with FastEmbed, configure:

```env
PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
MODEL=qwen/qwen3.8-27b
EMBED_PROVIDER=fastembed
EMBED_MODEL=BAAI/bge-small-en-v1.5
```

The repository `.gitignore` excludes `.env` and `chroma_db/`. The Chroma index is generated locally by ingestion and is not part of the submission.

## Run the Workflow

Run these commands from `Task/task-8`:

```sh
python 1_ingest.py
python 2_search.py
python task_agent.py
```

`1_ingest.py` reads all `data/*.md` files, splits them into 300-character chunks with 50-character overlap, clears and rebuilds `chroma_db/`, and stores the vectors. With the included six documents, the recorded run loaded 6 documents and created 27 chunks.

`2_search.py` prints the top three matches and their cosine distances for sample questions, including the placement eligibility question. The placement policy appears as the top result for that question.

`task_agent.py` runs five questions in the shared `task-run` thread. Its tools retrieve handbook passages, look up course fees, check attendance eligibility, and calculate totals. Follow-up questions can use the prior conversation context.

## Relevance Guard

The agent's `search_handbook` tool requests the top three results, then retains only results whose cosine distance is at most `MAX_DISTANCE` (`0.4`). If all results exceed the threshold, it returns:

```text
NO_MATCH: this is not covered in the college handbook.
```

The system prompt tells the agent to respond that it does not know when it receives `NO_MATCH`. The recorded FastEmbed scores in `results.md` are `0.185`, `0.236`, and `0.284` for the placement question, and `0.573`, `0.573`, and `0.577` for the France question. The chosen threshold retains the placement results and filters the unrelated France results.

## Evidence

See `results.md` for the captured ingestion and search outputs, measured threshold evidence, and the five-question report. `run_log.txt` contains the actual terminal output from `python task_agent.py`, including tool calls and answers.
