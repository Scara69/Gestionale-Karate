from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QCheckBox, QHeaderView)
from PySide6.QtCore import Qt

class ConflictDialog(QDialog):
    def __init__(self, athlete_name, db_data, import_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Conflitto Dati: {athlete_name}")
        self.setMinimumSize(700, 400)
        
        self.db_data = db_data
        self.import_data = import_data
        self.results = {} # Will store chosen values
        
        layout = QVBoxLayout(self)
        
        info_lbl = QLabel(f"Sono state riscontrate discrepanze per l'atleta <b>{athlete_name}</b>.<br>"
                         "Seleziona quali dati importati vuoi utilizzare per sovrascrivere quelli attuali.")
        info_lbl.setWordWrap(True)
        layout.addWidget(info_lbl)
        
        # Table of discrepancies
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Campo", "Database Attuale", "Dato Importato", "Sovrascrivi?"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        fields_to_compare = {
            "name": "Nome",
            "surname": "Cognome",
            "birth_date": "Data Nascita",
            "birth_place": "Luogo Nascita",
            "address": "Indirizzo",
            "phone": "Telefono",
            "email": "Email",
            "current_belt": "Cintura",
            "current_rank": "Grado",
            "asc_number": "Numero ASC",
            "roles": "Ruoli"
        }
        
        row = 0
        for key, label in fields_to_compare.items():
            db_val = str(getattr(db_data, key) or "")
            imp_val = str(import_data.get(key) or "")
            
            # Case insensitive comparison for strings, or direct for others
            if db_val.strip().lower() != imp_val.strip().lower() and imp_val.strip() != "":
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(label))
                self.table.setItem(row, 1, QTableWidgetItem(db_val))
                self.table.setItem(row, 2, QTableWidgetItem(imp_val))
                
                check_box = QCheckBox()
                check_box.setChecked(True) # Default to overwrite if there's a difference? 
                # Or keep DB by default? Let's default to Checked (Imported) as per request "possibile sovrascrivere"
                container = QHBoxLayout()
                center_widget = QLabel() # Just to hold the layout
                container.addWidget(check_box)
                container.setAlignment(Qt.AlignCenter)
                container.setContentsMargins(0,0,0,0)
                
                cell_widget = QCheckBox()
                cell_widget.setChecked(True)
                
                # Using a workaround for checkbox in cell
                self.table.setCellWidget(row, 3, cell_widget)
                
                # Store references to retrieve results later
                self.results[key] = (imp_val, cell_widget)
                row += 1
                
        layout.addWidget(self.table)
        
        if row == 0:
            # No real differences found after all?
            self.accept()
            
        # Buttons
        btn_layout = QHBoxLayout()
        btn_confirm = QPushButton("Conferma Scelte")
        btn_confirm.clicked.connect(self.accept)
        btn_confirm.setProperty("class", "success")
        
        btn_skip = QPushButton("Ignora Record")
        btn_skip.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_confirm)
        btn_layout.addWidget(btn_skip)
        layout.addLayout(btn_layout)

    def get_final_data(self):
        final_mapping = {}
        for key, (val, checkbox) in self.results.items():
            if checkbox.isChecked():
                final_mapping[key] = val
        return final_mapping
