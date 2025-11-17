"""
Script de compression rapide d'UNE SEULE vidéo (pour test)
Usage: python compress_one_video.py "chemin/vers/video.mkv"
"""

import subprocess
import sys
from pathlib import Path
import shutil

def compress_video(input_path, quality="medium"):
    """Compresse une vidéo avec FFmpeg."""
    
    input_path = Path(input_path)
    
    if not input_path.exists():
        print(f"❌ Fichier introuvable : {input_path}")
        return False
    
    # Fichier de sortie
    output_path = input_path.with_suffix('.mp4')
    
    if output_path.exists():
        print(f"⚠️  Le fichier {output_path.name} existe déjà")
        overwrite = input("Écraser ? (o/N) : ").strip().lower()
        if overwrite != 'o':
            return False
    
    # Presets de qualité
    quality_presets = {
        "high": {
            "crf": "20",
            "preset": "medium",
            "scale": "1920:-2",
            "audio_bitrate": "192k",
            "description": "Excellente qualité (~50% réduction)"
        },
        "medium": {
            "crf": "23",
            "preset": "medium",
            "scale": "1920:-2",
            "audio_bitrate": "128k",
            "description": "Bonne qualité (~65% réduction)"
        },
        "fast": {
            "crf": "26",
            "preset": "fast",
            "scale": "1280:-2",
            "audio_bitrate": "128k",
            "description": "Qualité correcte, rapide (~75% réduction)"
        }
    }
    
    preset = quality_presets.get(quality, quality_presets["medium"])
    
    # Informations
    size_gb = input_path.stat().st_size / (1024**3)
    print(f"\n🎬 Compression de : {input_path.name}")
    print(f"📏 Taille actuelle : {size_gb:.2f} GB")
    print(f"⚙️  Qualité : {preset['description']}")
    print(f"💾 Sortie : {output_path.name}")
    
    # Commande FFmpeg avec TOUTES les pistes préservées
    cmd = [
        "ffmpeg",
        "-i", str(input_path),
        "-map", "0",                    # ✅ Copier TOUTES les pistes (audio + sous-titres)
        "-c:v", "libx264",
        "-preset", preset["preset"],
        "-crf", preset["crf"],
        "-vf", f"scale={preset['scale']}",
        "-c:a", "aac",                  # Toutes les pistes audio → AAC
        "-b:a", preset["audio_bitrate"],
        "-c:s", "mov_text",             # ✅ Sous-titres en format MP4
        "-movflags", "+faststart",
        "-progress", "pipe:1",  # Progression
        "-y",
        str(output_path)
    ]
    
    print("\n⏳ Compression en cours...\n")
    
    # Lancer FFmpeg
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Afficher la progression
    for line in process.stdout:
        if "time=" in line or "frame=" in line or "fps=" in line:
            print(f"\r   {line.strip()[:80]}", end="", flush=True)
    
    process.wait()
    print("\n")
    
    if process.returncode == 0 and output_path.exists():
        new_size_gb = output_path.stat().st_size / (1024**3)
        reduction = ((size_gb - new_size_gb) / size_gb) * 100
        
        print(f"✅ Compression réussie !")
        print(f"   Avant : {size_gb:.2f} GB")
        print(f"   Après : {new_size_gb:.2f} GB")
        print(f"   Réduction : {reduction:.0f}%")
        print(f"   Espace libéré : {size_gb - new_size_gb:.2f} GB")
        
        # Proposer de renommer l'original
        print(f"\n💾 Fichier original : {input_path.name}")
        backup = input("Renommer en .original ? (o/N) : ").strip().lower()
        
        if backup == 'o':
            backup_path = input_path.with_suffix(input_path.suffix + '.original')
            input_path.rename(backup_path)
            print(f"✅ Renommé : {backup_path.name}")
        
        return True
    else:
        print("❌ Échec de la compression")
        if output_path.exists():
            output_path.unlink()
        return False

def main():
    # Vérifier FFmpeg
    if not shutil.which("ffmpeg"):
        print("❌ FFmpeg non installé !")
        print("   Installez-le avec : python check_and_install_ffmpeg.py")
        sys.exit(1)
    
    print("=" * 70)
    print("🗜️  COMPRESSION RAPIDE D'UNE VIDÉO")
    print("=" * 70)
    
    # Fichier à compresser
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = input("\n📁 Chemin de la vidéo à compresser : ").strip().strip('"')
    
    if not video_path:
        print("❌ Aucun fichier spécifié")
        sys.exit(1)
    
    # Choix de la qualité
    print("\n📐 Choisissez le niveau de qualité :")
    print("1. Haute (CRF 20, 1080p) - Excellente qualité, ~50% de réduction")
    print("2. Moyenne (CRF 23, 1080p) - Bonne qualité, ~65% de réduction [RECOMMANDÉ]")
    print("3. Rapide (CRF 26, 720p) - Qualité correcte, ~75% de réduction")
    
    choice = input("\nVotre choix (1/2/3) [2] : ").strip() or "2"
    
    quality_map = {"1": "high", "2": "medium", "3": "fast"}
    quality = quality_map.get(choice, "medium")
    
    # Compresser
    success = compress_video(video_path, quality)
    
    if success:
        print("\n🎉 Terminé ! Testez la vidéo dans HomeFlix")
    else:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Compression interrompue")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
