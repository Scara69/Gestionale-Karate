import pandas as pd
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QTableWidget, QTableWidgetItem, 
                             QComboBox, QFormLayout, QGroupBox, QMessageBox, QProgressBar)
from PySide6.QtCore import Qt
import datetime
from database import get_session, Athlete, MedicalCertificate, DatabaseManager
from cf_utils import parse_cf, get_comune_name
from conflict_dialog import ConflictDialog
from global_conflict_dialog import GlobalConflictDialog

class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Importa Dati Atleti")
        self.setMinimumSize(600, 500)
        
        self.df = None
        self.mapping = {}
        self.db_fields = {
            "Nome": "name",
            "Cognome": "surname",
            "Codice Fiscale": "tax_code",
            "Data di Nascita": "birth_date",
            "Luogo di Nascita": "birth_place",
            "Indirizzo": "address",
            "Telefono": "phone",
            "Email": "email",
            "Tipo Certificato": "cert_type",
            "Scadenza Certificato": "cert_expiry",
            "Colore Cintura": "current_belt",
            "Grado": "current_rank",
            "Numero Tessera ASC": "asc_number",
            "Ruoli": "roles"
        }
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # File Selection
        file_layout = QHBoxLayout()
        self.lbl_file = QLabel("Nessun file selezionato")
        btn_browse = QPushButton("Sfoglia...")
        btn_browse.clicked.connect(self.browse_file)
        file_layout.addWidget(self.lbl_file)
        file_layout.addWidget(btn_browse)
        layout.addLayout(file_layout)
        
        # Mapping Group
        self.group_mapping = QGroupBox("Mappatura Colonne")
        self.mapping_form = QFormLayout(self.group_mapping)
        self.combos = {}
        
        for label, key in self.db_fields.items():
            combo = QComboBox()
            combo.addItem("- Non Importare -")
            self.mapping_form.addRow(label, combo)
            self.combos[key] = combo
            
        layout.addWidget(self.group_mapping)
        self.group_mapping.setEnabled(False)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_import = QPushButton("Importa Ora")
        self.btn_import.setEnabled(False)
        self.btn_import.clicked.connect(self.start_import)
        
        btn_cancel = QPushButton("Chiudi")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_import)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleziona File", "", "File Dati (*.csv *.xlsx *.xls)"
        )
        if not file_path:
            return
            
        try:
            if file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
            else:
                self.df = pd.read_excel(file_path)
            
            self.lbl_file.setText(file_path.split('/')[-1])
            self.populate_combos()
            self.group_mapping.setEnabled(True)
            self.btn_import.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile leggere il file: {str(e)}")

    def populate_combos(self):
        columns = self.df.columns.tolist()
        for key, combo in self.combos.items():
            combo.clear()
            combo.addItem("- Non Importare -")
            combo.addItems(columns)
            
            # Try auto-mapping by name
            for col in columns:
                if col.lower() in [key.lower(), self.get_label_for_key(key).lower()]:
                    combo.setCurrentText(col)
                    break

    def get_label_for_key(self, key):
        for label, k in self.db_fields.items():
            if k == key: return label
        return ""

    def start_import(self):
        # Validate critical fields
        if self.combos["name"].currentIndex() == 0 or self.combos["surname"].currentIndex() == 0:
            QMessageBox.warning(self, "Attenzione", "Le colonne Nome e Cognome sono obbligatorie per l'importazione.")
            return

        self.progress.setVisible(True)
        self.progress.setMaximum(len(self.df))
        
        session = get_session()
        
        # 0. PRE-CHECK FOR CONFLICTS
        conflicts_found = []
        rows_to_process = []
        
        for index, row in self.df.iterrows():
            # Prepare row data
            row_data = {}
            for key, combo in self.combos.items():
                col = combo.currentText()
                if col == "- Non Importare -" or pd.isna(row[col]): continue
                val = row[col]
                if key in ["birth_date", "cert_expiry"]:
                    if not isinstance(val, (datetime.date, datetime.datetime)):
                        try: val = pd.to_datetime(val).date()
                        except: pass
                if key == "tax_code": val = str(val).strip().upper()
                row_data[key] = val
            
            # Extract from CF
            if "tax_code" in row_data:
                cf_data = parse_cf(row_data["tax_code"])
                if cf_data:
                    if "birth_date" not in row_data or not row_data["birth_date"]:
                        row_data["birth_date"] = cf_data["birth_date"]
                    if "birth_place" not in row_data or not row_data["birth_place"]:
                        row_data["birth_place"] = get_comune_name(cf_data["comune_code"])

            rows_to_process.append(row_data)
            
            # Identify conflict
            if "tax_code" in row_data:
                athlete = session.query(Athlete).filter_by(tax_code=row_data["tax_code"]).first()
                if athlete:
                    has_diff = False
                    for k, v in row_data.items():
                        if k in ["cert_type", "cert_expiry"]: continue
                        db_val = getattr(athlete, k, None)
                        if str(db_val or "").strip().lower() != str(v or "").strip().lower() and str(v or "").strip() != "":
                            has_diff = True
                            break
                    if has_diff:
                        conflicts_found.append((index, athlete, row_data))

        strategy = "manual"
        if len(conflicts_found) > 0:
            global_diag = GlobalConflictDialog(len(conflicts_found), self)
            if global_diag.exec() == QDialog.Accepted:
                strategy = global_diag.strategy
            else:
                return # User cancelled

        # 1. ACTUAL IMPORT LOOP
        count = 0
        errors = 0
        
        for index, row_data in enumerate(rows_to_process):
            try:
                athlete = None
                if "tax_code" in row_data:
                    athlete = session.query(Athlete).filter_by(tax_code=row_data["tax_code"]).first()
                
                is_conflict = any(c[0] == index for c in conflicts_found)
                
                if athlete and is_conflict:
                    if strategy == "overwrite_all":
                        for k, v in row_data.items():
                            if k not in ["cert_type", "cert_expiry"] and hasattr(athlete, k):
                                setattr(athlete, k, v)
                    elif strategy == "keep_current":
                        pass # Don't update athlete fields
                    else: # manual
                        diag = ConflictDialog(f"{athlete.name} {athlete.surname}", athlete, row_data, self)
                        if diag.exec() == QDialog.Accepted:
                            merged = diag.get_final_data()
                            for k, v in merged.items():
                                setattr(athlete, k, v)
                        else:
                            self.progress.setValue(index + 1)
                            continue
                elif not athlete:
                    athlete = Athlete()
                    session.add(athlete)
                    for k, v in row_data.items():
                        if k not in ["cert_type", "cert_expiry"] and hasattr(athlete, k):
                            setattr(athlete, k, v)
                
                # Certificate handling (same logic as before)
                ctype = row_data.get("cert_type", "Agonistico")
                expiry = row_data.get("cert_expiry")
                if expiry:
                    session.flush()
                    existing_cert = session.query(MedicalCertificate).filter_by(athlete_id=athlete.id).order_by(MedicalCertificate.expiry_date.desc()).first()
                    if existing_cert:
                        if existing_cert.expiry_date < expiry:
                            existing_cert.cert_type = ctype
                            existing_cert.expiry_date = expiry
                    else:
                        new_cert = MedicalCertificate(cert_type=ctype, expiry_date=expiry, athlete_id=athlete.id)
                        session.add(new_cert)

                count += 1
            except Exception as e:
                print(f"Error importing row {index}: {e}")
                errors += 1
            
            self.progress.setValue(index + 1)
            
        try:
            session.commit()
            QMessageBox.information(self, "Fine Importazione", f"Completato! Importati/Aggiornati {count} atleti.\nErrori: {errors}")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio: {e}")
        finally:
            session.close()
