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
        default_pass = 'Ciao1234'
        
        # Admin users
        admins = ['Roberto', 'Lucio', 'Giuseppe', 'Carmela']
        for username in admins:
            if not User.query.filter_by(username=username).first():
                admin = User(username=username, role='admin', admin_view_mode='extra2')
                admin.set_password(default_pass)
                db.session.add(admin)
        
        # Base users
        base_users = ['Gianmarco', 'Francescos', 'Francescou', 'Giovanni', 'Marco']
        for username in base_users:
            if not User.query.filter_by(username=username).first():
                base = User(username=username, role='base', admin_view_mode='standard')
                base.set_password(default_pass)
                db.session.add(base)
            
        db.session.commit()

    return app