import sqlite3

conn = sqlite3.connect('server/homeflix.db')
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM videos')
print(f'Nombre de vidéos: {cur.fetchone()[0]}')

cur.execute('SELECT COUNT(*) FROM profiles')
print(f'Nombre de profils: {cur.fetchone()[0]}')

cur.execute('SELECT COUNT(*) FROM watch_progress')
print(f'Nombre de progressions: {cur.fetchone()[0]}')

conn.close()
