from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# Racine du projet (2 niveaux au-dessus de ce fichier)
APP_ROOT = Path(__file__).resolve().parents[2]

# Dossier où sera stockée la base SQLite
DATA_DIR = APP_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Fichier de base de données
DB_PATH = DATA_DIR / "homeone.db"

# Configuration du moteur SQLAlchemy
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)

# Gestionnaire de sessions
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Classe de base pour les modèles
Base = declarative_base()


def init_db():
    """Crée les tables si elles n'existent pas déjà."""
    from . import models  # Assure l'import des modèles avant création
    Base.metadata.create_all(bind=engine)


def get_session():
    """Retourne une session de base de données."""
    return SessionLocal()
