"""
Script di migrazione per aggiungere la colonna categoria alla tabella lavoro_admin
Eseguire questo script per aggiornare il database esistente.

Istruzioni:
1. Assicurati di essere nella directory del progetto
2. Esegui: python migrate_add_categoria_column.py
   (o python3 a seconda del tuo sistema)

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

def add_categoria_column():
    """Aggiunge la colonna categoria alla tabella lavoro_admin"""
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
        
        # Verifica se la colonna esiste già
        if column_exists(cursor, 'lavoro_admin', 'categoria'):
            print("[i] Colonna categoria già esistente, skip...")
        else:
            try:
                cursor.execute("""
                    ALTER TABLE lavoro_admin 
                    ADD COLUMN categoria VARCHAR(20)
                """)
                conn.commit()
                print("[+] Colonna categoria aggiunta con successo")
            except Exception as e:
                print(f"[!] Errore aggiunta categoria: {e}")
                conn.close()
                return False
        
        conn.close()
        print("\n[OK] Migrazione completata con successo!")
        print("Ora puoi riavviare la tua web app.")
        return True
        
    except Exception as e:
        print(f"[!] ERRORE durante la connessione al database: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Migrazione Database: Aggiunta colonna categoria")
    print("=" * 60)
    print()
    
    success = add_categoria_column()
    
    if success:
        print("\n[SUCCESS] Il database è stato aggiornato correttamente!")
    else:
        print("\n[ERROR] Si sono verificati errori durante la migrazione.")
        print("Controlla i messaggi sopra per i dettagli.")
