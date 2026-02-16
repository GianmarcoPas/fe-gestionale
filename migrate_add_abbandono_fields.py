"""
Migrazione: Aggiunge campi per motivo abbandono a Bene
- motivo_abbandono (String(100), nullable)
- commento_abbandono (TEXT, nullable)
- data_abbandono (DATE, nullable)

Eseguire questo script sul server PythonAnywhere:
1. Vai su PythonAnywhere Dashboard
2. Apri una Bash console
3. Vai nella directory del progetto: cd ~/fe-gestionale
4. Attiva il virtualenv: source ~/.virtualenvs/my-venv/bin/activate
5. Esegui: python migrate_add_abbandono_fields.py
"""

from app import create_app, db
from app.models import Bene
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Verifica se le colonne esistono già
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('bene')]
        
        print(f"Colonne esistenti nella tabella 'bene': {len(columns)}")
        
        if 'motivo_abbandono' not in columns:
            print("Aggiungo colonna motivo_abbandono...")
            db.session.execute(text('ALTER TABLE bene ADD COLUMN motivo_abbandono VARCHAR(100)'))
        else:
            print("Colonna motivo_abbandono gia' esistente")
        
        if 'commento_abbandono' not in columns:
            print("Aggiungo colonna commento_abbandono...")
            db.session.execute(text('ALTER TABLE bene ADD COLUMN commento_abbandono TEXT'))
        else:
            print("Colonna commento_abbandono gia' esistente")
        
        if 'data_abbandono' not in columns:
            print("Aggiungo colonna data_abbandono...")
            db.session.execute(text('ALTER TABLE bene ADD COLUMN data_abbandono DATE'))
        else:
            print("Colonna data_abbandono gia' esistente")
        
        db.session.commit()
        print("[OK] Migrazione completata con successo!")
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERRORE] Errore durante la migrazione: {e}")
        import traceback
        traceback.print_exc()
        raise
