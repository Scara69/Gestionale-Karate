# Riorganizzazione Layout AthleteDialog

L'obiettivo è trasformare il layout da una singola colonna verticale a due colonne orizzontali per migliorare l'usabilità su schermi con risoluzione verticale limitata.

## Modifiche Proposte

### [Component: UI]

#### [MODIFY] [athlete_dialog.py](file:///c:/Users/Gloria/.gemini/antigravity/Gestionale-Karate/athlete_dialog.py)

- Introdurre un `QHBoxLayout` come contenitore principale (sotto il titolo se presente, o come layout base).
- Creare due `QVBoxLayout` per rappresentare le due colonne.
- **Colonna 1 (Sinistra):**
    - `personal_group` (Dati Personali) - questo è il gruppo più lungo.
- **Colonna 2 (Destra):**
    - `medical_group` (Certificato Medico)
    - `rank_group` (Grado Tecnico)
    - `assoc_group` (Dati Associativi)
    - `note_group` (Note)
- Aggiungere uno `stretch` in fondo alla colonna 2 se necessario per allineare i gruppi verso l'alto.
- Aumentare la larghezza minima della finestra (`setMinimumWidth`) per accomodare le due colonne (es. da 450 a 800-900).

## Piano di Verifica

### Verifica Manuale
- Aprire la finestra di aggiunta/modifica atleta.
- Verificare che tutti i campi siano visibili senza eccessivo scrolling.
- Verificare che il layout rimanga armonioso ridimensionando la finestra.
