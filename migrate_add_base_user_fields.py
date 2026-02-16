"""
Migrazione: Aggiunge campi per utenti base a LavoroAdmin
- data_contatto
- note
- sollecito
- data_sollecito
- compenso

Eseguire questo script sul server PythonAnywhere:
1. Vai su PythonAnywhere Dashboard
2. Apri una Bash console
3. Vai nella directory del progetto: cd ~/fe-gestionale
4. Attiva il virtualenv: source ~/.virtualenvs/my-venv/bin/activate
5. Esegui: python migrate_add_base_user_fields.py
"""

from app import create_app, db
from app.models import LavoroAdmin
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Verifica se le colonne esistono già
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('lavoro_admin')]
        
        print(f"Colonne esistenti: {len(columns)}")
        
        if 'data_contatto' not in columns:
            print("Aggiungo colonna data_contatto...")
            db.session.execute(text('ALTER TABLE lavoro_admin ADD COLUMN data_contatto DATE'))
        else:
            print("Colonna data_contatto gia' esistente")
        
        if 'note' not in columns:
            print("Aggiungo colonna note...")
            db.session.execute(text('ALTER TABLE lavoro_admin ADD COLUMN note TEXT'))
        else:
            print("Colonna note gia' esistente")
        
        if 'sollecito' not in columns:
            print("Aggiungo colonna sollecito...")
            db.session.execute(text('ALTER TABLE lavoro_admin ADD COLUMN sollecito BOOLEAN DEFAULT 0'))
        else:
            print("Colonna sollecito gia' esistente")
        
        if 'data_sollecito' not in columns:
            print("Aggiungo colonna data_sollecito...")
            db.session.execute(text('ALTER TABLE lavoro_admin ADD COLUMN data_sollecito DATE'))
        else:
            print("Colonna data_sollecito gia' esistente")
        
        if 'compenso' not in columns:
            print("Aggiungo colonna compenso...")
            db.session.execute(text('ALTER TABLE lavoro_admin ADD COLUMN compenso REAL DEFAULT 0.0'))
        else:
            print("Colonna compenso gia' esistente")
        
        db.session.commit()
        print("[OK] Migrazione completata con successo!")
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERRORE] Errore durante la migrazione: {e}")
        import traceback
        traceback.print_exc()
        raise
