"""
Script per inizializzare il primo changelog con le novità di oggi.

Eseguire questo script per creare il primo changelog:
python init_changelog.py
"""

from app import create_app, db
from app.models import Changelog
from datetime import datetime

app = create_app()

with app.app_context():
    try:
        # Verifica se esiste già un changelog
        existing = Changelog.query.first()
        if existing:
            print(f"Changelog già esistente: '{existing.titolo}' (ID: {existing.id})")
            print("Per creare un nuovo changelog, usa l'API o modifica quello esistente.")
            exit(0)
        
        # Crea il primo changelog
        changelog = Changelog(
            versione="2024-02-16",
            titolo="Nuove Funzionalità - Febbraio 2024",
            contenuto="""<h4>🎯 Gestione Lavori Abbandonati</h4>
<p>È stata aggiunta una nuova funzionalità per gestire i lavori abbandonati:</p>
<ul>
    <li><strong>Nuovo stato "Abbandonato"</strong>: Ora puoi segnare un bene come abbandonato direttamente dalla tabella lavori</li>
    <li><strong>Tre opzioni di abbandono</strong>:
        <ul>
            <li><strong>Assegnato ad altro studio</strong>: Il lavoro è stato assegnato a un altro studio professionale</li>
            <li><strong>Abbandonato dal cliente</strong>: Il cliente ha deciso di non procedere</li>
            <li><strong>Altro</strong>: Con possibilità di inserire un commento personalizzato</li>
        </ul>
    </li>
    <li><strong>Nuova sezione "Abbandonati"</strong>: Nella dashboard admin puoi vedere tutti i lavori abbandonati in una sezione dedicata</li>
    <li><strong>Filtro abbandonati</strong>: Puoi filtrare i lavori per vedere solo quelli abbandonati nella tabella principale</li>
</ul>

<h4>📝 Sistema Note Condivise</h4>
<p>È stato introdotto un nuovo sistema di note condivise tra tutti gli admin:</p>
<ul>
    <li><strong>Card Note nella Dashboard</strong>: Nuova card dedicata alle note nella prima riga della dashboard</li>
    <li><strong>Note scrollabili</strong>: Puoi vedere tutte le note scorrendo nella card, senza limiti</li>
    <li><strong>Gestione completa</strong>: Crea, modifica ed elimina note direttamente dalla card</li>
    <li><strong>Notifiche nuove note</strong>: Un badge rosso ti avvisa quando ci sono nuove note create da altri admin</li>
    <li><strong>Tracciamento autore</strong>: Ogni nota mostra chi l'ha creata e quando</li>
</ul>

<h4>🎨 Miglioramenti Dashboard</h4>
<ul>
    <li>Riorganizzazione layout: prima riga con 3 card uniformi (Fatturazione, Timeline, Note)</li>
    <li>Card note con scroll per visualizzare tutte le note</li>
    <li>Interfaccia più pulita e organizzata</li>
</ul>

<p><strong>💡 Suggerimento</strong>: Clicca sul pulsante "+" nella card Note per aggiungere una nuova nota, oppure clicca sulla card stessa per vedere tutte le note e gestirle.</p>""",
            attivo=True,
            ordine=1
        )
        
        db.session.add(changelog)
        db.session.commit()
        
        print(f"[OK] Changelog creato con successo!")
        print(f"     Titolo: {changelog.titolo}")
        print(f"     Versione: {changelog.versione}")
        print(f"     ID: {changelog.id}")
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERRORE] Errore durante la creazione del changelog: {e}")
        import traceback
        traceback.print_exc()
        raise
