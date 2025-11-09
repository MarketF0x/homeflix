"""Routeur vidéo: listing, recherche, random, update, progress, stream."""
from fastapi import APIRouter, HTTPException, Query, Body
from pathlib import Path
import random
from typing import Literal, List

from core.db import get_session
from core.models import Video
from core.config_manager import load_settings
from core.player import open_with_default
from core.thumbnails import get_thumbnail, ensure_thumbnail_sync, thumb_path_for

SessionMode = Literal["mixed", "films", "series"]

router = APIRouter(prefix="/api", tags=["videos"])


def _filter_by_mode(videos: List[Video], mode: SessionMode, min_film=75, max_series=55):
    if mode == "films":
        return [v for v in videos if (v.duration_seconds or 0) >= (min_film * 60)]
    if mode == "series":
        return [v for v in videos if 20 * 60 <= (v.duration_seconds or 0) <= (max_series * 60)]
    return videos


@router.get("/videos")
def list_videos(
    mode: SessionMode = Query("mixed"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None)
):
    with get_session() as s:
        query = s.query(Video).order_by(Video.title.asc())
        if search:
            query = query.filter(Video.title.ilike(f"%{search}%"))
        items = query.all()
        settings = load_settings()
        filtered = _filter_by_mode(items, mode, settings.min_film_minutes, settings.max_series_minutes)
        total = len(filtered)
        paginated = filtered[skip:skip + limit]
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "videos": [
                {
                    "id": v.id,
                    "title": v.title,
                    "path": v.path,
                    "duration_seconds": v.duration_seconds,
                    "size": v.size,
                    "year": v.year,
                    "genre": v.genre,
                    "watched": v.watched,
                    "last_position": v.last_position,
                }
                for v in paginated
            ],
        }


@router.get("/random")
def random_video(mode: SessionMode = Query("mixed")):
    with get_session() as s:
        items = s.query(Video).all()
        if not items:
            raise HTTPException(status_code=404, detail="Aucune vidéo dans la bibliothèque")
        settings = load_settings()
        filtered = _filter_by_mode(items, mode, settings.min_film_minutes, settings.max_series_minutes)
        if not filtered:
            raise HTTPException(status_code=404, detail=f"Aucune vidéo trouvée pour le mode '{mode}'")
        video = random.choice(filtered)
        return {
            "id": video.id,
            "title": video.title,
            "path": video.path,
            "duration_seconds": video.duration_seconds,
            "size": video.size,
            "year": video.year,
            "genre": video.genre,
            "watched": video.watched,
            "last_position": video.last_position,
        }


@router.post("/open")
def open_video(payload: dict = Body(...)):
    path = payload.get("path")
    video_id = payload.get("id")
    if not path:
        raise HTTPException(status_code=400, detail="Le champ 'path' est requis.")
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Le fichier est introuvable : {p}")
    if video_id:
        with get_session() as s:
            video = s.query(Video).filter(Video.id == video_id).first()
            if video:
                video.watched = True
                s.commit()
    open_with_default(p)
    return {"ok": True}


@router.post("/progress")
def save_progress(payload: dict = Body(...)):
    video_id = payload.get("id")
    position = payload.get("position", 0)
    if not video_id:
        raise HTTPException(status_code=400, detail="ID de la vidéo requis")
    with get_session() as s:
        video = s.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Vidéo introuvable")
        video.last_position = position
        if video.duration_seconds and position > video.duration_seconds * 0.9:
            video.watched = True
        s.commit()
    return {"ok": True, "position": position}


@router.post("/video/update")
def update_video(payload: dict = Body(...)):
    video_id = payload.get("id")
    if not video_id:
        raise HTTPException(status_code=400, detail="Le champ 'id' est requis.")
    with get_session() as s:
        video = s.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Vidéo introuvable.")
        if "watched" in payload:
            video.watched = bool(payload["watched"])
        if "last_position" in payload:
            video.last_position = int(payload["last_position"])
        if "year" in payload:
            video.year = payload["year"]
        if "genre" in payload:
            video.genre = payload["genre"]
        s.commit()
        return {
            "ok": True,
            "id": video.id,
            "watched": video.watched,
            "last_position": video.last_position,
            "year": video.year,
            "genre": video.genre,
        }
