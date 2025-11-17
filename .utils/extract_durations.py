"""
Script pour extraire les durées de toutes les vidéos avec FFprobe
"""
import subprocess
import json
from server.core.db import init_db, get_session
from server.core.models import Video

def get_video_duration(path: str) -> float:
    """Extrait la durée d'une vidéo avec FFprobe"""
    try:
        result = subprocess.run(
            [
                "C:\\ffmpeg\\bin\\ffprobe.exe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                path
            ],
            capture_output=True,
            text=True,
            timeout=5  # Réduit à 5 secondes
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration = float(data.get("format", {}).get("duration", 0))
            return duration
        return 0
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout")
        return 0
    except Exception as e:
        print(f"❌ Erreur: {str(e)[:50]}")
        return 0

def main():
    init_db()
    
    with get_session() as s:
        videos = s.query(Video).all()
        total = len(videos)
        updated = 0
        errors = 0
        skipped = 0
        
        print(f"📊 Traitement de {total} vidéos...\n")
        
        for i, video in enumerate(videos, 1):
            # Afficher progression
            percent = (i / total) * 100
            
            if video.duration_seconds and video.duration_seconds > 0:
                skipped += 1
                if i % 50 == 0:
                    print(f"[{i}/{total} - {percent:.1f}%] ⏭️ {skipped} déjà renseignées")
                continue
            
            duration = get_video_duration(video.path)
            
            if duration > 0:
                video.duration_seconds = int(duration)
                updated += 1
                mins = int(duration / 60)
                print(f"[{i}/{total} - {percent:.1f}%] ✅ {video.title[:50]}: {mins} min")
                
                # Sauvegarder tous les 10 films
                if updated % 10 == 0:
                    s.commit()
            else:
                errors += 1
                print(f"[{i}/{total} - {percent:.1f}%] ❌ {video.title[:50]}")
        
        # Sauvegarde finale
        s.commit()
        
        print(f"\n📈 Résumé:")
        print(f"  Total: {total}")
        print(f"  Mises à jour: {updated}")
        print(f"  Erreurs: {errors}")
        print(f"  Déjà renseignées: {skipped}")

if __name__ == "__main__":
    main()
