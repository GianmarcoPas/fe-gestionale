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
        
        # Crea utenti admin/base di default se non esistono
        if not User.query.filter_by(username='Carmela').first():
            admin = User(username='Carmela', role='admin', admin_view_mode='extra2')
            admin.set_password('Ciao1234')
            db.session.add(admin)
        
        if not User.query.filter_by(username='Gianmarco').first():
            base = User(username='Gianmarco', role='base')
            base.set_password('Ciao1234')
            db.session.add(base)
            
        db.session.commit()

    return app