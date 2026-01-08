from app import create_app, db
from app.models import User

app = create_app()

def initialize_users():
    """Crea gli utenti base e admin se non esistono"""
    with app.app_context():
        # Lista utenti come richiesto
        admins = ['Carmela', 'Roberto', 'Lucio', 'Giuseppe']
        base_users = ['Gianmarco', 'Giovanni', 'Francesco', 'Marco']
        
        default_pass = "Ciao1234"
        
        # Controllo e creazione Admins
        for name in admins:
            if not User.query.filter_by(username=name).first():
                new_user = User(username=name, role='admin')
                new_user.set_password(default_pass)
                db.session.add(new_user)
                print(f"[+] Admin creato: {name}")

        # Controllo e creazione Base Users
        for name in base_users:
            if not User.query.filter_by(username=name).first():
                new_user = User(username=name, role='base')
                new_user.set_password(default_pass)
                db.session.add(new_user)
                print(f"[+] Utente Base creato: {name}")

        db.session.commit()

if __name__ == '__main__':
    initialize_users() # Lancia la creazione utenti
    app.run(debug=True)