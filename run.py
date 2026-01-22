from app import create_app, db
from app.models import User

app = create_app()

def initialize_users():
    """Crea gli utenti base e admin se non esistono, o aggiorna password se esistono"""
    with app.app_context():
        # Lista utenti come richiesto
        admins = ['Roberto', 'Lucio', 'Giuseppe', 'Carmela']
        base_users = ['Gianmarco', 'Francescos', 'Francescou', 'Giovanni', 'Marco']
        
        default_pass = "Ciao1234"
        
        # Controllo e creazione/aggiornamento Admins
        for name in admins:
            user = User.query.filter_by(username=name).first()
            if not user:
                new_user = User(username=name, role='admin', admin_view_mode='extra2')
                new_user.set_password(default_pass)
                db.session.add(new_user)
                print(f"[+] Admin creato: {name}")
            else:
                # Aggiorna password se l'utente esiste già
                user.set_password(default_pass)
                user.role = 'admin'
                if hasattr(user, 'admin_view_mode'):
                    user.admin_view_mode = 'extra2'
                db.session.commit()
                print(f"[✓] Password reset per admin: {name}")

        # Controllo e creazione/aggiornamento Base Users
        for name in base_users:
            user = User.query.filter_by(username=name).first()
            if not user:
                new_user = User(username=name, role='base', admin_view_mode='standard')
                new_user.set_password(default_pass)
                db.session.add(new_user)
                print(f"[+] Utente Base creato: {name}")
            else:
                # Aggiorna password se l'utente esiste già
                user.set_password(default_pass)
                user.role = 'base'
                db.session.commit()
                print(f"[✓] Password reset per utente base: {name}")

        db.session.commit()
        print("\n✅ Tutti gli utenti sono stati inizializzati/resettati!")

if __name__ == '__main__':
    # NOTA: initialize_users() NON viene chiamata automaticamente
    # Per inizializzare/resettare gli utenti, esegui manualmente:
    # python -c "from run import initialize_users, app; initialize_users()"
    # Oppure usa: python init_users.py
    app.run(debug=True)