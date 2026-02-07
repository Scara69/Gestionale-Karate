from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLineEdit, QFrame, 
                             QMessageBox, QStackedWidget, QGridLayout, QComboBox,
                             QFormLayout, QGroupBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from qt_material import apply_stylesheet
from database import get_session, Athlete, MedicalCertificate, DatabaseManager
from athlete_dialog import AthleteDialog
from import_dialog import ImportDialog
import datetime
import sys
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestionale Karate ASD")
        self.setMinimumSize(1100, 750)
        
        # Load Settings
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_settings.json')
        self.settings = self.load_settings()
        
        # Database Initialization
        self.db_manager = DatabaseManager()
        db_path = self.settings.get("db_path")
        
        if not db_path or not os.path.exists(db_path):
            db_path = self.prompt_select_database()
            if not db_path:
                sys.exit(0) # Utente ha annullato
            self.settings["db_path"] = db_path
            self.save_settings_to_file()
            
        self.db_manager.initialize(db_path)
        
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setStyleSheet("background-color: #263238; border-right: 1px solid #37474f;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        title_label = QLabel("KARATE ASD")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #00bcd4;")
        sidebar_layout.addWidget(title_label)
        
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_athletes = QPushButton("Atleti")
        self.btn_certificates = QPushButton("Certificati")
        self.btn_settings = QPushButton("Impostazioni")
        
        for btn in [self.btn_dashboard, self.btn_athletes, self.btn_certificates, self.btn_settings]:
            btn.setCheckable(True)
            sidebar_layout.addWidget(btn)
        
        self.btn_dashboard.clicked.connect(lambda: self.switch_view(0))
        self.btn_athletes.clicked.connect(lambda: self.switch_view(1))
        self.btn_certificates.clicked.connect(lambda: self.switch_view(2))
        self.btn_settings.clicked.connect(lambda: self.switch_view(3))
        
        sidebar_layout.addStretch()
        main_layout.addWidget(self.sidebar)
        
        # Stacked Widget for Views
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Setup Views
        self.setup_dashboard_view()
        self.setup_athletes_view()
        self.setup_certificates_view()
        self.setup_settings_view()
        
        # Initial view
        self.load_initial_theme()
        self.switch_view(0)

    def switch_view(self, index):
        self.stack.setCurrentIndex(index)
        buttons = [self.btn_dashboard, self.btn_athletes, self.btn_certificates, self.btn_settings]
        for i, btn in enumerate(buttons):
            btn.setChecked(i == index)
        
        if index == 0: self.load_stats()
        elif index == 1: self.load_athletes()
        elif index == 2: self.load_certificates_filter()

    # --- VIEW SETUP METHODS ---

    def setup_settings_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        
        header = QLabel("Impostazioni")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Personaizzazione
        theme_group = QGroupBox("Personalizzazione Interfaccia")
        theme_layout = QFormLayout(theme_group)
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Tema Scuro (Teal)", "Tema Chiaro (Blue)"])
        current_theme = self.settings.get('theme', 'dark_teal.xml')
        self.combo_theme.setCurrentIndex(0 if "dark" in current_theme else 1)
        theme_layout.addRow("Seleziona Tema:", self.combo_theme)
        layout.addWidget(theme_group)

        # Gestione Database
        db_group = QGroupBox("Gestione Database")
        db_layout = QVBoxLayout(db_group)
        
        self.lbl_current_db = QLabel(f"Percorso Attuale: <b>{self.settings.get('db_path')}</b>")
        self.lbl_current_db.setWordWrap(True)
        db_layout.addWidget(self.lbl_current_db)
        
        db_btn_layout = QHBoxLayout()
        btn_change_db = QPushButton("Cambia / Ricollega Database")
        btn_change_db.clicked.connect(self.change_database)
        btn_sync_db = QPushButton("Sincronizza Ora (Cloud)")
        btn_sync_db.clicked.connect(self.sync_database)
        
        db_btn_layout.addWidget(btn_change_db)
        db_btn_layout.addWidget(btn_sync_db)
        db_layout.addLayout(db_btn_layout)
        layout.addWidget(db_group)
        
        btn_save = QPushButton("Salva Impostazioni")
        btn_save.setProperty('class', 'success')
        btn_save.clicked.connect(self.save_all_settings)
        layout.addWidget(btn_save)

        layout.addStretch()
        self.stack.insertWidget(3, view)

    def prompt_select_database(self):
        from PySide6.QtWidgets import QFileDialog
        msg = QMessageBox()
        msg.setWindowTitle("Inizializzazione Database")
        msg.setText("Seleziona un file database esistente o creane uno nuovo.")
        msg.setInformativeText("L'applicazione richiede un file .db per funzionare.")
        btn_open = msg.addButton("Apri Database Esistente", QMessageBox.ActionRole)
        btn_new = msg.addButton("Crea Nuovo Database", QMessageBox.ActionRole)
        btn_exit = msg.addButton("Esci", QMessageBox.RejectRole)
        msg.exec()
        
        if msg.clickedButton() == btn_open:
            path, _ = QFileDialog.getOpenFileName(self, "Apri Database", "", "Database Files (*.db)")
            return path
        elif msg.clickedButton() == btn_new:
            path, _ = QFileDialog.getSaveFileName(self, "Crea Nuovo Database", "karate_data.db", "Database Files (*.db)")
            return path
        return None

    def change_database(self):
        new_path = self.prompt_select_database()
        if new_path:
            self.settings["db_path"] = new_path
            self.db_manager.initialize(new_path)
            self.lbl_current_db.setText(f"Percorso Attuale: <b>{new_path}</b>")
            self.save_settings_to_file()
            self.load_stats()
            self.load_athletes()
            QMessageBox.information(self, "Successo", "Database ricollegato con successo!")

    def sync_database(self):
        if self.db_manager.sync_manual():
            QMessageBox.information(self, "Sincronizzazione", "Sincronizzazione completata! (Modalità: Locale)")
        else:
            QMessageBox.warning(self, "Errore", "Impossibile completare la sincronizzazione.")

    def save_all_settings(self):
        # Update theme based on combo (this is called from UI button)
        theme_idx = self.combo_theme.currentIndex()
        theme_name = 'dark_teal.xml' if theme_idx == 0 else 'light_blue.xml'
        self.settings["theme"] = theme_name
        self.save_settings_to_file()
        apply_stylesheet(QApplication.instance(), theme=theme_name)
        QMessageBox.information(self, "Impostazioni", "Impostazioni salvate correttamente!")

    def save_settings_to_file(self):
        import json
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_settings.json')
        with open(config_path, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def load_settings(self):
        import json
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_settings.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except: pass
        return {}

    def load_initial_theme(self):
        theme = self.settings.get('theme', 'dark_teal.xml')
        apply_stylesheet(QApplication.instance(), theme=theme)

    def setup_dashboard_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        
        header = QLabel("Dashboard")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        stats_layout = QGridLayout()
        
        self.card_total = self.create_stat_card("Totale Atleti", "0", "#00bcd4")
        self.card_agonisti = self.create_stat_card("Agonisti", "0", "#4caf50")
        self.card_non_agonisti = self.create_stat_card("Non Agonisti", "0", "#ff9800")
        self.card_expiring = self.create_stat_card("In Scadenza (30gg)", "0", "#f44336")
        
        stats_layout.addWidget(self.card_total, 0, 0)
        stats_layout.addWidget(self.card_agonisti, 0, 1)
        stats_layout.addWidget(self.card_non_agonisti, 1, 0)
        stats_layout.addWidget(self.card_expiring, 1, 1)
        
        layout.addLayout(stats_layout)
        layout.addStretch()
        self.stack.insertWidget(0, view)

    def setup_certificates_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        
        header = QLabel("Gestione Certificati")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Mostra scadenze entro:"))
        
        self.combo_cert_filter = QComboBox()
        self.combo_cert_filter.addItems(["Prossimi 30 giorni", "Prossimi 60 giorni", "Prossimi 90 giorni", "Tutti i scaduti"])
        self.combo_cert_filter.currentIndexChanged.connect(self.load_certificates_filter)
        filter_layout.addWidget(self.combo_cert_filter)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        self.cert_table = QTableWidget()
        self.cert_table.setColumnCount(5)
        self.cert_table.setHorizontalHeaderLabels(["Atleta", "Tipo", "Data Scadenza", "Telefono", "Email"])
        self.cert_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.cert_table.horizontalHeader().setStretchLastSection(True)
        self.cert_table.setSortingEnabled(True)
        layout.addWidget(self.cert_table)
        
        self.stack.insertWidget(2, view)

    def create_stat_card(self, title, value, color):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"background-color: #37474f; border-left: 5px solid {color}; border-radius: 5px;")
        card.setMinimumHeight(150)
        
        layout = QVBoxLayout(card)
        t_label = QLabel(title)
        t_label.setStyleSheet("font-size: 16px; color: #b0bec5;")
        v_label = QLabel(value)
        v_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        
        layout.addWidget(t_label)
        layout.addWidget(v_label)
        return card

    def update_card_value(self, card, value):
        for child in card.findChildren(QLabel):
            if "32px" in child.styleSheet():
                child.setText(str(value))

    def setup_athletes_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        
        header_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cerca per nome, cognome o CF...")
        self.search_bar.textChanged.connect(self.load_athletes)
        header_layout.addWidget(self.search_bar)
        
        # New Column Visibility Button
        self.btn_columns = QPushButton("Colonne")
        self.btn_columns.setFixedWidth(100)
        self.btn_columns.clicked.connect(self.show_column_menu)
        header_layout.addWidget(self.btn_columns)

        btn_add = QPushButton("Aggiungi Atleta")
        btn_add.setProperty('class', 'success')
        btn_add.clicked.connect(self.add_athlete)
        header_layout.addWidget(btn_add)
        
        self.btn_import = QPushButton("Importa Dati")
        self.btn_import.clicked.connect(self.import_data)
        header_layout.addWidget(self.btn_import)
        
        layout.addLayout(header_layout)
        
        # Table Configuration
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionsMovable(True)
        self.table.horizontalHeader().sectionMoved.connect(self.on_column_moved)
        self.table.cellDoubleClicked.connect(self.on_row_double_clicked)
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        
        layout.addWidget(self.table)
        
        # Default Columns Internal Metadata
        self.all_columns = [
            {"key": "id", "label": "#", "fixed": True},
            {"key": "surname", "label": "Cognome", "fixed": True},
            {"key": "name", "label": "Nome", "fixed": True},
            {"key": "birth_date", "label": "Data Nascita"},
            {"key": "birth_place", "label": "Luogo Nascita"},
            {"key": "tax_code", "label": "Codice Fiscale"},
            {"key": "current_belt", "label": "Cintura"},
            {"key": "current_rank", "label": "Grado"},
            {"key": "address", "label": "Indirizzo"},
            {"key": "phone", "label": "Telefono"},
            {"key": "email", "label": "Email"},
            {"key": "asc_number", "label": "Numero ASC"},
            {"key": "roles", "label": "Ruoli"},
            {"key": "scadenza", "label": "Scad. Cert."},
        ]
        
        # Load visibility settings
        self.visible_keys = self.settings.get("visible_columns")
        if not self.visible_keys:
            self.visible_keys = ["id", "surname", "name", "current_belt", "current_rank", "scadenza"]
            
        # Load order settings
        self.col_order = self.settings.get("column_order")
        
        self.stack.insertWidget(1, view)

    def show_column_menu(self):
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction
        menu = QMenu(self)
        for col in self.all_columns:
            if col.get("fixed"): continue
            
            action = QAction(col["label"], menu, checkable=True)
            action.setChecked(col["key"] in self.visible_keys)
            action.triggered.connect(lambda checked, k=col["key"]: self.toggle_column(k, checked))
            menu.addAction(action)
        
        menu.exec(self.btn_columns.mapToGlobal(self.btn_columns.rect().bottomLeft()))

    def toggle_column(self, key, visible):
        if visible and key not in self.visible_keys:
            self.visible_keys.append(key)
        elif not visible and key in self.visible_keys:
            self.visible_keys.remove(key)
        
        self.settings["visible_columns"] = self.visible_keys
        self.save_settings_to_file()
        self.load_athletes()

    def on_column_moved(self, logicalIndex, oldVisualIndex, newVisualIndex):
        # We need to save the visual order
        header = self.table.horizontalHeader()
        count = header.count()
        new_order = []
        for i in range(count):
            logical_idx = header.logicalIndex(i)
            # Find which key this matches
            col_label = self.table.horizontalHeaderItem(logical_idx).text()
            for col in self.all_columns:
                if col["label"] == col_label:
                    new_order.append(col["key"])
                    break
        
        # Ensure # is always first if moved by user (actually header move doesn't force this easily, 
        # but we can check if index 0 changed)
        if new_order and new_order[0] != "id":
             # We could force it back or just let it be. User asked: "numero progressivo deve rimanere sempre la prima"
             # Let's force it back visually if it moved
             visual_idx_of_id = header.visualIndex(0) # 0 is logical index for #
             if visual_idx_of_id != 0:
                 header.moveSection(visual_idx_of_id, 0)
                 return # Recurse once
        
        self.settings["column_order"] = new_order
        self.save_settings_to_file()

    def on_row_double_clicked(self, row, column):
        # Dynamically find the index of the '#' (id) column to get the athlete ID
        logical_index_of_id = -1
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            if self.table.horizontalHeaderItem(i).text() == "#":
                logical_index_of_id = i
                break
        
        if logical_index_of_id != -1:
            item = self.table.item(row, logical_index_of_id)
            if item:
                athlete_id = item.data(Qt.UserRole)
                if athlete_id:
                    self.edit_athlete(athlete_id)

    # --- LOGIC METHODS ---

    def load_stats(self):
        session = get_session()
        total = session.query(Athlete).count()
        agonisti = session.query(MedicalCertificate).filter(MedicalCertificate.cert_type == "Agonistico").count()
        non_agonisti = session.query(MedicalCertificate).filter(MedicalCertificate.cert_type == "Non Agonistico").count()
        
        today = datetime.date.today()
        next_30 = today + datetime.timedelta(days=30)
        expiring = session.query(MedicalCertificate).filter(MedicalCertificate.expiry_date.between(today, next_30)).count()
        
        self.update_card_value(self.card_total, total)
        self.update_card_value(self.card_agonisti, agonisti)
        self.update_card_value(self.card_non_agonisti, non_agonisti)
        self.update_card_value(self.card_expiring, expiring)
        session.close()

    def add_athlete(self):
        dialog = AthleteDialog(self)
        if dialog.exec():
            self.load_athletes()
            self.load_stats()

    def import_data(self):
        dialog = ImportDialog(self)
        if dialog.exec():
            self.load_athletes()
            self.load_stats()

    def edit_athlete(self, athlete_id):
        dialog = AthleteDialog(self, athlete_id=athlete_id)
        result = dialog.exec()
        if result:
            self.load_athletes()
            self.load_stats()

    def load_athletes(self):
        session = get_session()
        query = session.query(Athlete)
        
        search_text = self.search_bar.text()
        if search_text:
            query = query.filter(
                (Athlete.name.ilike(f"%{search_text}%")) | 
                (Athlete.surname.ilike(f"%{search_text}%")) |
                (Athlete.tax_code.ilike(f"%{search_text}%"))
            )
            
        athletes = query.all()
        
        # Determine current visible columns in order
        current_cols = []
        if self.col_order:
             # Follow saved order but filter for visibility
             for k in self.col_order:
                 if k in self.visible_keys:
                     for col in self.all_columns:
                         if col["key"] == k:
                             current_cols.append(col)
                             break
             # Add any new visibility keys that weren't in order yet
             for k in self.visible_keys:
                 if k not in [c["key"] for c in current_cols]:
                      for col in self.all_columns:
                         if col["key"] == k:
                             current_cols.append(col)
                             break
        else:
            # Default order
            for col in self.all_columns:
                if col["key"] in self.visible_keys:
                    current_cols.append(col)

        # IMPORTANT: Disable sorting and clear table for data integrity
        self.table.setSortingEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(0)
        
        self.table.setColumnCount(len(current_cols))
        self.table.setHorizontalHeaderLabels([c["label"] for c in current_cols])
        self.table.setRowCount(len(athletes))
        
        for i, athlete in enumerate(athletes):
            for col_idx, col_cfg in enumerate(current_cols):
                key = col_cfg["key"]
                
                if key == "id":
                    val = str(i + 1)
                elif key == "scadenza":
                    cert = athlete.latest_certificate
                    val = cert.expiry_date.strftime("%d/%m/%Y") if cert else "Assente"
                else:
                    val = getattr(athlete, key, "")
                
                item = QTableWidgetItem(str(val if val is not None else ""))
                
                # Highlight Key Fields
                if key in ["name", "surname"]:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    item.setForeground(Qt.cyan) # Aesthetic highlight
                
                # Scadenza Colors
                if key == "scadenza" and athlete.latest_certificate:
                    cert = athlete.latest_certificate
                    if cert.expiry_date < datetime.date.today():
                        item.setForeground(Qt.red)
                    elif cert.expiry_date < datetime.date.today() + datetime.timedelta(days=30):
                        item.setForeground(Qt.yellow)
                
                # Store Real ID for double click on the '#' column (key == "id")
                if key == "id":
                    item.setData(Qt.UserRole, athlete.id)
                
                self.table.setItem(i, col_idx, item)
        
        # Re-enable sorting after data is stable
        self.table.setSortingEnabled(True)
        session.close()

    def load_certificates_filter(self):
        session = get_session()
        today = datetime.date.today()
        idx = self.combo_cert_filter.currentIndex()
        
        query = session.query(MedicalCertificate).join(Athlete)
        
        if idx == 0: # 30 days
            query = query.filter(MedicalCertificate.expiry_date.between(today, today + datetime.timedelta(days=30)))
        elif idx == 1: # 60 days
            query = query.filter(MedicalCertificate.expiry_date.between(today, today + datetime.timedelta(days=60)))
        elif idx == 2: # 90 days
            query = query.filter(MedicalCertificate.expiry_date.between(today, today + datetime.timedelta(days=90)))
        elif idx == 3: # Expired
            query = query.filter(MedicalCertificate.expiry_date < today)
            
        certs = query.order_by(MedicalCertificate.expiry_date).all()
        self.cert_table.setRowCount(len(certs))
        
        for i, cert in enumerate(certs):
            athlete = cert.athlete
            self.cert_table.setItem(i, 0, QTableWidgetItem(f"{athlete.name} {athlete.surname}"))
            self.cert_table.setItem(i, 1, QTableWidgetItem(cert.cert_type))
            self.cert_table.setItem(i, 2, QTableWidgetItem(cert.expiry_date.strftime("%d/%m/%Y")))
            self.cert_table.setItem(i, 3, QTableWidgetItem(athlete.phone or "-"))
            self.cert_table.setItem(i, 4, QTableWidgetItem(athlete.email or "-"))
        
        session.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
