"""Routeur pour les miniatures: get, generate, repair."""
from fastapi import APIRouter, Query, Body
from fastapi.responses import FileResponse
from pathlib import Path

from core.db import get_session
from core.models import Video
from core.thumbnails import get_thumbnail as _get_thumbnail, ensure_thumbnail_sync, thumb_path_for, THUMB_DIR

router = APIRouter(prefix="/api", tags=["thumbnails"])


@router.get("/thumbnail")
def thumbnail(path: str = Query(...), direct: int = Query(0)):
    """
    Retourne une miniature.
    - Si direct=1 et path est juste un nom de fichier, cherche dans data/thumbs/
    - Sinon utilise le système normal de génération de miniatures
    Supporte WebP et JPEG automatiquement.
    """
    
    if direct == 1:
        # Mode direct: chercher dans data/thumbs/
        thumb_path = THUMB_DIR / path
        if thumb_path.exists():
            # Déterminer le type MIME en fonction de l'extension
            media_type = "image/webp" if thumb_path.suffix.lower() == ".webp" else "image/jpeg"
            return FileResponse(
                thumb_path, 
                media_type=media_type,
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                }
            )
    
    return _get_thumbnail(path)


@router.post("/thumbnails/generate")
def generate_thumbnails(payload: dict | None = Body(None)):
    force = bool(payload.get("force", False)) if payload else False
    stats = {"total": 0, "generated": 0, "skipped": 0, "errors": 0}
    with get_session() as s:
        videos = s.query(Video).all()
        stats["total"] = len(videos)
        for v in videos:
            try:
                vpath = Path(v.path)
                tpath = thumb_path_for(vpath)
                if tpath.exists() and not force:
                    stats["skipped"] += 1
                    continue
                ok = ensure_thumbnail_sync(str(vpath), force=force)
                if ok:
                    stats["generated"] += 1
                else:
                    stats["errors"] += 1
            except Exception:
                stats["errors"] += 1
    return {"ok": True, **stats}


@router.post("/thumbnails/repair")
def repair_thumbnails():
    stats = {"total": 0, "missing": 0, "generated": 0, "failed": 0}
    with get_session() as s:
        videos = s.query(Video).all()
        stats["total"] = len(videos)
        for v in videos:
            try:
                vpath = Path(v.path)
                tpath = thumb_path_for(vpath)
                if tpath.exists():
                    continue
                stats["missing"] += 1
                ok = ensure_thumbnail_sync(str(vpath), force=True)
                if ok:
                    stats["generated"] += 1
                else:
                    stats["failed"] += 1
            except Exception:
                stats["failed"] += 1
    return {"ok": True, **stats}
