from pathlib import Path
from ruamel.yaml import YAML
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import io

# Racine du projet
APP_ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = APP_ROOT / "settings.yaml"


class Settings(BaseModel):
    """Structure des paramètres généraux de HomeOne."""
    session_mode: str = Field(default="mixed")
    # Utilise la clé YAML historique "video_directories" (alias) pour la compatibilité.
    video_directories: List[str] = Field(default_factory=list, alias="video_directories")
    min_film_minutes: int = Field(default=75, ge=0)
    max_series_minutes: int = Field(default=55, ge=0)
    tmdb_api_key: Optional[str] = Field(default=None)
    auto_clean_filenames: bool = Field(default=True)
    language: str = Field(default="fr")

    @validator("session_mode")
    def validate_session_mode(cls, v):
        if v not in ["mixed", "films", "series"]:
            raise ValueError('session_mode doit être "mixed", "films" ou "series"')
        return v

    @validator("video_directories")
    def validate_video_dirs(cls, dirs):
        valid_dirs = []
        for dir_path in dirs:
            path = Path(dir_path)
            if path.exists() and path.is_dir():
                valid_dirs.append(str(path.absolute()))
        return valid_dirs


_yaml = YAML(typ="safe")


def load_settings() -> Settings:
    """Charge les paramètres depuis le fichier YAML."""
    if not SETTINGS_PATH.exists():
        settings = Settings()
        save_settings(settings)
        return settings
    try:
        data = _yaml.load(SETTINGS_PATH.read_text(encoding="utf-8")) or {}
        # Supporte indifféremment video_dirs et video_directories en entrée
        if "video_dirs" in data and "video_directories" not in data:
            data["video_directories"] = data.pop("video_dirs")
        return Settings(**data)
    except Exception as e:
        print(f"[ERREUR] Impossible de charger settings.yaml : {e}")
        return Settings()


def save_settings(settings: Settings) -> bool:
    """Sauvegarde les paramètres dans le fichier YAML."""
    try:
        stream = io.StringIO()
        # Écrit en utilisant les alias (video_directories)
        _yaml.dump(settings.dict(by_alias=True), stream)
        text = stream.getvalue()
        SETTINGS_PATH.write_text(text, encoding="utf-8")
        return True
    except Exception as e:
        print(f"[ERREUR] Impossible de sauvegarder settings.yaml : {e}")
        return False
