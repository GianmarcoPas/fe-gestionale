from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inizializza le estensioni
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Effettua il login per accedere."

def create_app():
    app = Flask(__name__)
    
    # Configurazione
    app.config['SECRET_KEY'] = 'chiave_super_segreta_cambiala_in_produzione'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestionale.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Collega estensioni all'app
    db.init_app(app)
    login_manager.init_app(app)

    # Importa i modelli e definisci il user_loader QUI per evitare errori
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registra le rotte (Blueprints)
    from app.routes.auth_routes import bp as auth_bp
    from app.routes.main_routes import bp as main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Crea il database se non esiste
    with app.app_context():
        db.create_all()
        
        # Auto-migrazione: aggiunge colonne mancanti alla tabella user
        try:
            inspector = db.inspect(db.engine)
            if inspector.has_table('user'):
                user_columns = [col['name'] for col in inspector.get_columns('user')]
                from sqlalchemy import text
                if 'last_seen_note_id' not in user_columns:
                    db.session.execute(text('ALTER TABLE user ADD COLUMN last_seen_note_id INTEGER DEFAULT 0'))
                if 'dismissed_changelog_id' not in user_columns:
                    db.session.execute(text('ALTER TABLE user ADD COLUMN dismissed_changelog_id INTEGER DEFAULT 0'))
                db.session.commit()
        except Exception:
            db.session.rollback()
        
        # Auto-migrazione: crea tabella changelog se non esiste
        try:
            inspector = db.inspect(db.engine)
            if not inspector.has_table('changelog'):
                from sqlalchemy import text
                db.session.execute(text('''
                    CREATE TABLE changelog (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        versione VARCHAR(50) NOT NULL,
                        titolo VARCHAR(200) NOT NULL,
                        contenuto TEXT NOT NULL,
                        data_pubblicazione DATETIME DEFAULT CURRENT_TIMESTAMP,
                        attivo BOOLEAN DEFAULT 1,
                        ordine INTEGER DEFAULT 0
                    )
                '''))
                db.session.commit()
        except Exception:
            db.session.rollback()
        
        # Crea utenti admin/base di default SOLO se non esistono
        # NOTA: Non resettiamo le password degli utenti esistenti per evitare problemi su PythonAnywhere
        # Usa init_users.py per resettare manualmente le password quando necessario
        
        default_pass = 'Ciao1234'
        
        # Admin users - crea solo se non esistono
        admins = ['Roberto', 'Lucio', 'Giuseppe', 'Carmela']
        for username in admins:
            if not User.query.filter_by(username=username).first():
                admin = User(username=username, role='admin', admin_view_mode='extra2')
                admin.set_password(default_pass)
                db.session.add(admin)
        
        # Base users - crea solo se non esistono
        base_users = ['Gianmarco', 'Francescos', 'Francescou', 'Giovanni', 'Marco']
        for username in base_users:
            if not User.query.filter_by(username=username).first():
                base = User(username=username, role='base', admin_view_mode='standard')
                base.set_password(default_pass)
                db.session.add(base)
            
        db.session.commit()

        # Auto-seed changelog: aggiunge il nuovo changelog se non esiste
        try:
            from app.models import Changelog
            if not Changelog.query.filter_by(versione="2026-02-21").first():
                nuovo_changelog = Changelog(
                    versione="2026-02-21",
                    titolo="Aggiornamento Dashboard e Fatturazione",
                    contenuto="""<h4>💰 Fatturazione Differenziata</h4>
<p>La logica di fatturazione è stata aggiornata per distinguere i diversi soggetti:</p>
<p><em>...video in arrivo...</em></p>

<h4>📊 Card Fatturazione Aggiornata</h4>
<p>La card di fatturazione nella dashboard ora mostra informazioni più dettagliate:</p>
<ul>
    <li><strong>Lavori da fatturare</strong>: numero di lavori per cui manca ancora la fattura (divisi per soggetto)</li>
    <li><strong>Lavori incassati</strong>: lavori per cui la fattura è stata emessa e il pagamento ricevuto</li>
    <li>Visione chiara e immediata dello stato di fatturazione complessivo</li>
</ul>

<h4>💸 Card Lavori da Incassare</h4>
<p>Nuova card dedicata ai lavori da incassare:</p>
<ul>
    <li>Mostra i lavori per i quali la fattura FE è stata emessa ma il <strong>pagamento non è ancora stato ricevuto</strong></li>
    <li>Permette di tenere sotto controllo i crediti in sospeso</li>
</ul>

<h4>🎨 Miglioramenti Layout Dashboard</h4>
<ul>
    <li><strong>Card stati lavori riposizionate</strong>: le card che mostrano gli stati dei lavori sono state spostate per migliorare l'utilizzo dello spazio</li>
    <li>Layout più compatto e leggibile, con le informazioni più importanti in primo piano</li>
</ul>""",
                    attivo=True,
                    ordine=2
                )
                db.session.add(nuovo_changelog)
                db.session.commit()
        except Exception:
            db.session.rollback()

    return app