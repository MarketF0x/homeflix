"""
API pour l'exploration du système de fichiers
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List, Dict
import os
import string

router = APIRouter()


@router.get("/browse")
async def browse_directory(path: str = None):
    """
    Liste les dossiers d'un répertoire donné
    Si path est None, retourne les lecteurs disponibles (Windows) ou /home (Linux/Mac)
    """
    try:
        if not path:
            # Pas de chemin spécifié : retourner les lecteurs/racines
            if os.name == 'nt':  # Windows
                drives = []
                for letter in string.ascii_uppercase:
                    drive = f"{letter}:\\"
                    if os.path.exists(drive):
                        drives.append({
                            "name": drive,
                            "path": drive,
                            "type": "drive"
                        })
                return {"current_path": "", "items": drives}
            else:  # Linux/Mac
                path = "/"
        
        # Normaliser le chemin
        current_path = Path(path).resolve()
        
        if not current_path.exists():
            raise HTTPException(status_code=404, detail="Le chemin n'existe pas")
        
        if not current_path.is_dir():
            raise HTTPException(status_code=400, detail="Le chemin n'est pas un dossier")
        
        # Lister uniquement les dossiers
        items = []
        try:
            for item in sorted(current_path.iterdir()):
                if item.is_dir():
                    try:
                        # Vérifier si on a accès au dossier
                        list(item.iterdir())
                        items.append({
                            "name": item.name,
                            "path": str(item),
                            "type": "folder"
                        })
                    except PermissionError:
                        # Dossier sans permission, on l'ajoute quand même mais marqué
                        items.append({
                            "name": item.name,
                            "path": str(item),
                            "type": "folder",
                            "locked": True
                        })
        except PermissionError:
            raise HTTPException(status_code=403, detail="Permission refusée")
        
        # Ajouter le parent si ce n'est pas la racine
        parent = None
        if current_path.parent != current_path:
            parent = str(current_path.parent)
        
        return {
            "current_path": str(current_path),
            "parent": parent,
            "items": items
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
