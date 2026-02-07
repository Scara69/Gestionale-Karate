# Implementation Plan - Associative Data Section

Add a new section to the athlete's details and update the import functionality to support ASC membership information and administrative/athletic roles.

## User Review Required

> [!IMPORTANT]
> **Data Persistence**: Roles will be saved as a multi-selection. If an athlete has multiple roles, they will all be preserved.
> **Extensibility**: The system is designed to allow adding more roles in the future easily.

## Proposed Changes

### [Database]
- **[MODIFY]** `database.py`:
    - Add `asc_number` (String) to the `Athlete` model.
    - Add `roles` (String) to the `Athlete` model to store selected roles (e.g., as a separated string).

### [Athlete Dialog]
- **[MODIFY]** `athlete_dialog.py`:
    - **UI**: Add a new `QGroupBox` titled "DATI ASSOCIATIVI".
    - **Fields**: Include a `QLineEdit` for the ASC number and a set of `QCheckBox` for roles ("Atleta", "Praticante", "Dirigente", "Agonista").
    - **Logic**: Update `load_athlete_data` to read these values and `save_athlete` to persist them.

### [Main Table]
- **[MODIFY]** `main.py`:
    - Update `all_columns` configuration to include "Numero ASC" and "Ruoli", allowing users to show them in the main table if desired.

### [Import Functionality]
- **[MODIFY]** `import_dialog.py`:
    - Add "Numero di tessera ASC" and "Ruoli" to the mapping dictionary.
- **[MODIFY]** `conflict_dialog.py`:
    - Add "asc_number" and "roles" to the fields compared during manual conflict resolution.

## Verification Plan

### Manual Verification
1.  Open an athlete's profile.
2.  Fill in the ASC number and select multiple roles (e.g., Atleta and Dirigente).
3.  Save and reopen: verify that all selections are correctly loaded.
4.  In the main table, use the "Colonne" button to show the new "Ruoli" and "Numero ASC" columns: verify they display correctly.
5.  **Import Test**: Import a CSV file containing ASC numbers and roles. Verify that the mapping works and data is imported correctly, including conflict resolution.
