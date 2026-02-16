"""
Migrazione: Crea la tabella note_admin e aggiunge last_seen_note_id a user

IMPORTANTE: Questo script usa sqlite3 diretto per evitare conflitti con SQLAlchemy
quando la colonna last_seen_note_id non esiste ancora.

Eseguire questo script sul server PythonAnywhere:
1. Vai su PythonAnywhere Dashboard
2. Apri una Bash console
3. Vai nella directory del progetto: cd ~/fe-gestionale
4. Attiva il virtualenv: source ~/.virtualenvs/my-venv/bin/activate
5. Esegui: python migrate_create_note_admin_table.py
"""

import sqlite3
import os

# Determina il percorso del database
# PythonAnywhere: ~/fe-gestionale/instance/gestionale.db
# Locale: instance/gestionale.db
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, 'instance', 'gestionale.db')

if not os.path.exists(db_path):
    print(f"[ERRORE] Database non trovato: {db_path}")
    exit(1)

print(f"Database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 1. Crea tabella note_admin se non esiste
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='note_admin'")
    if not cursor.fetchone():
        print("Creo la tabella note_admin...")
        cursor.execute('''
            CREATE TABLE note_admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenuto TEXT NOT NULL,
                autore_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (autore_id) REFERENCES user(id)
            )
        ''')
        print("[OK] Tabella note_admin creata con successo!")
    else:
        print("Tabella note_admin gia' esistente")

    # 2. Aggiungi last_seen_note_id alla tabella user se non esiste
    cursor.execute("PRAGMA table_info(user)")
    user_columns = [row[1] for row in cursor.fetchall()]

    if 'last_seen_note_id' not in user_columns:
        print("Aggiungo colonna last_seen_note_id a user...")
        cursor.execute('ALTER TABLE user ADD COLUMN last_seen_note_id INTEGER DEFAULT 0')
        print("[OK] Colonna last_seen_note_id aggiunta!")
    else:
        print("Colonna last_seen_note_id gia' esistente")

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
