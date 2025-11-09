"""Routeur pour les miniatures: get, generate, repair."""
from fastapi import APIRouter, Query, Body
from pathlib import Path

from core.db import get_session
from core.models import Video
from core.thumbnails import get_thumbnail as _get_thumbnail, ensure_thumbnail_sync, thumb_path_for

router = APIRouter(prefix="/api", tags=["thumbnails"])


@router.get("/thumbnail")
def thumbnail(path: str = Query(...)):
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
