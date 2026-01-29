"""
Script di migrazione per aggiungere le colonne data_fattura_* alla tabella lavoro_admin
Eseguire questo script su PythonAnywhere per aggiornare il database esistente.

Istruzioni:
1. Carica questo file su PythonAnywhere (via Files o Git)
2. Apri una Bash console su PythonAnywhere
3. Esegui: python3.10 migrate_add_data_fattura_columns.py
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

def add_data_fattura_columns():
    """Aggiunge le colonne data_fattura_* alla tabella lavoro_admin"""
    db_path = find_database()
    
    if not db_path:
        print("[!] ERRORE: Database gestionale.db non trovato!")
        print("    Cerca manualmente il percorso del database e modifica lo script.")
        return False
    
    print(f"[i] Database trovato: {db_path}")
    print()
    
    # Lista delle colonne da aggiungere
    columns_to_add = [
        ('data_fattura_fe', 'DATE'),
        ('data_fattura_amin', 'DATE'),
        ('data_fattura_galvan', 'DATE'),
        ('data_fattura_fh', 'DATE'),
        ('data_fattura_bianc', 'DATE'),
        ('data_fattura_deloitte', 'DATE'),
        ('data_fattura_ext', 'DATE'),
        ('data_fattura_revisore', 'DATE'),
        ('data_fattura_caricamento', 'DATE')
    ]
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for column_name, column_type in columns_to_add:
            # Verifica se la colonna esiste già
            if column_exists(cursor, 'lavoro_admin', column_name):
                print(f"[i] Colonna {column_name} già esistente, skip...")
            else:
                try:
                    cursor.execute(f"""
                        ALTER TABLE lavoro_admin 
                        ADD COLUMN {column_name} {column_type}
                    """)
                    conn.commit()
                    print(f"[+] Colonna {column_name} aggiunta con successo")
                except Exception as e:
                    print(f"[!] Errore aggiunta {column_name}: {e}")
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
    print("Migrazione Database: Aggiunta colonne data_fattura_*")
    print("=" * 60)
    print()
    
    success = add_data_fattura_columns()
    
    if success:
        print("\n[SUCCESS] Il database è stato aggiornato correttamente!")
    else:
        print("\n[ERROR] Si sono verificati errori durante la migrazione.")
        print("Controlla i messaggi sopra per i dettagli.")
