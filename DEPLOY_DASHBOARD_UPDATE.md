# Guida Completa: Deploy Aggiornamento Dashboard e Nuove Funzionalità

Questa guida spiega come portare sul server PythonAnywhere tutte le modifiche fatte da quando abbiamo ridisposto la dashboard.

## 📋 Riepilogo Modifiche

### 1. Dashboard Riorganizzata
- Prima riga: 3 card uniformi (Fatturazione, Timeline Lavori, Note)
- Seconda riga: 4 card stato lavori
- Card Note scrollabile con tutte le note visibili

### 2. Sistema Note Admin
- Nuova card Note nella dashboard
- Gestione completa note (crea, modifica, elimina)
- Notifiche nuove note (badge rosso)
- Note scrollabili senza troncamento

### 3. Sistema Changelog
- Modal changelog che si apre automaticamente per gli admin
- Tracciamento changelog visti
- Possibilità di non mostrare più un changelog

---

## 🚀 Procedura Completa di Deploy

### STEP 1: Backup (Consigliato)

Prima di iniziare, fai un backup del database:
```bash
cd ~/fe-gestionale
cp instance/gestionale.db instance/gestionale.db.backup_$(date +%Y%m%d)
```

### STEP 2: Carica i File Modificati

Carica sul server tutti questi file (via Files tab o Git):

**File Modificati:**
- `app/models.py` - Aggiunti modelli NoteAdmin e Changelog, campi User
- `app/routes/main_routes.py` - Aggiunte route API per note e changelog
- `app/templates/main/dashboard.html` - Dashboard riorganizzata con card Note
- `app/templates/base.html` - Aggiunto modal changelog
- `app/static/css/style.css` - Stili per card note, modal changelog
- `app/__init__.py` - Auto-migrazione per colonne/tabelle mancanti

**Nuovi File da Caricare:**
- `migrate_create_note_admin_table.py` - Migrazione per note admin
- `migrate_add_changelog.py` - Migrazione per changelog
- `init_changelog.py` - Script per inizializzare primo changelog

### STEP 3: Esegui le Migrazioni

Apri una **Bash console** su PythonAnywhere e segui questi passaggi:

#### 3.1 Vai nella directory del progetto
```bash
cd ~/fe-gestionale
```

#### 3.2 Attiva il virtualenv
```bash
source ~/.virtualenvs/my-venv/bin/activate
```

#### 3.3 Migrazione 1: Note Admin
```bash
python migrate_create_note_admin_table.py
```

**Output atteso:**
```
Database: /home/tuousername/fe-gestionale/instance/gestionale.db
Tabella note_admin gia' esistente (o: Creo la tabella note_admin...)
Colonna last_seen_note_id gia' esistente (o: Aggiungo colonna last_seen_note_id...)
[OK] Migrazione completata con successo!
```

#### 3.4 Migrazione 2: Changelog
```bash
python migrate_add_changelog.py
```

**Output atteso:**
```
Database: /home/tuousername/fe-gestionale/instance/gestionale.db
Creo la tabella changelog...
[OK] Tabella changelog creata con successo!
Aggiungo colonna dismissed_changelog_id a user...
[OK] Colonna dismissed_changelog_id aggiunta!
[OK] Migrazione completata con successo!
```

#### 3.5 Inizializza il Primo Changelog
```bash
python init_changelog.py
```

**Output atteso:**
```
[OK] Changelog creato con successo!
     Titolo: Nuove Funzionalità - Febbraio 2024
     Versione: 2024-02-16
     ID: 1
```

### STEP 4: Verifica le Migrazioni

Controlla che tutto sia andato a buon fine:

```bash
python -c "from app import create_app, db; from app.models import NoteAdmin, Changelog, User; app = create_app(); print('✓ Modelli importati correttamente'); print('✓ NoteAdmin:', NoteAdmin.query.count(), 'note'); print('✓ Changelog:', Changelog.query.count(), 'changelog'); print('✓ User con last_seen_note_id:', User.query.filter(User.last_seen_note_id != None).count(), 'utenti')"
```

### STEP 5: Ricarica l'Applicazione

1. Vai su **Web tab** su PythonAnywhere
2. Clicca su **Reload** per ricaricare l'applicazione

### STEP 6: Test

1. Accedi come admin
2. Verifica che:
   - La dashboard mostri la nuova card Note
   - Il modal changelog si apra automaticamente
   - Le note siano scrollabili nella card
   - Il badge rosso appaia se ci sono nuove note

---

## 🔍 Risoluzione Problemi

### Errore: "no such column: user.last_seen_note_id"
**Soluzione:** Esegui manualmente:
```bash
python -c "import sqlite3; conn = sqlite3.connect('instance/gestionale.db'); conn.execute('ALTER TABLE user ADD COLUMN last_seen_note_id INTEGER DEFAULT 0'); conn.execute('ALTER TABLE user ADD COLUMN dismissed_changelog_id INTEGER DEFAULT 0'); conn.commit(); conn.close(); print('OK')"
```

### Errore: "no such table: note_admin"
**Soluzione:** Esegui di nuovo `migrate_create_note_admin_table.py`

### Errore: "no such table: changelog"
**Soluzione:** Esegui di nuovo `migrate_add_changelog.py`

### Il changelog non si apre
**Controlla:**
1. Che la tabella changelog esista: `python -c "from app import create_app, db; from app.models import Changelog; app = create_app(); print(Changelog.query.count())"`
2. Che ci sia almeno un changelog attivo
3. Che l'utente sia admin (`current_user.role == 'admin'`)

### Le note non si vedono
**Controlla:**
1. Che la tabella note_admin esista
2. Che l'utente sia admin
3. Console del browser per errori JavaScript

---

## 📝 Checklist Finale

- [ ] File modificati caricati sul server
- [ ] File nuovi caricati sul server
- [ ] Migrazione note_admin eseguita con successo
- [ ] Migrazione changelog eseguita con successo
- [ ] Primo changelog inizializzato
- [ ] Applicazione ricaricata
- [ ] Dashboard mostra card Note
- [ ] Modal changelog si apre automaticamente
- [ ] Note sono scrollabili
- [ ] Badge nuove note funziona

---

## 🎯 Ordine di Esecuzione Riepilogato

```bash
# 1. Backup (opzionale ma consigliato)
cp instance/gestionale.db instance/gestionale.db.backup_$(date +%Y%m%d)

# 2. Attiva virtualenv
source ~/.virtualenvs/my-venv/bin/activate

# 3. Migrazioni
python migrate_create_note_admin_table.py
python migrate_add_changelog.py
python init_changelog.py

# 4. Verifica
python -c "from app import create_app; app = create_app(); print('OK')"

# 5. Ricarica app da Web tab
```

---

## 📚 File di Riferimento

- `MIGRATION_INSTRUCTIONS.md` - Istruzioni dettagliate per ogni migrazione
- `migrate_create_note_admin_table.py` - Script migrazione note
- `migrate_add_changelog.py` - Script migrazione changelog
- `init_changelog.py` - Script inizializzazione changelog

---

**Nota:** Se qualcosa va storto, puoi sempre ripristinare il backup del database:
```bash
cp instance/gestionale.db.backup_YYYYMMDD instance/gestionale.db
```
