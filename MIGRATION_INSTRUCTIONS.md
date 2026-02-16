# Istruzioni per eseguire le migrazioni sul server PythonAnywhere

## Migrazione: Campi Abbandono

Aggiunge i campi per gestire i lavori abbandonati nella tabella `bene`.

### Passaggi

1. **Vai su PythonAnywhere Dashboard** (https://www.pythonanywhere.com)

2. **Apri una Bash console** (Console tab)

3. **Vai nella directory del progetto:**
   ```bash
   cd ~/fe-gestionale
   ```

4. **Attiva il virtualenv:**
   ```bash
   source ~/.virtualenvs/my-venv/bin/activate
   ```

5. **Esegui lo script di migrazione:**
   ```bash
   python migrate_add_abbandono_fields.py
   ```

6. **Verifica che l'output mostri:**
   ```
   [OK] Migrazione completata con successo!
   ```

7. **Ricarica l'applicazione web** (Web tab > Reload)

### Colonne che verranno aggiunte alla tabella `bene`

- `motivo_abbandono` (VARCHAR(100)) - Motivo dell'abbandono: 'assegnato_altro_studio', 'abbandonato_cliente', 'altro'
- `commento_abbandono` (TEXT) - Commento quando il motivo è 'altro'
- `data_abbandono` (DATE) - Data in cui il bene è stato abbandonato (per ordinare i lavori abbandonati)

Lo script è sicuro e può essere eseguito più volte: controlla se le colonne esistono già prima di aggiungerle.

---

## Migrazione: Ordine Abbandono

Aggiunge il campo `ordine_abbandono` alla tabella `bene` per poter ordinare
i lavori abbandonati nell'esatto ordine in cui vengono abbandonati.

### Passaggi

1. **Vai su PythonAnywhere Dashboard** (https://www.pythonanywhere.com)

2. **Apri una Bash console** (Console tab)

3. **Vai nella directory del progetto:**
   ```bash
   cd ~/fe-gestionale
   ```

4. **Attiva il virtualenv:**
   ```bash
   source ~/.virtualenvs/my-venv/bin/activate
   ```

5. **Esegui lo script di migrazione:**
   ```bash
   python migrate_add_ordine_abbandono.py
   ```

6. **Verifica che l'output mostri:**
   ```text
   [OK] Migrazione completata con successo!
   ```

7. **Ricarica l'applicazione web** (Web tab > Reload)

### Colonna che verrà aggiunta alla tabella `bene`

- `ordine_abbandono` (INTEGER) - Progressivo globale usato per ordinare i lavori abbandonati
  nell'ordine in cui vengono abbandonati (primo in alto, poi via via gli altri sotto).

Lo script è sicuro e può essere eseguito più volte: controlla se la colonna esiste già
prima di aggiungerla e inizializza un ordine per i beni già abbandonati.

---

## Migrazione: Campi Utenti Base (Legacy)

Il database sul server non ha ancora le colonne aggiunte per gli utenti base. Segui questi passaggi:

### Passaggi

1. **Vai su PythonAnywhere Dashboard** (https://www.pythonanywhere.com)

2. **Apri una Bash console** (Console tab)

3. **Vai nella directory del progetto:**
   ```bash
   cd ~/fe-gestionale
   ```

4. **Attiva il virtualenv:**
   ```bash
   source ~/.virtualenvs/my-venv/bin/activate
   ```

5. **Esegui lo script di migrazione:**
   ```bash
   python migrate_add_base_user_fields.py
   ```

6. **Verifica che l'output mostri:**
   ```
   [OK] Migrazione completata con successo!
   ```

7. **Ricarica l'applicazione web** (Web tab > Reload)

### Colonne che verranno aggiunte alla tabella `lavoro_admin`

- `data_contatto` (DATE) - Data contatto per utenti base
- `note` (TEXT) - Note per utenti base
- `sollecito` (BOOLEAN) - Flag sollecito
- `data_sollecito` (DATE) - Data sollecito
- `compenso` (REAL) - Compenso assegnato da Roberto

Lo script è sicuro e può essere eseguito più volte: controlla se le colonne esistono già prima di aggiungerle.
