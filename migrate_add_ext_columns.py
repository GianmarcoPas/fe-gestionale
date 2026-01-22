"""
Script di migrazione per aggiungere le colonne ext_type e ext_value alla tabella lavoro_admin
Eseguire questo script su PythonAnywhere per aggiornare il database esistente.

Istruzioni:
1. Carica questo file su PythonAnywhere (via Files o Git)
2. Apri una Bash console su PythonAnywhere
3. Esegui: python3.10 migrate_add_ext_columns.py
   (sostituisci 3.10 con la versione Python del tuo ambiente)

NOTA: Questo script si connette direttamente al database senza importare l'intera app
per evitare problemi con dipendenze mancanti.
"""
import sqlite3
import os
from pathlib import Path

def find_database():
    """Trova il percorso del database gestionale.db"""
    # Prova prima nella directory corrente
    current_dir = Path.cwd()
    db_path = current_dir / 'instance' / 'gestionale.db'
    if db_path.exists():
        return str(db_path)
    
    # Prova nella root del progetto
    db_path = current_dir / 'gestionale.db'
    if db_path.exists():
        return str(db_path)
    
    # Prova in instance/
    db_path = current_dir.parent / 'instance' / 'gestionale.db'
    if db_path.exists():
        return str(db_path)
    
    return None

def column_exists(cursor, table_name, column_name):
    """Verifica se una colonna esiste già nella tabella"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def add_ext_columns():
    """Aggiunge le colonne ext_type e ext_value alla tabella lavoro_admin"""
    db_path = find_database()
    
    if not db_path:
        print("[!] ERRORE: Database gestionale.db non trovato!")
        print("    Cerca manualmente il percorso del database e modifica lo script.")
        return False
    
    print(f"[i] Database trovato: {db_path}")
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica se le colonne esistono già
        if column_exists(cursor, 'lavoro_admin', 'ext_type'):
            print("[i] Colonna ext_type gia esistente, skip...")
        else:
            try:
                cursor.execute("""
                    ALTER TABLE lavoro_admin 
                    ADD COLUMN ext_type VARCHAR(10) DEFAULT 'perc'
                """)
                conn.commit()
                print("[+] Colonna ext_type aggiunta con successo")
            except Exception as e:
                print(f"[!] Errore aggiunta ext_type: {e}")
                conn.close()
                return False
        
        if column_exists(cursor, 'lavoro_admin', 'ext_value'):
            print("[i] Colonna ext_value gia esistente, skip...")
        else:
            try:
                cursor.execute("""
                    ALTER TABLE lavoro_admin 
                    ADD COLUMN ext_value FLOAT DEFAULT 0.0
                """)
                conn.commit()
                print("[+] Colonna ext_value aggiunta con successo")
            except Exception as e:
                print(f"[!] Errore aggiunta ext_value: {e}")
                conn.close()
                return False
        
        conn.close()
        print("\n[OK] Migrazione completata con successo!")
        print("Ora puoi riavviare la tua web app su PythonAnywhere.")
        return True
        
    except Exception as e:
        print(f"[!] ERRORE durante la connessione al database: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Migrazione Database: Aggiunta colonne ext_type e ext_value")
    print("=" * 60)
    print()
    
    success = add_ext_columns()
    
    if success:
        print("\n[SUCCESS] Il database e stato aggiornato correttamente!")
    else:
        print("\n[ERROR] Si sono verificati errori durante la migrazione.")
        print("Controlla i messaggi sopra per i dettagli.")
