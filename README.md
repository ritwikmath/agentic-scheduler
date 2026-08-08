# Agentic RAG Query Scheduler (POC)

A proof-of-concept FastAPI service that exposes a LangChain agent over a `/chat`
endpoint. The agent answers user queries directly, or — when a request implies a
future time ("remind me at 6pm", "send this tomorrow") — schedules it as a task
in a local SQLite database instead of responding immediately.

## Features

- **Chat endpoint** (`POST /chat`) that streams the agent's response.
- **Task scheduling tool** the agent can call to defer a request, persisting it
  to `scheduler.db` (SQLite) with the task description, target datetime, and
  status.
- Powered by `langchain`'s `create_agent` with an OpenAI (`gpt-4o`) model.

## Requirements

- Python >= 3.12
- An OpenAI API key

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for virtual environment and
package management.

1. Clone the repo and move into it.

2. Install `uv` if you don't already have it:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Create the virtual environment and install dependencies:

   ```bash
   uv sync
   ```

   This creates a `.venv` (using the Python version pinned in `.python-version`)
   and installs everything listed in `requirements.txt` / `pyproject.toml`.

4. Activate the virtual environment:

   ```bash
   source .venv/bin/activate
   ```

   Alternatively, skip activation and prefix commands with `uv run` (e.g.
   `uv run fastapi dev src/agentic_rag_query_scheduler_poc/main.py`).

5. Create a `.env` file in the project root with your OpenAI credentials:

   ```
   OPENAI_API_KEY=sk-...
   ```

### Adding packages

Use `uv add <package>` instead of `pip install` so new dependencies are
recorded in `pyproject.toml`/`requirements.txt`:

```bash
uv add <package>
```

## Running the server

This project uses the FastAPI CLI (bundled via `fastapi[standard]`).

Development mode (with auto-reload):

```bash
fastapi dev src/agentic_rag_query_scheduler_poc/main.py
```

Production mode:

```bash
fastapi run src/agentic_rag_query_scheduler_poc/main.py
```

The server starts at `http://127.0.0.1:8000`, with interactive API docs at
`/docs`.

On startup, the app automatically creates a `task` table in `scheduler.db` if
it doesn't already exist.

## Usage

Send a chat message:

```bash
curl -N -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Remind me to check the deploy status tomorrow at 9am"}'
```

The response streams back as plain text chunks from the agent.

## Project structure

```
src/agentic_rag_query_scheduler_poc/
└── main.py   # FastAPI app, chat endpoint, and scheduling tool
```

## Notes

This is a POC — there is currently no worker/cron process that reads pending
rows from `scheduler.db` and actually executes them at their scheduled time;
scheduling only persists the request.
