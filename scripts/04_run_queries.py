"""Run every query in analysis_queries.sql against the SQLite DB,
save each result as its own CSV (for the dashboard) and print to console
(for the README write-up)."""
import sqlite3
import pandas as pd
import re
import os

DB_PATH = "/home/claude/ecommerce_project/data/ecommerce.db"
SQL_PATH = "/home/claude/ecommerce_project/sql/analysis_queries.sql"
OUT_DIR = "/home/claude/ecommerce_project/output"
os.makedirs(OUT_DIR, exist_ok=True)

with open(SQL_PATH) as f:
    content = f.read()

# split on the numbered comment headers "-- N. Title"
chunks = re.split(r"-- \d+\.\s*(.+?)\s*-{0,}\n", content)
# chunks[0] is file header/comment block before first match; then alternating title, sql
pairs = []
for i in range(1, len(chunks), 2):
    title = chunks[i].strip()
    sql = chunks[i + 1].strip()
    pairs.append((title, sql))

conn = sqlite3.connect(DB_PATH)

for idx, (title, sql) in enumerate(pairs, start=1):
    try:
        res = pd.read_sql_query(sql, conn)
    except Exception as e:
        print(f"[{idx}] FAILED: {title}\n  {e}\n")
        continue
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:50]
    out_path = os.path.join(OUT_DIR, f"q{idx:02d}_{slug}.csv")
    res.to_csv(out_path, index=False)
    print(f"[{idx}] {title}")
    print(res.to_string(index=False))
    print(f"  -> saved {out_path}\n")

conn.close()
