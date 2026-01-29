# Fix per PythonAnywhere - Pulsanti Categoria Visibili

Se i pulsanti categoria appaiono sempre visibili come rettangoli grigi invece di essere nascosti, segui questi passaggi:

## 🔧 Soluzione 1: Svuota la Cache del Browser

1. **Su PythonAnywhere:**
   - Vai su **Web** → **Static files**
   - Verifica che il file `style.css` sia presente e aggiornato

2. **Nel browser:**
   - Premi `Ctrl + Shift + R` (Windows/Linux) o `Cmd + Shift + R` (Mac) per fare un hard refresh
   - Oppure svuota la cache del browser

## 🔧 Soluzione 2: Verifica che il CSS sia Caricato

1. Apri la console del browser (F12)
2. Vai alla tab **Network**
3. Ricarica la pagina
4. Cerca `style.css` e verifica che sia caricato (status 200)
5. Controlla che non ci siano errori 404

## 🔧 Soluzione 3: Forza il Reload del CSS

Aggiungi un parametro di versione al CSS nel template `base.html`:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}?v=2.0">
```

Oppure modifica direttamente il file CSS su PythonAnywhere aggiungendo in cima:

```css
/* Versione 2.0 - Fix pulsanti categoria */
```

Poi riavvia l'applicazione.

## 🔧 Soluzione 4: Verifica il File CSS

1. Su PythonAnywhere, apri il file `app/static/css/style.css`
2. Cerca `.category-button` e verifica che contenga:
   ```css
   opacity: 0 !important;
   visibility: hidden !important;
   pointer-events: none !important;
   display: none !important;
   ```
3. Cerca `.category-buttons.active .category-button` e verifica che contenga:
   ```css
   opacity: 1 !important;
   visibility: visible !important;
   display: flex !important;
   ```

## 🔧 Soluzione 5: Verifica JavaScript

1. Apri la console del browser (F12)
2. Controlla che non ci siano errori JavaScript
3. Verifica che la funzione `toggleCategoryButtons()` sia definita
4. Prova a eseguire manualmente: `toggleCategoryButtons()` nella console

## 🔧 Soluzione 6: Re-carica Tutti i File

Se nulla funziona, ricarica tutti i file modificati:

1. **File da ricaricare:**
   - `app/static/css/style.css`
   - `app/templates/main/lavori_admin.html`
   - `app/routes/main_routes.py`
   - `app/models.py`

2. **Dopo il caricamento:**
   - Riavvia l'applicazione (Web → Reload)
   - Svuota la cache del browser
   - Testa di nuovo

## ✅ Verifica Finale

Dopo aver applicato le correzioni, i pulsanti categoria dovrebbero:

- [ ] Essere completamente nascosti di default
- [ ] Apparire solo quando si clicca sul pulsante +
- [ ] Essere rotondi (non rettangolari)
- [ ] Avere sfondo bianco e bordo nero
- [ ] Illuminarsi di blu al hover

Se il problema persiste, controlla i log di errore su PythonAnywhere (Web → Error log).
