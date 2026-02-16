"""
Migrazione: Crea la tabella changelog e aggiunge dismissed_changelog_id a user

IMPORTANTE: Questo script usa sqlite3 diretto per evitare conflitti con SQLAlchemy.

Eseguire questo script sul server PythonAnywhere:
1. Vai su PythonAnywhere Dashboard
2. Apri una Bash console
3. Vai nella directory del progetto: cd ~/fe-gestionale
4. Attiva il virtualenv: source ~/.virtualenvs/my-venv/bin/activate
5. Esegui: python migrate_add_changelog.py
"""

import sqlite3
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'instance', 'gestionale.db')

if not os.path.exists(db_path):
    print(f"[ERRORE] Database non trovato: {db_path}")
    exit(1)

print(f"Database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 1. Crea tabella changelog se non esiste
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='changelog'")
    if not cursor.fetchone():
        print("Creo la tabella changelog...")
        cursor.execute('''
            CREATE TABLE changelog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                versione VARCHAR(50) NOT NULL,
                titolo VARCHAR(200) NOT NULL,
                contenuto TEXT NOT NULL,
                data_pubblicazione DATETIME DEFAULT CURRENT_TIMESTAMP,
                attivo BOOLEAN DEFAULT 1,
                ordine INTEGER DEFAULT 0
            )
        ''')
        print("[OK] Tabella changelog creata con successo!")
    else:
        print("Tabella changelog gia' esistente")

    # 2. Aggiungi dismissed_changelog_id alla tabella user se non esiste
    cursor.execute("PRAGMA table_info(user)")
    user_columns = [row[1] for row in cursor.fetchall()]

    if 'dismissed_changelog_id' not in user_columns:
        print("Aggiungo colonna dismissed_changelog_id a user...")
        cursor.execute('ALTER TABLE user ADD COLUMN dismissed_changelog_id INTEGER DEFAULT 0')
        print("[OK] Colonna dismissed_changelog_id aggiunta!")
    else:
        print("Colonna dismissed_changelog_id gia' esistente")

    conn.commit()
    print("\n[OK] Migrazione completata con successo!")

except Exception as e:
    conn.rollback()
    print(f"[ERRORE] Errore durante la migrazione: {e}")
    import traceback
    traceback.print_exc()
    raise
finally:
    conn.close()
