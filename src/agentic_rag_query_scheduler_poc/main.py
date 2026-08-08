import sqlite3
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

load_dotenv()

DB_PATH = "scheduler.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                schedule_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                result TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@tool
def schedule_task(task: str, schedule_at: datetime):
    """Schedules a customer request to be exected later.

    Use this tool when user asks
    - Scheudle a query to be executed later
    - User wants a information at specific time in future
    - User wants delay the response

    Do not use this tool when
    - User wants something immediate
    - User does not want to deplay response

    args:
    - task: a string containing stripped down version of user query without noise
    - schedule_at: date and time suitable for SQL database DateTime column

    Returns:
    - true if schedule is successful
    - false if error occured during schedule
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO task (task, schedule_at) VALUES (?, ?)",
            (task, schedule_at.isoformat()),
        )
        conn.commit()
        return True
    except sqlite3.Error as ex:
        print(ex)
        return False
    finally:
        conn.close()


prompt = PromptTemplate.from_template("You are a helpful assistant. Current date and time is {curr_date_time}")

system_prompt = prompt.format(curr_date_time=(datetime.now(UTC)).strftime("%Y-%m-%d %H:%M:%S"))

agent = create_agent(
    model="openai:gpt-4o", tools=[schedule_task], system_prompt=system_prompt
)


class Message(BaseModel):
    message: str

@app.post("/chat")
async def chat(input: Message):
    user_input = input.message.strip()

    async def event_stream():
        async for chunk in agent.astream({"messages": [{"role": "user", "content": user_input}]}):
            for update in chunk.values():
                message = update["messages"][-1]
                yield f"{message.content}\n"

    return StreamingResponse(event_stream(), media_type="text/plain")
