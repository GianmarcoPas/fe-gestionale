# Changelog

## [2026-01-22] - Modifiche e Correzioni

### 🔧 Correzioni

#### Gestione Utenti
- **Rimosso reset automatico password**: Modificato `run.py` e `app/__init__.py` per evitare il reset automatico delle password degli utenti ad ogni avvio del server
- **Script di inizializzazione utenti**: Creato `init_users.py` come script standalone per inizializzare/resettare manualmente gli utenti con la password predefinita "Ciao1234"
- **Utenti predefiniti**: Configurati gli utenti admin (Roberto, Lucio, Giuseppe, Carmela) e base (Gianmarco, Francescos, Francescou, Giovanni, Marco) con password predefinita

#### Visualizzazione Compensi
- **Formattazione valori zero**: Modificata la visualizzazione dei compensi per mostrare "-" invece di "€ 0,00" quando il valore è zero o nullo
  - Applicato a: Overlay Compensi (visualizzazione standard e extra2/focus), Tabella Focus, Tabella Scroll (extra1)
  - Campi interessati: FE, AMIN, GALVAN, FH, BIANC, DELOITTE, Ext, Rev, Caricamento

#### Sincronizzazione Overlay con Filtri
- **Sincronizzazione automatica**: Implementata la sincronizzazione degli overlay (Compensi, Fatture, Procacciatori) con i filtri applicati alla tabella principale
- **Aggiunto data-id**: Aggiunto attributo `data-id` a tutte le righe degli overlay per facilitare la sincronizzazione
- **Funzione `syncOverlaysWithFilters()`**: Creata funzione JavaScript per sincronizzare automaticamente gli overlay quando si applicano filtri, ricerche o selezioni di redattore
- **Funzione `recalculateOverlayRowspans()`**: Creata funzione per ricalcolare correttamente i rowspan negli overlay dopo il filtraggio

#### Correzione Rowspan con Filtri
- **Ricalcolo rowspan migliorato**: Corretta la funzione `recalculateRowspans()` per gestire correttamente i rowspan quando si applicano filtri o ricerche
- **Gestione ordine DOM**: Assicurato che la prima riga (con i rowspan) sia sempre la prima riga visibile nell'ordine DOM dopo il filtraggio
- **Correzione struttura tabella**: Risolto il problema di scombinamento delle righe quando si applicano filtri, ricerche o selezioni di redattore
- **Miglioramento `applyAllFilters()`**: Aggiunta logica per assicurare che la prima riga sia sempre visibile se ci sono righe visibili del lavoro

### 📝 File Modificati

#### Backend
- `app/__init__.py`: Rimosso reset automatico password, mantenuta solo inizializzazione utenti se non esistono
- `run.py`: Rimosso reset automatico password, mantenuta solo inizializzazione utenti se non esistono
- `init_users.py`: Creato nuovo script per inizializzazione/reset manuale utenti

#### Frontend
- `app/templates/main/lavori_admin.html`:
  - Modificata formattazione compensi per mostrare "-" invece di "€ 0,00" quando valore è zero
  - Aggiunto attributo `data-id` a tutte le righe degli overlay
  - Creata funzione `syncOverlaysWithFilters()` per sincronizzare overlay con filtri
  - Creata funzione `recalculateOverlayRowspans()` per ricalcolare rowspan negli overlay
  - Migliorata funzione `recalculateRowspans()` per gestire correttamente filtri e ricerche
  - Migliorata funzione `applyAllFilters()` per assicurare ordine corretto delle righe
  - Aggiunto CSS per nascondere righe filtrate anche negli overlay (`.overlay-table tbody tr.filtered-out`)

### 🎯 Risultati

- ✅ Le password degli utenti non vengono più resettate ad ogni avvio del server
- ✅ I compensi con valore zero sono più facilmente distinguibili (mostrano "-")
- ✅ Gli overlay si aggiornano automaticamente quando si applicano filtri o ricerche
- ✅ La struttura della tabella rimane corretta anche dopo l'applicazione di filtri complessi
- ✅ I rowspan vengono ricalcolati correttamente in base alle righe visibili

### 📋 Note Tecniche

- La sincronizzazione degli overlay funziona basandosi sull'attributo `data-id` delle righe
- Il ricalcolo dei rowspan tiene conto solo delle righe visibili (non filtrate)
- La prima riga di ogni lavoro viene sempre mantenuta visibile se ci sono righe visibili del lavoro stesso
- L'ordine delle righe nel DOM viene preservato durante il filtraggio
