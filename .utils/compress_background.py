"""
Compression progressive en arrière-plan
Compresse les gros fichiers MKV un par un, en tâche de fond
"""

import subprocess
import sys
import time
from pathlib import Path
import yaml
import sqlite3
from datetime import datetime

def get_large_videos_from_db(min_size_gb=1.5):
    """Récupère les vidéos volumineuses depuis la base de données."""
    db_path = Path(__file__).parent / "data" / "homeone.db"
    
    if not db_path.exists():
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Taille minimale en octets
    min_size_bytes = min_size_gb * 1024 * 1024 * 1024
    
    # Récupérer les MKV/AVI volumineuses qui n'ont pas encore de version MP4
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
        
        # Si le MP4 n'existe pas ET que le MKV existe encore
        if not mp4_path.exists() and video_path.exists():
            to_compress.append({
                'id': video_id,
                'path': video_path,
                'size_gb': size / (1024**3),
                'title': title
            })
    
    return to_compress

def compress_video_background(input_path, quality="medium", log_file=None):
    """Compresse une vidéo en utilisant peu de CPU (mode nice)."""
    
    output_path = input_path.with_suffix('.mp4')
    
    quality_presets = {
        "medium": {
            "crf": "23",
            "preset": "medium",
            "scale": "1920:-2",
            "audio_bitrate": "128k"
        }
    }
    
    preset = quality_presets[quality]
    
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
        "-y",
        str(output_path)
    ]
    
    # Log du démarrage
    log_msg = f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Compression démarrée\n"
    log_msg += f"Fichier: {input_path.name}\n"
    log_msg += f"Sortie: {output_path.name}\n"
    
    if log_file:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg)
    
    print(log_msg)
    
    # Lancer FFmpeg avec priorité basse (pour ne pas ralentir le système)
    try:
        # Sur Windows, on peut réduire la priorité avec le module psutil
        import psutil
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS if sys.platform == 'win32' else 0
        )
        
        # Réduire encore plus la priorité
        if sys.platform == 'win32':
            p = psutil.Process(process.pid)
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        
        # Attendre la fin
        stdout, stderr = process.communicate()
        
        success = process.returncode == 0 and output_path.exists()
        
        if success:
            original_size = input_path.stat().st_size / (1024**3)
            new_size = output_path.stat().st_size / (1024**3)
            reduction = ((original_size - new_size) / original_size) * 100
            
            result_msg = f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Réussi: {original_size:.2f} GB → {new_size:.2f} GB ({reduction:.0f}%)\n"
            
            # Renommer l'original
            backup_path = input_path.with_suffix(input_path.suffix + '.original')
            input_path.rename(backup_path)
            result_msg += f"   Original → {backup_path.name}\n"
        else:
            result_msg = f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Échec\n"
            if output_path.exists():
                output_path.unlink()
        
        if log_file:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(result_msg)
        
        print(result_msg)
        return success
        
    except ImportError:
        # psutil non disponible, compression normale
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        return process.returncode == 0

def main():
    print("=" * 70)
    print("🔄 COMPRESSION PROGRESSIVE EN ARRIÈRE-PLAN")
    print("=" * 70)
    print("\n💡 Ce script compresse les gros fichiers un par un, en tâche de fond.")
    print("   Vous pouvez continuer à utiliser HomeFlix pendant ce temps.\n")
    
    # Trouver les vidéos à compresser
    print("🔍 Recherche des vidéos volumineuses...")
    videos = get_large_videos_from_db(min_size_gb=1.5)
    
    if not videos:
        print("\n✅ Aucune vidéo volumineuse à compresser !")
        print("   Toutes vos vidéos sont déjà optimisées.\n")
        return
    
    print(f"\n📊 {len(videos)} vidéo(s) à compresser :\n")
    
    total_size = sum(v['size_gb'] for v in videos)
    estimated_final = total_size * 0.35  # ~65% de réduction
    
    for i, video in enumerate(videos[:10], 1):  # Afficher les 10 premières
        print(f"{i:2}. {video['title'][:60]}")
        print(f"    {video['size_gb']:.2f} GB")
    
    if len(videos) > 10:
        print(f"... et {len(videos) - 10} autres")
    
    print(f"\n💾 Total : {total_size:.2f} GB")
    print(f"📉 Après compression : ~{estimated_final:.2f} GB")
    print(f"🎉 Espace libéré : ~{total_size - estimated_final:.2f} GB\n")
    
    # Configuration
    print("⚙️  MODE DE COMPRESSION:")
    print("   - 1 fichier à la fois")
    print("   - Priorité basse (ne ralentit pas le système)")
    print("   - Originals conservés (.original)")
    print("   - Vous pouvez continuer à utiliser HomeFlix\n")
    
    # Options
    print("OPTIONS:")
    print("1. Compresser TOUT maintenant (peut prendre plusieurs heures)")
    print("2. Compresser les 5 premiers seulement (test)")
    print("3. Annuler")
    
    choice = input("\nVotre choix (1/2/3) : ").strip()
    
    if choice == "3" or not choice:
        print("❌ Annulé")
        return
    
    limit = None if choice == "1" else 5
    videos_to_process = videos[:limit] if limit else videos
    
    print(f"\n🚀 Compression de {len(videos_to_process)} vidéo(s)...")
    print("⏸️  Vous pouvez minimiser cette fenêtre et continuer à utiliser HomeFlix\n")
    
    # Créer un fichier de log
    log_file = Path(__file__).parent / "compression_log.txt"
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*70}\n")
        f.write(f"Session de compression: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Nombre de vidéos: {len(videos_to_process)}\n")
        f.write(f"{'='*70}\n")
    
    # Compresser
    success_count = 0
    failed_count = 0
    
    for i, video in enumerate(videos_to_process, 1):
        print(f"\n[{i}/{len(videos_to_process)}] {video['title']}")
        print(f"   Taille: {video['size_gb']:.2f} GB")
        
        success = compress_video_background(video['path'], quality="medium", log_file=log_file)
        
        if success:
            success_count += 1
        else:
            failed_count += 1
        
        # Petit délai entre chaque compression
        if i < len(videos_to_process):
            time.sleep(2)
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ")
    print("=" * 70)
    print(f"✅ Réussies : {success_count}")
    print(f"❌ Échouées : {failed_count}")
    print(f"📁 Total : {len(videos_to_process)}")
    print(f"\n📝 Log détaillé : {log_file}")
    
    if success_count > 0:
        print("\n💡 IMPORTANT:")
        print("   1. Les vidéos compressées (.mp4) sont prêtes à l'emploi")
        print("   2. Les originaux (.original) sont conservés")
        print("   3. Relancez HomeFlix pour détecter les nouveaux MP4")
        print("   4. Testez les vidéos, puis supprimez les .original:")
        print("\n      Get-ChildItem -Recurse -Filter *.original | Remove-Item")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Compression interrompue")
        print("   Les vidéos déjà compressées sont conservées")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
