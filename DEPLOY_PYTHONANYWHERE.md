# Guida Deploy su PythonAnywhere

Questa guida ti aiuta ad applicare tutte le modifiche delle categorie su PythonAnywhere.

## 📋 File Modificati

I seguenti file sono stati modificati e devono essere caricati su PythonAnywhere:

1. **`app/models.py`** - Aggiunto campo `categoria` al modello `LavoroAdmin`
2. **`app/static/css/style.css`** - Aggiunti stili per i pulsanti categoria
3. **`app/templates/main/lavori_admin.html`** - Modificato HTML e JavaScript per i pulsanti categoria
4. **`app/routes/main_routes.py`** - Aggiornate le route per salvare/recuperare la categoria
5. **`migrate_add_categoria_column.py`** - Script di migrazione per aggiungere la colonna al database

## 🚀 Procedura di Deploy

### Passo 1: Backup del Database (IMPORTANTE!)

Prima di tutto, fai un backup del database esistente:

```bash
# Su PythonAnywhere, nella Bash console
cd /home/tuousername/mysite  # Sostituisci tuousername con il tuo username
cp instance/gestionale.db instance/gestionale.db.backup
```

Oppure scarica il file `instance/gestionale.db` tramite l'interfaccia Files di PythonAnywhere.

### Passo 2: Carica i File Modificati

Carica tutti i file modificati su PythonAnywhere tramite:
- **Git** (se usi Git): `git pull` nella directory del progetto
- **Files interface**: Carica manualmente i file modificati
- **SFTP**: Usa un client SFTP per caricare i file

### Passo 3: Esegui la Migrazione del Database

Apri una **Bash console** su PythonAnywhere e esegui:

```bash
# Vai nella directory del progetto
cd /home/tuousername/mysite  # Sostituisci tuousername con il tuo username

# Attiva l'ambiente virtuale (se ne usi uno)
source venv/bin/activate  # oppure source virtualenv/bin/activate

# Esegui lo script di migrazione
python3 migrate_add_categoria_column.py
```

Lo script:
- Troverà automaticamente il database `instance/gestionale.db`
- Aggiungerà la colonna `categoria` alla tabella `lavoro_admin`
- Ti mostrerà un messaggio di successo

**Output atteso:**
```
============================================================
Migrazione Database: Aggiunta colonna categoria
============================================================

[i] Database trovato: /home/tuousername/mysite/instance/gestionale.db

[+] Colonna categoria aggiunta con successo

[OK] Migrazione completata con successo!
Ora puoi riavviare la tua web app.

[SUCCESS] Il database è stato aggiornato correttamente!
```

### Passo 4: Verifica la Migrazione (Opzionale)

Puoi verificare che la colonna sia stata aggiunta:

```bash
# Apri SQLite
sqlite3 instance/gestionale.db

# Verifica la struttura della tabella
.schema lavoro_admin

# Dovresti vedere la colonna categoria
# Esci da SQLite
.quit
```

### Passo 5: Riavvia l'Applicazione Web

1. Vai su **Web** nella dashboard di PythonAnywhere
2. Clicca sul pulsante **Reload** per riavviare l'applicazione

### Passo 6: Testa le Funzionalità

1. Accedi all'applicazione
2. Vai alla pagina dei lavori admin
3. **Testa i pulsanti categoria:**
   - Clicca sul pulsante + nella barra in basso
   - Verifica che appaiano i 4 pulsanti categoria
   - Clicca su uno di essi e verifica che si apra il form con la categoria corretta
4. **Testa la modifica lavori:**
   - Modifica un lavoro esistente
   - Verifica che i pulsanti categoria appaiano sopra l'anagrafica cliente
   - Cambia categoria e verifica che si salvi correttamente

## ⚠️ Note Importanti

### Lavori Esistenti

I lavori esistenti avranno `categoria = NULL` (nessuna categoria). Questo è normale e non causa problemi. Puoi:

1. **Lasciarli così** - funzioneranno normalmente
2. **Assegnare categorie manualmente** - modifica ogni lavoro e seleziona una categoria
3. **Assegnare categorie in batch** (se necessario, posso creare uno script)

### Se Qualcosa Va Storto

Se qualcosa non funziona:

1. **Ripristina il backup del database:**
   ```bash
   cp instance/gestionale.db.backup instance/gestionale.db
   ```

2. **Verifica i log di errore:**
   - Vai su **Web** → **Error log** nella dashboard di PythonAnywhere
   - Controlla gli errori e risolvili

3. **Verifica che tutti i file siano stati caricati correttamente:**
   - Controlla che i file modificati siano presenti
   - Verifica che non ci siano errori di sintassi

## 🔍 Verifica Post-Deploy

Dopo il deploy, verifica:

- [ ] I pulsanti categoria appaiono quando clicchi sul pulsante +
- [ ] I pulsanti categoria hanno lo stile corretto (bianco, bordo nero)
- [ ] Cliccando su un pulsante categoria si apre il form con la categoria corretta
- [ ] Il titolo del form mostra "Nuovo Lavoro - [CATEGORIA]"
- [ ] Modificando un lavoro esistente, i pulsanti categoria appaiono sopra l'anagrafica
- [ ] Cambiando categoria in un lavoro esistente, si salva correttamente
- [ ] I lavori esistenti funzionano normalmente (anche senza categoria)

## 📞 Supporto

Se riscontri problemi durante il deploy, controlla:
1. I log di errore su PythonAnywhere
2. Che tutti i file siano stati caricati
3. Che la migrazione sia stata eseguita correttamente
4. Che l'applicazione sia stata riavviata
