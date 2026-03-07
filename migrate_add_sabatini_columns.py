"""
Script di migrazione per aggiungere le colonne Nuova Sabatini alla tabella lavoro_admin.
Eseguire questo script su PythonAnywhere per aggiornare il database esistente.

Istruzioni:
1. Carica questo file su PythonAnywhere (via Files o Git)
2. Apri una Bash console su PythonAnywhere
3. Esegui: python3.10 migrate_add_sabatini_columns.py
"""
import sqlite3
from pathlib import Path


def find_database():
    """Trova il percorso del database gestionale.db"""
    current_dir = Path.cwd()
    for candidate in [
        current_dir / 'instance' / 'gestionale.db',
        current_dir / 'gestionale.db',
        current_dir.parent / 'instance' / 'gestionale.db',
    ]:
        if candidate.exists():
            return str(candidate)
    return None


def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


COLUMNS = [
    ('has_sabatini',          'BOOLEAN DEFAULT 0'),
    ('nome_sabatini',         'VARCHAR(100)'),
    ('importo_sabatini',      'FLOAT DEFAULT 0.0'),
    ('sab_type',              "VARCHAR(10) DEFAULT 'perc'"),
    ('sab_value',             'FLOAT DEFAULT 0.0'),
    ('c_sabatini',            'FLOAT DEFAULT 0.0'),
    ('f_sabatini',            'VARCHAR(50)'),
    ('data_fattura_sabatini', 'DATE'),
]


def migrate():
    db_path = find_database()
    if not db_path:
        print("[!] ERRORE: Database gestionale.db non trovato!")
        return False

    print(f"[i] Database trovato: {db_path}\n")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for col_name, col_type in COLUMNS:
            if column_exists(cursor, 'lavoro_admin', col_name):
                print(f"[i] Colonna {col_name} gia esistente, skip...")
            else:
                try:
                    cursor.execute(f"ALTER TABLE lavoro_admin ADD COLUMN {col_name} {col_type}")
                    conn.commit()
                    print(f"[+] Colonna {col_name} aggiunta con successo")
                except Exception as e:
                    print(f"[!] Errore aggiunta {col_name}: {e}")
                    conn.close()
                    return False

        conn.close()
        print("\n[OK] Migrazione completata con successo!")
        return True

    except Exception as e:
        print(f"[!] ERRORE durante la connessione al database: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Migrazione Database: Aggiunta colonne Nuova Sabatini")
    print("=" * 60)
    print()

    success = migrate()

    if success:
        print("\n[SUCCESS] Il database e stato aggiornato correttamente!")
        print("Ora puoi riavviare la tua web app su PythonAnywhere.")
    else:
        print("\n[ERROR] Si sono verificati errori durante la migrazione.")
