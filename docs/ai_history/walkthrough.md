# Walkthrough - Sezione Dati Associativi

Ho implementato la nuova sezione "Dati Associativi" per permettere la gestione del numero di tessera ASC e dei ruoli dell'atleta.

## Cambiamenti apportati

### 1. Database
Ho aggiornato il modello `Athlete` in [database.py](file:///C:/Users/Simone/.gemini/antigravity/scratch/Gestionale%20Karate/database.py) aggiungendo i campi:
- `asc_number`: Stringa per il numero di tessera.
- `roles`: Stringa separata da virgola per memorizzare i ruoli selezionati.

### 2. Migrazione Automatica
Ho implementato un meccanismo di migrazione automatica in `DatabaseManager._migrate_columns()`. All'avvio, l'applicazione controlla se le nuove colonne esistono nel database SQLite e, se mancanti, le aggiunge automaticamente tramite comandi `ALTER TABLE`. Questo evita errori di "colonna mancante" su database esistenti.

### 3. Interfaccia Dettaglio Atleta
In [athlete_dialog.py](file:///C:/Users/Simone/.gemini/antigravity/scratch/Gestionale%20Karate/athlete_dialog.py), ho aggiunto il gruppo "Dati Associativi" che include:
- Un campo di testo per il **Numero Tessera ASC**.
- Checkbox per la selezione multipla dei **Ruoli** (Atleta, Praticante, Dirigente, Agonista).

### 4. Importazione Dati
Ho esteso la maschera di importazione CSV/Excel in [import_dialog.py](file:///C:/Users/Simone/.gemini/antigravity/scratch/Gestionale%20Karate/import_dialog.py) per includere:
- **Mapping**: Ora è possibile associare le colonne del file ai campi "Numero Tessera ASC" e "Ruoli".
- **Gestione Conflitti**: In [conflict_dialog.py](file:///C:/Users/Simone/.gemini/antigravity/scratch/Gestionale%20Karate/conflict_dialog.py), i nuovi campi sono ora inclusi nel confronto per la risoluzione manuale dei conflitti.

### 5. Tabella Principale
In [main.py](file:///C:/Users/Simone/.gemini/antigravity/scratch/Gestionale%20Karate/main.py), ho aggiunto le nuove colonne "Numero ASC" e "Ruoli" alla configurazione della tabella. Gli utenti possono ora visualizzare queste informazioni attivandone la visibilità dal pulsante "Colonne".

## Verifica Effettuata

1.  **Inserimento Dati**: Ho aggiunto/modificato un atleta impostando il numero ASC "12345" e selezionando i ruoli "Atleta" e "Agonista"
2.  **Persistenza**: Salvando e riaprendo il dialogo, i dati risultano correttamente caricati.
3.  **Visualizzazione**: Attivando le colonne nella tabella principale, i dati vengono visualizzati correttamente (i ruoli appaiono come "Atleta,Agonista").

---

# Guida alla Sincronizzazione Multi-Postazione

Questa guida spiega come gestire il progetto **Gestionale Karate** su più computer senza perdere dati o progressi.

## 1. Stato Attuale Versionamento (Git)
Ho già configurato Git per te:
- **Inizializzato** il repository locale.
- **Creato** il file `.gitignore` e `requirements.txt`.
- **Eseguito il primo commit** con tutti i file del progetto (esclusi quelli ignorati).

Per collegarlo a GitHub e sincronizzarlo online:
1.  Crea un repository vuoto su GitHub (chiamalo `Gestionale-Karate`).
2.  Nel terminale del progetto, incolla questi comandi:
    ```bash
    git remote add origin https://github.com/Scara69/Gestionale-Karate.git
    git branch -M main
    git push -u origin main
    ```

## 2. Ambiente di Sviluppo
Su ogni nuova macchina, segui questi passi:
1.  Clona il repository: `git clone <url-repo>`
2.  Crea l'ambiente virtuale: `python -m venv venv`
3.  Attivalo e installa le dipendenze: `pip install -r requirements.txt`

## 3. Gestione Database locale
I file `.db` sono esclusi dal versionamento (per sicurezza e dimensione).
- **Opzione A**: Copia manualmente `karate_data.db` tramite chiavetta o cloud drive.
- **Opzione B**: Configura un database cloud (es. MongoDB o PostgreSQL) se desideri una sincronizzazione in tempo reale.

## 4. Persistenza Storia AI (Chat e Decisioni)
Per non perdere la storia delle conversazioni e i piani di sviluppo:
1.  Ho creato la cartella `docs/ai_history/`.
2.  **Copia periodica**: Ti consiglio di copiare i file dalla cartella di sistema di Antigravity nella cartella `docs/ai_history/` del progetto prima di fare il `git push`.
    - Percorso origine: `C:\Users\Simone\.gemini\antigravity\brain\9002a805-386b-4303-8475-89cebce119bf\`
    - In questo modo, chiunque cloni il repo avrà accesso ai `walkthrough.md` e `implementation_plan.md`.

> [!TIP]
> Esegui sempre `git pull` all'inizio e `git push` alla fine di ogni sessione di lavoro!
