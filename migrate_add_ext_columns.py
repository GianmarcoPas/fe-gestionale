"""
Script di migrazione per aggiungere le colonne ext_type e ext_value alla tabella lavoro_admin
Eseguire questo script su PythonAnywhere per aggiornare il database esistente.

Istruzioni:
1. Carica questo file su PythonAnywhere (via Files o Git)
2. Apri una Bash console su PythonAnywhere
3. Esegui: python3.10 migrate_add_ext_columns.py
   (sostituisci 3.10 con la versione Python del tuo ambiente)
"""
from app import create_app, db
from sqlalchemy import text, inspect

app = create_app()

def column_exists(conn, table_name, column_name):
    """Verifica se una colonna esiste già nella tabella"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def add_ext_columns():
    """Aggiunge le colonne ext_type e ext_value alla tabella lavoro_admin"""
    with app.app_context():
        with db.engine.connect() as conn:
            # Verifica se le colonne esistono già
            if column_exists(conn, 'lavoro_admin', 'ext_type'):
                print("[i] Colonna ext_type gia esistente, skip...")
            else:
                try:
                    conn.execute(text("""
                        ALTER TABLE lavoro_admin 
                        ADD COLUMN ext_type VARCHAR(10) DEFAULT 'perc'
                    """))
                    conn.commit()
                    print("[+] Colonna ext_type aggiunta con successo")
                except Exception as e:
                    print(f"[!] Errore aggiunta ext_type: {e}")
                    return False
            
            if column_exists(conn, 'lavoro_admin', 'ext_value'):
                print("[i] Colonna ext_value gia esistente, skip...")
            else:
                try:
                    conn.execute(text("""
                        ALTER TABLE lavoro_admin 
                        ADD COLUMN ext_value FLOAT DEFAULT 0.0
                    """))
                    conn.commit()
                    print("[+] Colonna ext_value aggiunta con successo")
                except Exception as e:
                    print(f"[!] Errore aggiunta ext_value: {e}")
                    return False
        
        print("\n[OK] Migrazione completata con successo!")
        print("Ora puoi riavviare la tua web app su PythonAnywhere.")
        return True

if __name__ == '__main__':
    print("=" * 50)
    print("Migrazione Database: Aggiunta colonne ext_type e ext_value")
    print("=" * 50)
    print()
    
    success = add_ext_columns()
    
    if success:
        print("\n[SUCCESS] Il database e stato aggiornato correttamente!")
    else:
        print("\n[ERROR] Si sono verificati errori durante la migrazione.")
        print("Controlla i messaggi sopra per i dettagli.")
