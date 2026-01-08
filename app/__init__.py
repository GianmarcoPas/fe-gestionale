from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inizializza le estensioni
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configurazione Segreta (chiave per criptare i cookie)
    app.config['SECRET_KEY'] = 'chiave-super-segreta-first-engineering'
    # Configurazione Database (file locale SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestionale.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Se non sei loggato, vai qui

    with app.app_context():
        # Importa le parti del nostro programma
        from .routes import auth_routes, main_routes
        from . import models

        # Registra le rotte (Blueprint)
        app.register_blueprint(auth_routes.bp)
        app.register_blueprint(main_routes.bp)

        # Crea il database se non esiste
        db.create_all()

    return app