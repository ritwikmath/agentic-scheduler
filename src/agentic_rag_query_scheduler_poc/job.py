import asyncio
import sqlite3
from pathlib import Path
import aiohttp

DB_PATH = Path(__file__).resolve().parent.parent.parent / "scheduler.db"


async def process_query(id: int, query: str):
    url = "http://localhost:8000/chat"

    payload = {
        "message": query
    }

    async with aiohttp.ClientSession() as session, session.post(
        url,
        json=payload,
    ) as response:
        print("Status:", response.status)
        print("Response:", await response.text())


async def worker(queue: asyncio.Queue) -> str:
    while True:
        item = await queue.get()
        try:
            id, query = item
            await process_query(id, query)
        except Exception as ex:
            print(ex)
        finally:
            queue.task_done()


def fetch_pending_queries():
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        res = cur.execute("SELECT id, task FROM task WHERE schedule_at < datetime('now') and status = 'pending'")
        rows = res.fetchall()
        return rows
    except Exception as ex:
        print(ex)
    finally:
        conn.close()


async def main():
    queue = asyncio.Queue()

    workers = [asyncio.create_task(worker(queue)) for _ in range(5)]

    rows = fetch_pending_queries()

    for row in rows:
        await queue.put(row)

    await queue.join()

    for w in workers:
        w.cancel()


if __name__ == "__main__":
    asyncio.run(main())