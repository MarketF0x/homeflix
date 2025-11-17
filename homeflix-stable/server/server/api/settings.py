"""Routeur pour la gestion de la configuration."""
from fastapi import APIRouter, Body
from pathlib import Path
import yaml
import threading

from core.config_manager import load_settings
from core.scanner import scan_all

router = APIRouter(prefix="/api", tags=["settings"])


@router.get("/settings")
def get_settings():
    settings = load_settings()
    return {
        "language": getattr(settings, "language", "fr"),
        "video_directories": settings.video_directories if hasattr(settings, "video_directories") else [],
        "tmdb_api_key": getattr(settings, "tmdb_api_key", ""),
        "auto_clean_filenames": getattr(settings, "auto_clean_filenames", True),
        "min_film_minutes": settings.min_film_minutes,
        "max_series_minutes": settings.max_series_minutes,
        "session_mode": getattr(settings, "session_mode", "mixed"),
    }


@router.post("/settings")
def update_settings(payload: dict = Body(...)):
    settings_path = Path("settings.yaml")
    if settings_path.exists():
        config = yaml.safe_load(settings_path.read_text(encoding="utf-8")) or {}
    else:
        config = {}
    for key in [
        "language",
        "video_directories",
        "tmdb_api_key",
        "auto_clean_filenames",
        "min_film_minutes",
        "max_series_minutes",
        "session_mode",
    ]:
        if key in payload:
            config[key] = payload[key]
    settings_path.write_text(yaml.safe_dump(config, allow_unicode=True, default_flow_style=False), encoding="utf-8")
    if payload.get("rescan", False):
        threading.Thread(target=lambda: scan_all(load_settings()), daemon=True).start()
    return {
        "ok": True,
        "language": config.get("language", "fr"),
        "video_directories": config.get("video_directories", []),
        "tmdb_api_key": config.get("tmdb_api_key", ""),
        "auto_clean_filenames": config.get("auto_clean_filenames", True),
        "min_film_minutes": config.get("min_film_minutes", 75),
        "max_series_minutes": config.get("max_series_minutes", 55),
        "session_mode": config.get("session_mode", "mixed"),
        "message": "Configuration sauvegardée",
    }
