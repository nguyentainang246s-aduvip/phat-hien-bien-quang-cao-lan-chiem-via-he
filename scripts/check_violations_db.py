import sqlite3
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('data/surveillance.db')
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", c.fetchall())

try:
    c.execute("SELECT date(timestamp), count(*) FROM violations GROUP BY date(timestamp)")
    print("Violations by date(timestamp):", c.fetchall())
except Exception as e:
    print("Error querying date(timestamp):", e)

c.execute("SELECT count(*) FROM violations")
print("Total violations:", c.fetchone()[0])

c.execute("PRAGMA table_info(violations)")
print("Columns:", [col[1] for col in c.fetchall()])

c.execute("SELECT id, timestamp, camera_id, status FROM violations ORDER BY id DESC LIMIT 10")
print("Recent records:")
for r in c.fetchall():
    print(" ", r)

