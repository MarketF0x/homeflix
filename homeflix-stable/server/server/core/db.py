from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from pathlib import Path
import os

# Racine du projet (2 niveaux au-dessus de ce fichier)
APP_ROOT = Path(__file__).resolve().parents[2]

# Fichier de base de données
# Priorité 1: Variable d'environnement DB_PATH (pour version STABLE avec BDD partagée)
# Priorité 2: Mode empaqueté (Electron) : resources/server/homeflix.db
# Priorité 3: Mode dev : homeflix/server/homeflix.db
if os.environ.get("DB_PATH"):
    # Utiliser la base de données partagée spécifiée par l'environnement
    DB_PATH = Path(os.environ["DB_PATH"])
    print(f"[DB] Utilisation base de donnees partagee (DB_PATH env): {DB_PATH}")
elif os.path.exists(Path(__file__).parent.parent / "homeflix.db"):
    # Mode empaqueté : resources/server/homeflix.db
    DB_PATH = Path(__file__).parent.parent / "homeflix.db"
else:
    # Mode dev : homeflix/server/homeflix.db
    DB_PATH = APP_ROOT / "server" / "homeflix.db"

print(f"[DB] Chemin base de donnees: {DB_PATH}")
print(f"[DB] Existe: {DB_PATH.exists()}")

# Configuration du moteur SQLAlchemy avec optimisations SQLite
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    future=True,
    # Pool de connexions optimisé pour SQLite
    poolclass=StaticPool,
    # Optimisations de connexion
    connect_args={
        "check_same_thread": False,  # Permet multi-threading
        "timeout": 30,  # Timeout de 30 secondes
    },
)


# Activer les optimisations SQLite à chaque connexion
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Active les optimisations SQLite pour chaque connexion."""
    cursor = dbapi_conn.cursor()
    # WAL mode pour meilleures performances en lecture/écriture
    cursor.execute("PRAGMA journal_mode=WAL")
    # Cache optimisé (2MB)
    cursor.execute("PRAGMA cache_size=-2000")
    # Synchronisation moins stricte pour performances
    cursor.execute("PRAGMA synchronous=NORMAL")
    # Optimisation mémoire temporaire
    cursor.execute("PRAGMA temp_store=MEMORY")
    # Analyse automatique pour optimiser les requêtes
    cursor.execute("PRAGMA optimize")
    cursor.close()


# Gestionnaire de sessions
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Classe de base pour les modèles
Base = declarative_base()


def init_db():
    """Crée les tables si elles n'existent pas déjà."""
    from . import models  # Assure l'import des modèles avant création
    Base.metadata.create_all(bind=engine)


def get_session():
    """Retourne une session de base de données.
    
    Important: Cette fonction retourne une session qui DOIT être fermée
    manuellement avec session.close() dans un bloc try/finally.
    """
    return SessionLocal()

