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

1. Clone the repo and move into it.

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your OpenAI credentials:

   ```
   OPENAI_API_KEY=sk-...
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
