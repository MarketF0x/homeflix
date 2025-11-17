"""
Script de compression intelligente des vidéos volumineuses
Convertit les gros fichiers MKV/AVI en MP4 H.264 optimisés pour le streaming
"""

import subprocess
import sys
from pathlib import Path
from tqdm import tqdm
import shutil

def get_video_duration(video_path):
    """Récupère la durée de la vidéo avec ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return None

def compress_video(input_path, output_path, quality="medium", progress_callback=None):
    """
    Compresse une vidéo avec FFmpeg.
    
    Qualités disponibles :
    - high : CRF 20, 1080p, AAC 192k (excellente qualité, fichiers moyens)
    - medium : CRF 23, 1080p, AAC 128k (bonne qualité, fichiers réduits)
    - fast : CRF 26, 720p, AAC 128k (qualité correcte, fichiers petits, rapide)
    """
    
    quality_presets = {
        "high": {
            "crf": "20",
            "preset": "medium",
            "scale": "1920:-2",
            "audio_bitrate": "192k",
            "description": "Excellente qualité"
        },
        "medium": {
            "crf": "23",
            "preset": "medium",
            "scale": "1920:-2",
            "audio_bitrate": "128k",
            "description": "Bonne qualité (recommandé)"
        },
        "fast": {
            "crf": "26",
            "preset": "fast",
            "scale": "1280:-2",
            "audio_bitrate": "128k",
            "description": "Qualité correcte, rapide"
        }
    }
    
    preset = quality_presets.get(quality, quality_presets["medium"])
    
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
        "-movflags", "+faststart",  # Optimisé pour streaming
        "-y",  # Écraser si existe
        str(output_path)
    ]
    
    print(f"\n🎬 Compression : {input_path.name}")
    print(f"   Qualité : {preset['description']}")
    print(f"   Sortie : {output_path.name}")
    
    # Lancer FFmpeg
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Afficher la progression
    for line in process.stdout:
        if progress_callback:
            progress_callback(line)
        # Afficher les lignes importantes
        if "time=" in line or "frame=" in line:
            print(f"\r   {line.strip()[:80]}", end="", flush=True)
    
    process.wait()
    print()  # Nouvelle ligne après la progression
    
    return process.returncode == 0

def scan_large_videos(root_dirs, min_size_gb=1.5):
    """Scan les dossiers pour trouver les vidéos volumineuses."""
    large_videos = []
    extensions = ['.mkv', '.avi', '.mov', '.flv', '.wmv']
    
    print(f"\n🔍 Recherche des vidéos > {min_size_gb} GB...")
    
    for root_dir in root_dirs:
        root_path = Path(root_dir)
        if not root_path.exists():
            print(f"⚠️  Dossier introuvable : {root_dir}")
            continue
        
        for ext in extensions:
            for video in root_path.rglob(f"*{ext}"):
                size_gb = video.stat().st_size / (1024**3)
                if size_gb >= min_size_gb:
                    large_videos.append((video, size_gb))
    
    # Trier par taille décroissante
    large_videos.sort(key=lambda x: x[1], reverse=True)
    
    return large_videos

def estimate_compressed_size(original_size_gb, quality="medium"):
    """Estime la taille après compression."""
    compression_ratios = {
        "high": 0.5,    # Réduit de 50%
        "medium": 0.35, # Réduit de 65%
        "fast": 0.25    # Réduit de 75%
    }
    ratio = compression_ratios.get(quality, 0.35)
    return original_size_gb * ratio

def main():
    # Vérifier FFmpeg
    if not shutil.which("ffmpeg"):
        print("❌ FFmpeg non installé !")
        print("   Installez-le avec : python check_and_install_ffmpeg.py")
        sys.exit(1)
    
    print("=" * 70)
    print("🗜️  COMPRESSION INTELLIGENTE DES VIDÉOS VOLUMINEUSES")
    print("=" * 70)
    
    # Lire settings.yaml pour les dossiers vidéo
    import yaml
    settings_path = Path(__file__).parent / "settings.yaml"
    
    with open(settings_path, 'r', encoding='utf-8') as f:
        settings = yaml.safe_load(f)
    
    video_dirs = settings.get('video_directories', [])
    
    if not video_dirs:
        print("❌ Aucun dossier vidéo configuré dans settings.yaml")
        sys.exit(1)
    
    # Scanner les vidéos volumineuses
    large_videos = scan_large_videos(video_dirs, min_size_gb=1.5)
    
    if not large_videos:
        print("\n✅ Aucune vidéo volumineuse trouvée (> 1.5 GB)")
        return
    
    print(f"\n📊 {len(large_videos)} vidéo(s) volumineuse(s) trouvée(s) :\n")
    
    total_size = 0
    for i, (video, size) in enumerate(large_videos, 1):
        total_size += size
        print(f"{i:3}. {video.name}")
        print(f"     Taille : {size:.2f} GB")
        print(f"     Chemin : {video.parent}")
        print()
    
    print(f"💾 Taille totale : {total_size:.2f} GB")
    
    # Choix de la qualité
    print("\n📐 Choisissez le niveau de qualité :")
    print("1. Haute (CRF 20, 1080p, 192k audio) - Excellente qualité, ~50% de réduction")
    print("2. Moyenne (CRF 23, 1080p, 128k audio) - Bonne qualité, ~65% de réduction [RECOMMANDÉ]")
    print("3. Rapide (CRF 26, 720p, 128k audio) - Qualité correcte, ~75% de réduction")
    
    choice = input("\nVotre choix (1/2/3) [2] : ").strip() or "2"
    
    quality_map = {"1": "high", "2": "medium", "3": "fast"}
    quality = quality_map.get(choice, "medium")
    
    estimated_size = estimate_compressed_size(total_size, quality)
    space_saved = total_size - estimated_size
    
    print(f"\n💡 Estimation après compression :")
    print(f"   Taille finale : ~{estimated_size:.2f} GB")
    print(f"   Espace libéré : ~{space_saved:.2f} GB ({(space_saved/total_size*100):.0f}%)")
    
    # Confirmation
    print("\n⚠️  IMPORTANT :")
    print("   - Les fichiers originaux seront CONSERVÉS (renommés .mkv.original)")
    print("   - Vous pourrez les supprimer manuellement après vérification")
    print("   - La compression peut prendre plusieurs heures pour les gros fichiers")
    
    confirm = input("\n🚀 Lancer la compression ? (o/N) : ").strip().lower()
    
    if confirm != 'o':
        print("❌ Compression annulée")
        return
    
    # Compresser les vidéos
    print("\n" + "=" * 70)
    print("🎬 COMPRESSION EN COURS...")
    print("=" * 70)
    
    success_count = 0
    failed_count = 0
    
    for i, (video, size) in enumerate(large_videos, 1):
        print(f"\n[{i}/{len(large_videos)}]")
        
        # Créer le nom du fichier de sortie
        output_path = video.with_suffix('.mp4')
        
        # Si le MP4 existe déjà, passer
        if output_path.exists():
            print(f"⏭️  Déjà compressé : {output_path.name}")
            continue
        
        # Compresser
        success = compress_video(video, output_path, quality)
        
        if success:
            # Vérifier que le fichier de sortie existe et n'est pas vide
            if output_path.exists() and output_path.stat().st_size > 1024:
                original_size = video.stat().st_size / (1024**3)
                new_size = output_path.stat().st_size / (1024**3)
                reduction = ((original_size - new_size) / original_size) * 100
                
                print(f"✅ Compressé : {original_size:.2f} GB → {new_size:.2f} GB ({reduction:.0f}% de réduction)")
                
                # Renommer l'original
                backup_path = video.with_suffix(video.suffix + '.original')
                video.rename(backup_path)
                print(f"💾 Original sauvegardé : {backup_path.name}")
                
                success_count += 1
            else:
                print(f"❌ Erreur : fichier de sortie invalide")
                if output_path.exists():
                    output_path.unlink()
                failed_count += 1
        else:
            print(f"❌ Échec de la compression")
            failed_count += 1
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ")
    print("=" * 70)
    print(f"✅ Réussies : {success_count}")
    print(f"❌ Échouées : {failed_count}")
    print(f"📁 Total : {len(large_videos)}")
    
    if success_count > 0:
        print("\n💡 Prochaines étapes :")
        print("   1. Testez les vidéos compressées dans HomeFlix")
        print("   2. Si tout fonctionne, supprimez les fichiers .original")
        print("   3. Relancez le scan des vidéos : les nouvelles MP4 seront détectées")
        print("\n🗑️  Pour supprimer les .original :")
        print("   Get-ChildItem -Recurse -Filter *.original | Remove-Item")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Compression interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
