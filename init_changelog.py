"""
Script per inizializzare i changelog con le novità.

Eseguire questo script per creare/aggiornare i changelog:
python init_changelog.py
"""

from app import create_app, db
from app.models import Changelog
from datetime import datetime

app = create_app()

with app.app_context():
    try:
        # Changelog 1 - Febbraio 2024 (originale)
        existing_1 = Changelog.query.filter_by(versione="2024-02-16").first()
        if not existing_1:
            changelog_1 = Changelog(
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
            db.session.add(changelog_1)
            print("[OK] Changelog v2024-02-16 creato!")
        else:
            print("Changelog v2024-02-16 già esistente, skip.")

        # Changelog 2 - Febbraio 2026 (nuovo)
        existing_2 = Changelog.query.filter_by(versione="2026-02-21").first()
        if not existing_2:
            changelog_2 = Changelog(
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
            db.session.add(changelog_2)
            print("[OK] Changelog v2026-02-21 creato!")
        else:
            print("Changelog v2026-02-21 già esistente, skip.")

        db.session.commit()
        print("\n[OK] Inizializzazione changelog completata con successo!")
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERRORE] Errore durante la creazione del changelog: {e}")
        import traceback
        traceback.print_exc()
        raise
