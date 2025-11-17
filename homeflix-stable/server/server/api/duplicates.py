"""
API pour la gestion des fichiers en doublon
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from pathlib import Path
import os
from collections import defaultdict

from core.db import SessionLocal
from core.models import Video
from core.logger import logger

router = APIRouter()


class DeleteDuplicatesRequest(BaseModel):
    """Requête pour supprimer des doublons"""
    file_paths: List[str]


def normalize_title(title: str) -> str:
    """Normalise un titre pour la comparaison"""
    # Retirer les extensions, espaces, underscores, tirets
    normalized = title.lower()
    normalized = normalized.replace("_", " ").replace("-", " ")
    # Retirer les caractères spéciaux courants
    for char in [".", "(", ")", "[", "]", "{", "}"]:
        normalized = normalized.replace(char, " ")
    # Retirer les espaces multiples
    normalized = " ".join(normalized.split())
    return normalized.strip()


@router.get("/duplicates")
async def find_duplicates():
    """
    Trouve tous les fichiers en doublon basés sur le nom du film
    Retourne un dictionnaire avec le titre normalisé comme clé
    et la liste des fichiers comme valeur
    """
    try:
        db = SessionLocal()
        videos = db.query(Video).all()
        db.close()
        
        # Grouper par titre normalisé
        groups = defaultdict(list)
        for video in videos:
            # Extraire le nom du fichier sans extension
            file_path = Path(video.path)
            file_name = file_path.stem  # Nom sans extension
            normalized = normalize_title(file_name)
            
            # Stocker les informations du fichier
            file_info = {
                "id": video.id,
                "path": video.path,
                "title": video.title,
                "file_name": file_name,
                "file_size": video.file_size or 0,
                "duration": video.duration,
                "resolution": video.resolution,
                "last_position": video.last_position or 0,
                "year": video.year
            }
            groups[normalized].append(file_info)
        
        # Ne garder que les groupes avec plusieurs fichiers
        duplicates = {}
        for normalized_title, files in groups.items():
            if len(files) > 1:
                # Trier par taille de fichier (décroissant) pour aider l'utilisateur
                files.sort(key=lambda x: x["file_size"], reverse=True)
                duplicates[normalized_title] = files
        
        logger.info(f"Trouvé {len(duplicates)} groupes de doublons")
        
        return {
            "duplicates": duplicates,
            "total_groups": len(duplicates),
            "total_files": sum(len(files) for files in duplicates.values())
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de doublons: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/duplicates/delete")
async def delete_duplicates(request: DeleteDuplicatesRequest):
    """
    Supprime définitivement les fichiers spécifiés
    """
    try:
        db = SessionLocal()
        deleted_files = []
        errors = []
        
        for file_path in request.file_paths:
            try:
                # Vérifier que le fichier existe
                if not os.path.exists(file_path):
                    errors.append(f"Fichier introuvable: {file_path}")
                    continue
                
                # Supprimer le fichier physique
                os.remove(file_path)
                logger.info(f"Fichier supprimé: {file_path}")
                
                # Supprimer de la base de données
                video = db.query(Video).filter(Video.path == file_path).first()
                if video:
                    db.delete(video)
                    db.commit()
                
                deleted_files.append(file_path)
                
            except Exception as e:
                error_msg = f"Erreur lors de la suppression de {file_path}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        db.close()
        
        return {
            "success": True,
            "deleted_count": len(deleted_files),
            "deleted_files": deleted_files,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression des doublons: {e}")
        raise HTTPException(status_code=500, detail=str(e))
