import sqlite3
from pathlib import Path

db1 = Path('data/homeone.db')
db2 = Path('server/homeflix.db')

print(f'data/homeone.db exists: {db1.exists()}')
print(f'server/homeflix.db exists: {db2.exists()}')

if db2.exists():
    conn = sqlite3.connect(db2)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM profiles')
    print(f'Profiles in server/homeflix.db: {cur.fetchone()[0]}')
    cur.execute('SELECT name FROM profiles')
    print(f'  Names: {[r[0] for r in cur.fetchall()]}')
    conn.close()

if db1.exists():
    conn = sqlite3.connect(db1)
    cur = conn.cursor()
    try:
        cur.execute('SELECT COUNT(*) FROM profiles')
        print(f'Profiles in data/homeone.db: {cur.fetchone()[0]}')
        cur.execute('SELECT name FROM profiles')
        print(f'  Names: {[r[0] for r in cur.fetchall()]}')
    except:
        print('  (table profiles not found)')
    conn.close()
