import sqlite3

conn = sqlite3.connect('homeflix.db')
cursor = conn.cursor()

# Vérifier que la table existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hidden_videos'")
print('✓ Table hidden_videos existe:', cursor.fetchone() is not None)

# Afficher les colonnes
cursor.execute('PRAGMA table_info(hidden_videos)')
print('\nColonnes:')
for row in cursor.fetchall():
    print(f'  - {row[1]} ({row[2]})')

# Vérifier les index
cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='hidden_videos'")
print('\nIndex:')
for row in cursor.fetchall():
    print(f'  - {row[0]}')

conn.close()
