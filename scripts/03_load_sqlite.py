"""Load the cleaned CSV into a SQLite DB so the project uses real SQL,
not just pandas, matching the SQL skill expected for a BI/data-analyst role.
"""
import sqlite3
import pandas as pd

CLEAN_PATH = "/home/claude/ecommerce_project/data/orders_clean.csv"
DB_PATH = "/home/claude/ecommerce_project/data/ecommerce.db"

df = pd.read_csv(CLEAN_PATH, parse_dates=["order_date"])

conn = sqlite3.connect(DB_PATH)
df.to_sql("orders", conn, if_exists="replace", index=False)
conn.execute("CREATE INDEX idx_country ON orders(country)")
conn.execute("CREATE INDEX idx_category ON orders(category)")
conn.execute("CREATE INDEX idx_date ON orders(order_date)")
conn.commit()

cur = conn.execute("SELECT COUNT(*) FROM orders")
print(f"Loaded {cur.fetchone()[0]:,} rows into {DB_PATH} (table: orders)")
conn.close()
