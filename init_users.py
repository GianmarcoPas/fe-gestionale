#!/usr/bin/env python3
"""
Script per inizializzare o resettare gli utenti nel database.
Eseguire con: python init_users.py

Su PythonAnywhere:
1. Vai nella Console Bash
2. Naviga nella directory del progetto
3. Esegui: python3.10 init_users.py (o la versione Python che usi)
"""
from app import create_app, db
from app.models import User

app = create_app()

def init_users():
    with app.app_context():
        # Utenti da creare/resettare
        users_to_create = [
            # Admin
            {'username': 'Roberto', 'role': 'admin', 'admin_view_mode': 'extra2', 'password': 'Ciao1234'},
            {'username': 'Lucio', 'role': 'admin', 'admin_view_mode': 'extra2', 'password': 'Ciao1234'},
            {'username': 'Giuseppe', 'role': 'admin', 'admin_view_mode': 'extra2', 'password': 'Ciao1234'},
            {'username': 'Carmela', 'role': 'admin', 'admin_view_mode': 'extra2', 'password': 'Ciao1234'},
            # Base
            {'username': 'Gianmarco', 'role': 'base', 'admin_view_mode': 'standard', 'password': 'Ciao1234'},
            {'username': 'Francescos', 'role': 'base', 'admin_view_mode': 'standard', 'password': 'Ciao1234'},
            {'username': 'Francescou', 'role': 'base', 'admin_view_mode': 'standard', 'password': 'Ciao1234'},
            {'username': 'Giovanni', 'role': 'base', 'admin_view_mode': 'standard', 'password': 'Ciao1234'},
            {'username': 'Marco', 'role': 'base', 'admin_view_mode': 'standard', 'password': 'Ciao1234'}
        ]
        
        print("=== Inizializzazione Utenti ===\n")
        
        for user_data in users_to_create:
            username = user_data['username']
            user = User.query.filter_by(username=username).first()
            
            if user:
                # L'utente esiste, aggiorna password e ruolo
                print(f"✓ Utente '{username}' già esistente. Aggiornamento...")
                user.set_password(user_data['password'])
                user.role = user_data['role']
                if 'admin_view_mode' in user_data:
                    user.admin_view_mode = user_data['admin_view_mode']
                db.session.commit()
                print(f"  Password e ruolo aggiornati per '{username}'")
            else:
                # L'utente non esiste, crealo
                print(f"✓ Creazione nuovo utente '{username}'...")
                new_user = User(
                    username=username,
                    role=user_data['role'],
                    admin_view_mode=user_data.get('admin_view_mode', 'standard')
                )
                new_user.set_password(user_data['password'])
                db.session.add(new_user)
                db.session.commit()
                print(f"  Utente '{username}' creato con successo")
        
        print("\n=== Utenti disponibili ===")
        all_users = User.query.all()
        for u in all_users:
            print(f"  - {u.username} ({u.role}) - View Mode: {u.admin_view_mode}")
        
        print("\n✅ Inizializzazione completata!")
        print("\nCredenziali di accesso (password per tutti: Ciao1234):")
        print("  Admin: Roberto, Lucio, Giuseppe, Carmela")
        print("  Base:  Gianmarco, Francescos, Francescou, Giovanni, Marco")

if __name__ == '__main__':
    init_users()
