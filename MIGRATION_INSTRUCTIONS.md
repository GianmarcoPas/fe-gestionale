# Istruzioni per eseguire la migrazione sul server PythonAnywhere

Il database sul server non ha ancora le colonne aggiunte per gli utenti base. Segui questi passaggi:

## Passaggi

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

## Colonne che verranno aggiunte

- `data_contatto` (DATE) - Data contatto per utenti base
- `note` (TEXT) - Note per utenti base
- `sollecito` (BOOLEAN) - Flag sollecito
- `data_sollecito` (DATE) - Data sollecito
- `compenso` (REAL) - Compenso assegnato da Roberto

Lo script è sicuro e può essere eseguito più volte: controlla se le colonne esistono già prima di aggiungerle.
