from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QDateEdit, QComboBox, QPushButton, 
                             QLabel, QGroupBox, QMessageBox, QCheckBox)
from PySide6.QtCore import QDate, Qt
from database import Athlete, MedicalCertificate, Rank, get_session
import datetime

class AthleteDialog(QDialog):
    def __init__(self, parent=None, athlete_id=None):
        super().__init__(parent)
        self.athlete_id = athlete_id
        self.setWindowTitle("Aggiungi Atleta" if not athlete_id else "Modifica Atleta")
        self.setMinimumWidth(450)
        
        self.layout = QVBoxLayout(self)
        
        # Dati Personali
        personal_group = QGroupBox("Dati Personali")
        personal_form = QFormLayout(personal_group)
        
        self.name_input = QLineEdit()
        self.surname_input = QLineEdit()
        self.tax_code_input = QLineEdit()
        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(QDate.currentDate().addYears(-10))
        
        self.birth_place_input = QLineEdit()
        
        self.address_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        
        personal_form.addRow("Nome:", self.name_input)
        personal_form.addRow("Cognome:", self.surname_input)
        personal_form.addRow("Codice Fiscale:", self.tax_code_input)
        personal_form.addRow("Data di Nascita:", self.birth_date_input)
        personal_form.addRow("Luogo di Nascita:", self.birth_place_input)
        personal_form.addRow("Indirizzo:", self.address_input)
        personal_form.addRow("Telefono:", self.phone_input)
        personal_form.addRow("Email:", self.email_input)
        
        self.layout.addWidget(personal_group)
        
        # Certificato Medico
        medical_group = QGroupBox("Certificato Medico")
        medical_form = QFormLayout(medical_group)
        
        self.cert_type_input = QComboBox()
        self.cert_type_input.addItems(["Agonistico", "Non Agonistico", "Nessuno"])
        
        self.cert_expiry_input = QDateEdit()
        self.cert_expiry_input.setCalendarPopup(True)
        self.cert_expiry_input.setDate(QDate.currentDate().addYears(1))
        
        medical_form.addRow("Tipo Certificato:", self.cert_type_input)
        medical_form.addRow("Data Scadenza:", self.cert_expiry_input)
        
        self.layout.addWidget(medical_group)
        
        # Grado e Cintura
        rank_group = QGroupBox("Grado Tecnico")
        rank_form = QFormLayout(rank_group)
        
        self.belt_input = QComboBox()
        self.belt_input.addItems([
            "Bianca", "Gialla", "Arancione", "Verde", 
            "Blu", "Marrone", "Nera"
        ])
        
        self.rank_input = QLineEdit()
        self.rank_input.setPlaceholderText("es. 1° Dan, 3° Kyu")
        
        rank_form.addRow("Colore Cintura:", self.belt_input)
        rank_form.addRow("Grado:", self.rank_input)
        
        self.layout.addWidget(rank_group)

        # Dati Associativi
        assoc_group = QGroupBox("Dati Associativi")
        assoc_form = QFormLayout(assoc_group)
        
        self.asc_number_input = QLineEdit()
        assoc_form.addRow("Numero Tessera ASC:", self.asc_number_input)
        
        roles_layout = QHBoxLayout()
        self.role_atleta = QCheckBox("Atleta")
        self.role_praticante = QCheckBox("Praticante")
        self.role_dirigente = QCheckBox("Dirigente")
        self.role_agonista = QCheckBox("Agonista")
        
        roles_layout.addWidget(self.role_atleta)
        roles_layout.addWidget(self.role_praticante)
        roles_layout.addWidget(self.role_dirigente)
        roles_layout.addWidget(self.role_agonista)
        assoc_form.addRow("Ruoli:", roles_layout)
        
        self.layout.addWidget(assoc_group)
        
        # Bottoni
        button_layout = QHBoxLayout()
        
        if self.athlete_id:
            self.btn_delete = QPushButton("Elimina Atleta")
            self.btn_delete.setProperty('class', 'danger')
            self.btn_delete.clicked.connect(self.delete_athlete)
            button_layout.addWidget(self.btn_delete)
        
        button_layout.addStretch()
        
        self.btn_save = QPushButton("Salva")
        self.btn_save.clicked.connect(self.save_athlete)
        self.btn_cancel = QPushButton("Annulla")
        self.btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        self.layout.addLayout(button_layout)
        
        if self.athlete_id:
            self.load_athlete_data()

    def delete_athlete(self):
        reply = QMessageBox.question(self, "Conferma Eliminazione", 
                                   "Sei sicuro di voler eliminare definitivamente questo atleta?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            session = get_session()
            athlete = session.query(Athlete).filter_by(id=self.athlete_id).first()
            if athlete:
                session.delete(athlete)
                session.commit()
            session.close()
            self.done(2) # Custom return code for deletion

    def load_athlete_data(self):
        session = get_session()
        athlete = session.query(Athlete).filter_by(id=self.athlete_id).first()
        if athlete:
            self.name_input.setText(athlete.name)
            self.surname_input.setText(athlete.surname)
            self.tax_code_input.setText(athlete.tax_code)
            if athlete.birth_date:
                self.birth_date_input.setDate(QDate(athlete.birth_date.year, athlete.birth_date.month, athlete.birth_date.day))
            self.birth_place_input.setText(athlete.birth_place or "")
            self.address_input.setText(athlete.address or "")
            self.phone_input.setText(athlete.phone or "")
            self.email_input.setText(athlete.email or "")
            
            self.belt_input.setCurrentText(athlete.current_belt or "Bianca")
            self.rank_input.setText(athlete.current_rank or "")
            
            # New fields
            self.asc_number_input.setText(athlete.asc_number or "")
            roles = (athlete.roles or "").split(",")
            self.role_atleta.setChecked("Atleta" in roles)
            self.role_praticante.setChecked("Praticante" in roles)
            self.role_dirigente.setChecked("Dirigente" in roles)
            self.role_agonista.setChecked("Agonista" in roles)
            
            cert = athlete.latest_certificate
            if cert:
                self.cert_type_input.setCurrentText(cert.cert_type)
                self.cert_expiry_input.setDate(QDate(cert.expiry_date.year, cert.expiry_date.month, cert.expiry_date.day))
        session.close()

    def save_athlete(self):
        if not self.name_input.text() or not self.surname_input.text() or not self.tax_code_input.text():
            QMessageBox.warning(self, "Errore", "Nome, Cognome e Codice Fiscale sono obbligatori.")
            return
            
        session = get_session()
        try:
            if self.athlete_id:
                athlete = session.query(Athlete).filter_by(id=self.athlete_id).first()
            else:
                athlete = Athlete()
                session.add(athlete)
            
            athlete.name = self.name_input.text()
            athlete.surname = self.surname_input.text()
            athlete.tax_code = self.tax_code_input.text().upper()
            
            bd = self.birth_date_input.date()
            athlete.birth_date = datetime.date(bd.year(), bd.month(), bd.day())
            
            athlete.birth_place = self.birth_place_input.text()
            athlete.address = self.address_input.text()
            athlete.phone = self.phone_input.text()
            athlete.email = self.email_input.text()
            athlete.current_belt = self.belt_input.currentText()
            athlete.current_rank = self.rank_input.text()
            
            # New fields
            athlete.asc_number = self.asc_number_input.text()
            selected_roles = []
            if self.role_atleta.isChecked(): selected_roles.append("Atleta")
            if self.role_praticante.isChecked(): selected_roles.append("Praticante")
            if self.role_dirigente.isChecked(): selected_roles.append("Dirigente")
            if self.role_agonista.isChecked(): selected_roles.append("Agonista")
            athlete.roles = ",".join(selected_roles)
            
            # Handle Certificate (simplified: create or update most recent)
            cert_type = self.cert_type_input.currentText()
            if cert_type != "Nessuno":
                ed = self.cert_expiry_input.date()
                expiry = datetime.date(ed.year(), ed.month(), ed.day())
                
                if athlete.id and athlete.certificates:
                    latest = athlete.certificates[0]
                    latest.cert_type = cert_type
                    latest.expiry_date = expiry
                else:
                    new_cert = MedicalCertificate(cert_type=cert_type, expiry_date=expiry)
                    athlete.certificates.append(new_cert)
            
            session.commit()
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Errore Salvataggio", f"Si è verificato un errore: {str(e)}")
        finally:
            session.close()
