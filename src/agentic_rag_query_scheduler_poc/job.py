import sqlite3
from itertools import batched

DB_PATH = "scheduler.db"

conn = sqlite3.connect(DB_PATH)

cur = conn.cursor()

res = cur.execute("SELECT task FROM task WHERE schedule_at < datetime('now') and status = 'pending'")

rows = res.fetchall()

for batch in batched(rows, 10):
    for row in list(batch):
        print(row[0])