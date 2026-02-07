from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
import datetime
import os

Base = declarative_base()

class Athlete(Base):
    __tablename__ = 'athletes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    tax_code = Column(String, unique=True, nullable=False)
    birth_date = Column(Date)
    birth_place = Column(String)
    address = Column(String)
    phone = Column(String)
    email = Column(String)
    
    current_belt = Column(String)
    current_rank = Column(String)
    asc_number = Column(String)  # Numero tessera ASC
    roles = Column(String)      # Ruoli selezionati (separati da virgola)
    
    # Relationships
    certificates = relationship("MedicalCertificate", back_populates="athlete", cascade="all, delete-orphan", order_by="desc(MedicalCertificate.expiry_date)")
    ranks = relationship("Rank", back_populates="athlete", cascade="all, delete-orphan", order_by="desc(Rank.attainment_date)")

    @property
    def latest_certificate(self):
        return self.certificates[0] if self.certificates else None

class MedicalCertificate(Base):
    __tablename__ = 'medical_certificates'
    
    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey('athletes.id'))
    cert_type = Column(String)
    expiry_date = Column(Date, nullable=False)
    
    athlete = relationship("Athlete", back_populates="certificates")

class Rank(Base):
    __tablename__ = 'ranks'
    
    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey('athletes.id'))
    belt_color = Column(String, nullable=False)
    rank_name = Column(String)
    attainment_date = Column(Date, default=datetime.date.today)
    
    athlete = relationship("Athlete", back_populates="ranks")

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.engine = None
            cls._instance.SessionFactory = None
        return cls._instance

    def initialize(self, db_path):
        if self.engine:
            self.engine.dispose()
            
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        
        # Migrazione manuale per colonne aggiunte
        self._migrate_columns()
        
        self.SessionFactory = scoped_session(sessionmaker(bind=self.engine))
        print(f"Database inizializzato correttamente: {db_path}")

    def _migrate_columns(self):
        """Aggiunge colonne mancanti alla tabella athletes senza resettare il DB"""
        from sqlalchemy import text, inspect
        inspector = inspect(self.engine)
        columns = [c['name'] for c in inspector.get_columns('athletes')]
        
        with self.engine.connect() as conn:
            if 'asc_number' not in columns:
                try:
                    conn.execute(text("ALTER TABLE athletes ADD COLUMN asc_number VARCHAR"))
                    conn.commit()
                    print("Aggiunta colonna 'asc_number' con successo.")
                except Exception as e:
                    print(f"Errore migrazione asc_number: {e}")
            
            if 'roles' not in columns:
                try:
                    conn.execute(text("ALTER TABLE athletes ADD COLUMN roles VARCHAR"))
                    conn.commit()
                    print("Aggiunta colonna 'roles' con successo.")
                except Exception as e:
                    print(f"Errore migrazione roles: {e}")

    def get_session(self):
        if not self.SessionFactory:
            raise Exception("Database non inizializzato. Chiamare initialize() prima di get_session().")
        return self.SessionFactory()

    def sync_manual(self):
        """Previsione per sincronizzazione cloud futura"""
        print("Sincronizzazione manuale avviata (mock)...")
        # Qui andrebbe la logica di confronto con un server remoto
        return True

# Helper per mantenere compatibilità col codice esistente
def get_session():
    return DatabaseManager().get_session()
