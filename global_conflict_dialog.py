from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class GlobalConflictDialog(QDialog):
    def __init__(self, conflict_count, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rilevazione Conflitti Importazione")
        self.setFixedWidth(500)
        
        self.choice = "manual" # Default
        
        layout = QVBoxLayout(self)
        
        msg = QLabel(f"Sono stati rilevati <b>{conflict_count}</b> record in conflitto (già presenti nel database ma con dati diversi).<br><br>"
                    "Come desideri procedere?")
        msg.setWordWrap(True)
        layout.addWidget(msg)
        
        btn_overwrite = QPushButton("Sovrascrivi TUTTI i record esistenti")
        btn_overwrite.clicked.connect(lambda: self.set_choice("overwrite_all"))
        
        btn_keep = QPushButton("Mantieni TUTTI i dati attuali (salta modifiche)")
        btn_keep.clicked.connect(lambda: self.set_choice("keep_current"))
        
        btn_manual = QPushButton("Gestisci conflitti singolarmente (uno per uno)")
        btn_manual.clicked.connect(lambda: self.set_choice("manual"))
        btn_manual.setDefault(True)
        
        layout.addWidget(btn_overwrite)
        layout.addWidget(btn_keep)
        layout.addWidget(btn_manual)
        
        layout.addSpacing(20)
        
        btn_cancel = QPushButton("Annulla l'intera importazione")
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

    def set_choice(self, choice):
        self.choice = choice
        self.accept()

    @property
    def strategy(self):
        return self.choice
