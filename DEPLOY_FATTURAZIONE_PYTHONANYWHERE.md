# Guida Deploy Funzionalità Fatturazione su PythonAnywhere

Questa guida ti aiuta a caricare la nuova funzionalità di fatturazione su PythonAnywhere.

## 📋 File Modificati/Aggiunti

I seguenti file sono stati modificati o aggiunti e devono essere caricati su PythonAnywhere:

### File Modificati:
1. **`app/models.py`** - Aggiunti campi `data_fattura_*` per tracciare le date di fatturazione
2. **`app/routes/main_routes.py`** - Aggiunte route per la fatturazione:
   - `/fatturazione/<tipo>` - Pagina principale fatturazione
   - `/api/fatturazione/salva` - Salva numero fattura su più lavori
   - `/api/fatturazione/lista/<tipo>` - Lista fatture emesse
   - `/api/fatturazione/lavori-disponibili/<tipo>` - Lavori disponibili per modifica
   - `/api/fatturazione/dettaglio/<tipo>/<numero_fattura>` - Dettaglio fattura
   - `/api/fatturazione/aggiorna` - Aggiorna fattura esistente
3. **`app/templates/main/dashboard.html`** - Pulsanti FE, AMIN, GALV, FH ora cliccabili
4. **`app/static/css/style.css`** - Stili per i link dei pulsanti fatturazione

### File Nuovi:
5. **`app/templates/main/fatturazione.html`** - Nuovo template per la sezione fatturazione
6. **`migrate_add_data_fattura_columns.py`** - Script di migrazione database

## 🚀 Procedura di Deploy

### Passo 1: Backup del Database (IMPORTANTE!)

Prima di tutto, fai un backup del database esistente:

```bash
# Su PythonAnywhere, nella Bash console
cd /home/tuousername/mysite  # Sostituisci tuousername con il tuo username
cp instance/gestionale.db instance/gestionale.db.backup_$(date +%Y%m%d_%H%M%S)
```

Oppure scarica il file `instance/gestionale.db` tramite l'interfaccia Files di PythonAnywhere.

### Passo 2: Carica i File Modificati

Carica tutti i file modificati e nuovi su PythonAnywhere tramite:
- **Git** (se usi Git): `git pull` nella directory del progetto
- **Files interface**: Carica manualmente i file modificati
- **SFTP**: Usa un client SFTP per caricare i file

**File da caricare:**
- `app/models.py`
- `app/routes/main_routes.py`
- `app/templates/main/dashboard.html`
- `app/templates/main/fatturazione.html` (NUOVO)
- `app/static/css/style.css`
- `migrate_add_data_fattura_columns.py` (NUOVO)

### Passo 3: Esegui la Migrazione del Database

Apri una **Bash console** su PythonAnywhere e esegui:

```bash
# Vai nella directory del progetto
cd /home/tuousername/mysite  # Sostituisci tuousername con il tuo username

# Attiva l'ambiente virtuale (se ne usi uno)
source venv/bin/activate  # oppure source virtualenv/bin/activate

# Esegui lo script di migrazione
python3.10 migrate_add_data_fattura_columns.py
# (sostituisci 3.10 con la versione Python del tuo ambiente, es. python3.9, python3.11)
```

Lo script:
- Troverà automaticamente il database `instance/gestionale.db`
- Aggiungerà le colonne `data_fattura_*` alla tabella `lavoro_admin`
- Ti mostrerà un messaggio di successo per ogni colonna aggiunta

**Output atteso:**
```
============================================================
Migrazione Database: Aggiunta colonne data_fattura_*
============================================================

[i] Database trovato: /home/tuousername/mysite/instance/gestionale.db

[+] Colonna data_fattura_fe aggiunta con successo
[+] Colonna data_fattura_amin aggiunta con successo
[+] Colonna data_fattura_galvan aggiunta con successo
[+] Colonna data_fattura_fh aggiunta con successo
[+] Colonna data_fattura_bianc aggiunta con successo
[+] Colonna data_fattura_deloitte aggiunta con successo
[+] Colonna data_fattura_ext aggiunta con successo
[+] Colonna data_fattura_revisore aggiunta con successo
[+] Colonna data_fattura_caricamento aggiunta con successo

[OK] Migrazione completata con successo!
Ora puoi riavviare la tua web app su PythonAnywhere.

[SUCCESS] Il database è stato aggiornato correttamente!
```

### Passo 4: Verifica la Migrazione (Opzionale)

Puoi verificare che le colonne siano state aggiunte:

```bash
# Apri SQLite
sqlite3 instance/gestionale.db

# Verifica la struttura della tabella
.schema lavoro_admin

# Dovresti vedere le nuove colonne data_fattura_*
# Esci da SQLite
.quit
```

### Passo 5: Riavvia l'Applicazione Web

1. Vai su **Web** nella dashboard di PythonAnywhere
2. Clicca sul pulsante **Reload** per riavviare l'applicazione

### Passo 6: Testa le Funzionalità

1. Accedi all'applicazione
2. Vai alla dashboard (devi essere admin)
3. **Testa i pulsanti fatturazione:**
   - Nella card "Fatturato", clicca su uno dei pulsanti FE, AMIN, GALV, FH
   - Verifica che si apra la pagina di fatturazione
4. **Testa la fatturazione:**
   - Seleziona alcuni lavori con stato "incassata"
   - Inserisci un numero di fattura
   - Clicca "Salva Fattura"
   - Verifica che i lavori vengano rimossi dalla lista
5. **Testa lo storico fatture:**
   - Nella sezione "Fatture Emesse", verifica che le fatture salvate siano visibili
   - Clicca su una fattura per espanderla e vedere i lavori
   - Clicca "Modifica" per testare la modifica di una fattura

## ⚠️ Note Importanti

### Lavori Esistenti

I lavori esistenti avranno i campi `data_fattura_*` = NULL (nessuna data). Questo è normale e non causa problemi. Le date verranno impostate automaticamente quando salvi una fattura.

### Fatture Esistenti

Se hai già dei numeri di fattura salvati nei campi `f_amin`, `f_fe`, ecc., questi continueranno a funzionare. Le date verranno impostate solo per le nuove fatture salvate dopo il deploy.

### Se Qualcosa Va Storto

Se qualcosa non funziona:

1. **Ripristina il backup del database:**
   ```bash
   cp instance/gestionale.db.backup_YYYYMMDD_HHMMSS instance/gestionale.db
   ```

2. **Verifica i log di errore:**
   - Vai su **Web** → **Error log** nella dashboard di PythonAnywhere
   - Controlla gli errori e risolvili

3. **Verifica che tutti i file siano stati caricati correttamente:**
   - Controlla che i file modificati siano presenti
   - Verifica che non ci siano errori di sintassi
   - Controlla la console del browser (F12) per errori JavaScript

## 🔍 Verifica Post-Deploy

Dopo il deploy, verifica:

- [ ] I pulsanti FE, AMIN, GALV, FH nella dashboard sono cliccabili
- [ ] Cliccando su un pulsante si apre la pagina di fatturazione corretta
- [ ] La pagina mostra i lavori con stato "incassata" e compenso > 0
- [ ] È possibile selezionare lavori e inserire un numero di fattura
- [ ] Dopo il salvataggio, i lavori vengono rimossi dalla lista
- [ ] Lo storico delle fatture viene sempre caricato (anche senza lavori da fatturare)
- [ ] È possibile modificare una fattura esistente
- [ ] È possibile escludere/includere lavori da una fattura esistente

## 📞 Supporto

Se riscontri problemi durante il deploy, controlla:

1. I log di errore su PythonAnywhere (Web → Error log)
2. La console del browser (F12) per errori JavaScript
3. Che tutti i file siano stati caricati
4. Che la migrazione sia stata eseguita correttamente
5. Che l'applicazione sia stata riavviata

## 🔄 Rollback (se necessario)

Se devi tornare indietro:

1. Ripristina il backup del database
2. Rimuovi o rinomina il file `app/templates/main/fatturazione.html`
3. Ripristina i file originali di:
   - `app/models.py`
   - `app/routes/main_routes.py`
   - `app/templates/main/dashboard.html`
   - `app/static/css/style.css`
4. Riavvia l'applicazione
