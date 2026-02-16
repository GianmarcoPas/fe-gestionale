"""
Migrazione: Aggiunge campi per utenti base a LavoroAdmin
- data_contatto
- note
- sollecito
- data_sollecito
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
        
        if 'data_contatto' not in columns:
            print("Aggiungo colonna data_contatto...")
            db.session.execute(text('ALTER TABLE lavoro_admin ADD COLUMN data_contatto DATE'))
        
        if 'note' not in columns:
            print("Aggiungo colonna note...")
            db.session.execute(text('ALTER TABLE lavoro_admin ADD COLUMN note TEXT'))
        
        if 'sollecito' not in columns:
            print("Aggiungo colonna sollecito...")
            db.session.execute(text('ALTER TABLE lavoro_admin ADD COLUMN sollecito BOOLEAN DEFAULT 0'))
        
        if 'data_sollecito' not in columns:
            print("Aggiungo colonna data_sollecito...")
            db.session.execute(text('ALTER TABLE lavoro_admin ADD COLUMN data_sollecito DATE'))
        
        if 'compenso' not in columns:
            print("Aggiungo colonna compenso...")
            db.session.execute(text('ALTER TABLE lavoro_admin ADD COLUMN compenso REAL DEFAULT 0.0'))
        
        db.session.commit()
        print("[OK] Migrazione completata con successo!")
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERRORE] Errore durante la migrazione: {e}")
        raise
