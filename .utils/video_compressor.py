"""
Module unifié de compression vidéo pour HomeOne
Consolide compress_one_video.py, compress_large_videos.py et compress_background.py

Usage:
    # Compresser une vidéo unique
    python video_compressor.py compress "chemin/video.mkv" --quality medium
    
    # Compresser les gros fichiers du catalogue
    python video_compressor.py batch --min-size 2.0 --quality medium
    
    # Mode arrière-plan (daemon)
    python video_compressor.py daemon --interval 3600
"""

import subprocess
import sys
import time
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Literal

# Import du helper subprocess invisible
sys.path.insert(0, str(Path(__file__).parent / "server"))
from core.subprocess_helper import run_hidden, popen_hidden

# Presets de qualité
QUALITY_PRESETS = {
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

QualityLevel = Literal["high", "medium", "fast"]


def get_video_duration(video_path: Path) -> Optional[float]:
    """Récupère la durée de la vidéo avec ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        result = run_hidden(cmd, capture_output=True, text=True, check=True, timeout=10)
        return float(result.stdout.strip())
    except Exception:
        return None


def compress_video(
    input_path: Path,
    output_path: Optional[Path] = None,
    quality: QualityLevel = "medium",
    overwrite: bool = False,
    verbose: bool = True
) -> bool:
    """
    Compresse une vidéo avec FFmpeg.
    
    Args:
        input_path: Chemin du fichier source
        output_path: Chemin de sortie (défaut: même nom avec .mp4)
        quality: Niveau de qualité (high/medium/fast)
        overwrite: Écraser si le fichier existe
        verbose: Afficher les logs détaillés
    
    Returns:
        True si succès, False sinon
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        print(f"❌ Fichier introuvable : {input_path}")
        return False
    
    # Fichier de sortie
    if output_path is None:
        output_path = input_path.with_suffix('.mp4')
    else:
        output_path = Path(output_path)
    
    # Vérifier écrasement
    if output_path.exists() and not overwrite:
        print(f"⚠️ Le fichier {output_path.name} existe déjà (utilisez --overwrite pour forcer)")
        return False
    
    preset = QUALITY_PRESETS.get(quality, QUALITY_PRESETS["medium"])
    
    # Informations
    size_gb = input_path.stat().st_size / (1024**3)
    if verbose:
        print(f"\n🎬 Compression : {input_path.name}")
        print(f"📏 Taille : {size_gb:.2f} GB")
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
        "-y" if overwrite else "-n",
        str(output_path)
    ]
    
    try:
        if verbose:
            print(f"\n⏳ Compression en cours...")
            start_time = time.time()
        
        # Exécution FFmpeg
        result = run_hidden(
            cmd,
            stdout=subprocess.PIPE if not verbose else None,
            stderr=subprocess.PIPE if not verbose else None,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Erreur FFmpeg (code {result.returncode})")
            if not verbose and result.stderr:
                print(result.stderr[-500:])  # Dernières 500 chars d'erreur
            return False
        
        # Succès
        if verbose:
            elapsed = time.time() - start_time
            new_size_gb = output_path.stat().st_size / (1024**3)
            reduction = (1 - new_size_gb / size_gb) * 100
            
            print(f"\n✅ Compression réussie !")
            print(f"⏱️  Durée : {elapsed/60:.1f} min")
            print(f"📉 Taille : {size_gb:.2f} GB → {new_size_gb:.2f} GB ({reduction:.1f}% réduction)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False


def get_large_videos_from_db(min_size_gb: float = 1.5) -> list:
    """Récupère les vidéos volumineuses depuis la base de données."""
    db_path = Path(__file__).parent / "data" / "homeone.db"
    
    if not db_path.exists():
        print("⚠️ Base de données introuvable")
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Taille minimale en octets
    min_size_bytes = min_size_gb * 1024 * 1024 * 1024
    
    # Récupérer les MKV/AVI/MOV volumineuses
    results = cursor.execute("""
        SELECT id, path, size, title
        FROM videos
        WHERE (path LIKE '%.mkv' OR path LIKE '%.avi' OR path LIKE '%.mov')
        AND size > ?
        ORDER BY size DESC
    """, (min_size_bytes,)).fetchall()
    
    conn.close()
    
    # Filtrer ceux qui n'ont pas déjà une version MP4
    to_compress = []
    for video_id, path, size, title in results:
        video_path = Path(path)
        mp4_path = video_path.with_suffix('.mp4')
        
        # Si le MP4 n'existe pas ET que le fichier source existe
        if not mp4_path.exists() and video_path.exists():
            to_compress.append({
                'id': video_id,
                'path': video_path,
                'size_gb': size / (1024**3),
                'title': title
            })
    
    return to_compress


def compress_batch(min_size_gb: float = 1.5, quality: QualityLevel = "medium", limit: Optional[int] = None):
    """Compresse en batch les gros fichiers du catalogue."""
    videos = get_large_videos_from_db(min_size_gb)
    
    if not videos:
        print("✅ Aucune vidéo volumineuse à compresser")
        return
    
    if limit:
        videos = videos[:limit]
    
    print(f"\n📊 {len(videos)} vidéo(s) à compresser (>{min_size_gb} GB)")
    
    success = 0
    failed = 0
    
    for i, video in enumerate(videos, 1):
        print(f"\n[{i}/{len(videos)}] {video['title']} ({video['size_gb']:.2f} GB)")
        
        if compress_video(video['path'], quality=quality, overwrite=False, verbose=True):
            success += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Réussies : {success}")
    print(f"❌ Échecs : {failed}")


def daemon_mode(interval: int = 3600, min_size_gb: float = 1.5, quality: QualityLevel = "medium"):
    """Mode daemon : compresse automatiquement toutes les N secondes."""
    print(f"🤖 Mode daemon démarré (intervalle : {interval}s)")
    
    while True:
        try:
            videos = get_large_videos_from_db(min_size_gb)
            
            if videos:
                print(f"\n[{datetime.now()}] {len(videos)} vidéo(s) à compresser")
                video = videos[0]  # Prendre la plus grosse
                compress_video(video['path'], quality=quality, overwrite=False, verbose=True)
            else:
                print(f"[{datetime.now()}] Aucune vidéo à compresser")
            
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\n👋 Arrêt du daemon")
            break
        except Exception as e:
            print(f"❌ Erreur daemon : {e}")
            time.sleep(60)


def main():
    parser = argparse.ArgumentParser(description="Compresseur vidéo HomeOne unifié")
    subparsers = parser.add_subparsers(dest="command", help="Commande")
    
    # Commande: compress (une seule vidéo)
    compress_parser = subparsers.add_parser("compress", help="Compresser une vidéo")
    compress_parser.add_argument("input", type=str, help="Chemin du fichier vidéo")
    compress_parser.add_argument("-o", "--output", type=str, help="Fichier de sortie (défaut: .mp4)")
    compress_parser.add_argument("-q", "--quality", choices=["high", "medium", "fast"], default="medium")
    compress_parser.add_argument("--overwrite", action="store_true", help="Écraser si existe")
    
    # Commande: batch (plusieurs vidéos du catalogue)
    batch_parser = subparsers.add_parser("batch", help="Compresser en batch")
    batch_parser.add_argument("--min-size", type=float, default=1.5, help="Taille minimale en GB (défaut: 1.5)")
    batch_parser.add_argument("-q", "--quality", choices=["high", "medium", "fast"], default="medium")
    batch_parser.add_argument("--limit", type=int, help="Limiter le nombre de fichiers")
    
    # Commande: daemon (arrière-plan)
    daemon_parser = subparsers.add_parser("daemon", help="Mode daemon (arrière-plan)")
    daemon_parser.add_argument("--interval", type=int, default=3600, help="Intervalle en secondes (défaut: 3600)")
    daemon_parser.add_argument("--min-size", type=float, default=1.5, help="Taille minimale en GB")
    daemon_parser.add_argument("-q", "--quality", choices=["high", "medium", "fast"], default="medium")
    
    args = parser.parse_args()
    
    if args.command == "compress":
        output = Path(args.output) if args.output else None
        success = compress_video(
            Path(args.input),
            output_path=output,
            quality=args.quality,
            overwrite=args.overwrite,
            verbose=True
        )
        sys.exit(0 if success else 1)
    
    elif args.command == "batch":
        compress_batch(args.min_size, args.quality, args.limit)
    
    elif args.command == "daemon":
        daemon_mode(args.interval, args.min_size, args.quality)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
