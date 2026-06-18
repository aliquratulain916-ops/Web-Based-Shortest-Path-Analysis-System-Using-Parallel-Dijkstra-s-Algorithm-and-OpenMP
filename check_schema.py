import sqlite3

conn = sqlite3.connect('dijkstra.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

# Check schema of first table
if tables:
    table_name = tables[0][0]
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    print(f"\nColumns in {table_name}:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

conn.close()
