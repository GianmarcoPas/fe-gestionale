"""
Migrazione: Aggiunge il campo ordine_abbandono a Bene
- ordine_abbandono (INTEGER, nullable)

Serve per ordinare i lavori abbandonati nell'ordine effettivo di abbandono,
indipendentemente dall'ordine di creazione dei lavori.

Eseguire questo script sul server PythonAnywhere:
1. Vai su PythonAnywhere Dashboard
2. Apri una Bash console
3. Vai nella directory del progetto: cd ~/fe-gestionale
4. Attiva il virtualenv: source ~/.virtualenvs/my-venv/bin/activate
5. Esegui: python migrate_add_ordine_abbandono.py
"""

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('bene')]

        if 'ordine_abbandono' not in columns:
            print("Aggiungo colonna ordine_abbandono...")
            db.session.execute(text('ALTER TABLE bene ADD COLUMN ordine_abbandono INTEGER'))

            # Inizializza un ordine progressivo per i beni già abbandonati
            # usando l'ID bene come approssimazione dell'ordine storico
            print("Inizializzo ordine_abbandono per i beni già abbandonati...")
            result = db.session.execute(
                text("SELECT id FROM bene WHERE stato = 'abbandonato' ORDER BY id ASC")
            )
            current_order = 0
            for row in result:
                current_order += 1
                db.session.execute(
                    text("UPDATE bene SET ordine_abbandono = :ord WHERE id = :id"),
                    {"ord": current_order, "id": row.id},
                )
        else:
            print("Colonna ordine_abbandono già esistente")

        db.session.commit()
        print("[OK] Migrazione completata con successo!")

    except Exception as e:
        db.session.rollback()
        print(f"[ERRORE] Errore durante la migrazione: {e}")
        import traceback

        traceback.print_exc()
        raise

