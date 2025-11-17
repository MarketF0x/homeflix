"""
API pour la gestion des profils utilisateurs
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import sqlite3
import json
import hashlib
from pathlib import Path
from PIL import Image
import io
import base64
import uuid
import httpx
from core.logger import logger, log_exception

router = APIRouter()

DB_PATH = Path(__file__).parent.parent / "homeflix.db"
CUSTOM_AVATARS_DIR = Path(__file__).parent.parent / "static" / "custom_avatars"
CUSTOM_AVATARS_DIR.mkdir(parents=True, exist_ok=True)


def hash_password(password: str) -> str:
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


class ProfileCreate(BaseModel):
    name: str
    avatar: str
    is_main: bool = False
    restrictions: dict = {}
    security_question: Optional[str] = None
    security_answer: Optional[str] = None  # La réponse devient le mot de passe


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    restrictions: Optional[dict] = None
    old_password: Optional[str] = None  # Requis pour changer le mot de passe
    security_question: Optional[str] = None
    security_answer: Optional[str] = None  # La réponse devient le nouveau mot de passe


class PasswordVerify(BaseModel):
    profile_id: int
    password: str


class PasswordReset(BaseModel):
    profile_id: int
    security_answer: str  # La réponse devient le nouveau mot de passe


def get_db_connection():
    """Retourne une connexion à la base de données"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/profiles")
def get_profiles():
    """Récupère tous les profils (sans les mots de passe)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, avatar, is_main, restrictions, 
                   security_question, created_at,
                   CASE WHEN password_hash IS NOT NULL THEN 1 ELSE 0 END as has_password
            FROM profiles
            ORDER BY is_main DESC, created_at ASC
        """)
        
        profiles = []
        for row in cursor.fetchall():
            profiles.append({
                "id": row["id"],
                "name": row["name"],
                "avatar": row["avatar"],
                "is_main": bool(row["is_main"]),
                "restrictions": json.loads(row["restrictions"]) if row["restrictions"] else {},
                "security_question": row["security_question"],
                "has_password": bool(row["has_password"]),
                "created_at": row["created_at"]
            })
        
        conn.close()
        return {"ok": True, "profiles": profiles}
        
    except Exception as e:
        log_exception(e, context="get_profiles")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profiles")
def create_profile(profile: ProfileCreate):
    """Crée un nouveau profil"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier qu'il n'y a pas déjà un profil principal
        if profile.is_main:
            cursor.execute("SELECT COUNT(*) as count FROM profiles WHERE is_main = 1")
            if cursor.fetchone()["count"] > 0:
                conn.close()
                raise HTTPException(
                    status_code=400, 
                    detail="Un profil principal existe déjà"
                )
        
        # Si une question et réponse sont fournies, la réponse devient le mot de passe
        password_hash = None
        security_answer_hash = None
        if profile.security_question and profile.security_answer:
            password_hash = hash_password(profile.security_answer)
            security_answer_hash = hash_password(profile.security_answer)
        
        # Insérer le nouveau profil
        cursor.execute("""
            INSERT INTO profiles (name, avatar, is_main, restrictions, password_hash, security_question, security_answer)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.name,
            profile.avatar,
            1 if profile.is_main else 0,
            json.dumps(profile.restrictions),
            password_hash,
            profile.security_question,
            security_answer_hash
        ))
        
        profile_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Profil créé: {profile.name} (ID: {profile_id})")
        
        return {
            "ok": True,
            "profile": {
                "id": profile_id,
                "name": profile.name,
                "avatar": profile.avatar,
                "is_main": profile.is_main,
                "restrictions": profile.restrictions
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_exception(e, context="create_profile")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profiles/{profile_id}")
def update_profile(profile_id: int, profile: ProfileUpdate):
    """Met à jour un profil existant"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier que le profil existe
        cursor.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
        existing = cursor.fetchone()
        if not existing:
            conn.close()
            raise HTTPException(status_code=404, detail="Profil non trouvé")
        
        # Si on veut changer le mot de passe, vérifier l'ancien
        if profile.security_answer and existing["password_hash"]:
            if not profile.old_password:
                conn.close()
                raise HTTPException(status_code=400, detail="L'ancien mot de passe est requis")
            
            old_hash = hash_password(profile.old_password)
            if old_hash != existing["password_hash"]:
                conn.close()
                raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")
        
        # Construire la requête de mise à jour
        updates = []
        params = []
        
        if profile.name is not None:
            updates.append("name = ?")
            params.append(profile.name)
        
        if profile.avatar is not None:
            updates.append("avatar = ?")
            params.append(profile.avatar)
        
        if profile.restrictions is not None:
            updates.append("restrictions = ?")
            params.append(json.dumps(profile.restrictions))
        
        # Si question et réponse fournies, la réponse devient le nouveau mot de passe
        if profile.security_question and profile.security_answer:
            updates.append("password_hash = ?")
            params.append(hash_password(profile.security_answer))
            
            updates.append("security_question = ?")
            params.append(profile.security_question)
            
            updates.append("security_answer = ?")
            params.append(hash_password(profile.security_answer))
        
        if not updates:
            conn.close()
            return {"ok": True, "message": "Aucune modification"}
        
        params.append(profile_id)
        query = f"UPDATE profiles SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Profil mis à jour: ID {profile_id}")
        
        return {"ok": True, "message": "Profil mis à jour"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_exception(e, context="update_profile")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/profiles/{profile_id}")
def delete_profile(profile_id: int):
    """Supprime un profil"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier que le profil existe et n'est pas le profil principal
        cursor.execute("SELECT is_main FROM profiles WHERE id = ?", (profile_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Profil non trouvé")
        
        if row["is_main"]:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="Le profil principal ne peut pas être supprimé"
            )
        
        # Supprimer le profil
        cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Profil supprimé: ID {profile_id}")
        
        return {"ok": True, "message": "Profil supprimé"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_exception(e, context="delete_profile")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profiles/verify-password")
def verify_password(data: PasswordVerify):
    """Vérifie le mot de passe d'un profil"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT password_hash FROM profiles WHERE id = ?", (data.profile_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Profil non trouvé")
        
        if not row["password_hash"]:
            # Pas de mot de passe défini
            return {"ok": True, "valid": True}
        
        # Vérifier le mot de passe
        password_hash = hash_password(data.password)
        valid = password_hash == row["password_hash"]
        
        return {"ok": True, "valid": valid}
        
    except HTTPException:
        raise
    except Exception as e:
        log_exception(e, context="verify_password")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profiles/reset-password")
def reset_password(data: PasswordReset):
    """Réinitialise le mot de passe avec la réponse à la question secrète (la réponse devient le nouveau mot de passe)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT security_question, security_answer FROM profiles WHERE id = ?", 
            (data.profile_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Profil non trouvé")
        
        if not row["security_question"]:
            conn.close()
            return {"ok": False, "message": "Aucune question secrète définie"}
        
        # La réponse fournie devient le nouveau mot de passe ET la nouvelle réponse secrète
        answer_hash = hash_password(data.security_answer)
        
        cursor.execute(
            "UPDATE profiles SET password_hash = ?, security_answer = ? WHERE id = ?",
            (answer_hash, answer_hash, data.profile_id)
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Mot de passe réinitialisé via question secrète - Profil #{data.profile_id}")
        
        return {"ok": True, "message": "Mot de passe réinitialisé"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_exception(e, context="reset_password")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{profile_id}/security-question")
def get_security_question(profile_id: int):
    """Récupère la question secrète d'un profil"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT security_question FROM profiles WHERE id = ?", (profile_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Profil non trouvé")
        
        return {
            "ok": True,
            "question": row["security_question"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_exception(e, context="get_security_question")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ENDPOINTS POUR MASQUAGE DE VIDÉOS ====================

class HideVideoRequest(BaseModel):
    profile_id: int
    video_id: int


@router.post("/profiles/hide-video")
def hide_video(data: HideVideoRequest):
    """Masque une vidéo pour un profil spécifique"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier que le profil existe
        cursor.execute("SELECT is_main FROM profiles WHERE id = ?", (data.profile_id,))
        profile = cursor.fetchone()
        
        if not profile:
            conn.close()
            raise HTTPException(status_code=404, detail="Profil non trouvé")
        
        # Vérifier que ce n'est pas le profil principal
        if profile["is_main"]:
            conn.close()
            raise HTTPException(
                status_code=400, 
                detail="Le profil principal ne peut pas masquer de vidéos"
            )
        
        # Ajouter ou ignorer si déjà masquée
        cursor.execute("""
            INSERT OR IGNORE INTO hidden_videos (profile_id, video_id)
            VALUES (?, ?)
        """, (data.profile_id, data.video_id))
        
        conn.commit()
        was_new = cursor.rowcount > 0
        conn.close()
        
        if was_new:
            logger.info(f"✅ Vidéo #{data.video_id} masquée pour le profil #{data.profile_id}")
        
        return {"ok": True, "message": "Vidéo masquée"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_exception(e, context="hide_video")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profiles/unhide-video")
def unhide_video(data: HideVideoRequest):
    """Affiche à nouveau une vidéo masquée pour un profil"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM hidden_videos 
            WHERE profile_id = ? AND video_id = ?
        """, (data.profile_id, data.video_id))
        
        conn.commit()
        was_deleted = cursor.rowcount > 0
        conn.close()
        
        if was_deleted:
            logger.info(f"✅ Vidéo #{data.video_id} affichée pour le profil #{data.profile_id}")
        
        return {"ok": True, "message": "Vidéo affichée"}
        
    except Exception as e:
        log_exception(e, context="unhide_video")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{profile_id}/hidden-videos")
def get_hidden_videos(profile_id: int):
    """Récupère la liste des IDs de vidéos masquées pour un profil"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT video_id, hidden_at 
            FROM hidden_videos 
            WHERE profile_id = ?
            ORDER BY hidden_at DESC
        """, (profile_id,))
        
        hidden = []
        for row in cursor.fetchall():
            hidden.append({
                "video_id": row["video_id"],
                "hidden_at": row["hidden_at"]
            })
        
        conn.close()
        
        return {"ok": True, "hidden_videos": hidden}
        
    except Exception as e:
        log_exception(e, context="get_hidden_videos")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profiles/upload-avatar")
async def upload_custom_avatar(file: Optional[UploadFile] = File(None), url: Optional[str] = Form(None)):
    """
    Upload un avatar personnalisé depuis un fichier local ou une URL
    Redimensionne automatiquement l'image à 200x200px
    """
    try:
        image_data = None
        
        # Si c'est un fichier uploadé
        if file:
            logger.info(f"Upload avatar depuis fichier: {file.filename}")
            image_data = await file.read()
        
        # Si c'est une URL
        elif url:
            logger.info(f"Upload avatar depuis URL: {url}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail="Impossible de télécharger l'image depuis l'URL")
                image_data = response.content
        
        else:
            raise HTTPException(status_code=400, detail="Aucun fichier ou URL fourni")
        
        # Ouvrir l'image avec PIL
        try:
            image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Format d'image non valide: {str(e)}")
        
        # Convertir en RGB si nécessaire (pour les PNG avec transparence)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Créer un fond blanc
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Redimensionner à 200x200 (format carré des avatars)
        image = image.resize((200, 200), Image.Resampling.LANCZOS)
        
        # Générer un nom de fichier unique
        filename = f"custom_{uuid.uuid4().hex[:12]}.jpg"
        filepath = CUSTOM_AVATARS_DIR / filename
        
        # Sauvegarder l'image
        image.save(filepath, "JPEG", quality=90, optimize=True)
        
        logger.info(f"Avatar personnalisé créé: {filename}")
        
        return {
            "ok": True,
            "avatar": f"custom_avatars/{filename}",
            "filename": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_exception(e, context="upload_custom_avatar")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/custom_avatars/{filename}")
async def get_custom_avatar(filename: str):
    """Retourne un avatar personnalisé"""
    filepath = CUSTOM_AVATARS_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Avatar non trouvé")
    return FileResponse(filepath)
