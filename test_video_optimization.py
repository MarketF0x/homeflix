# Test des optimisations du lecteur vidéo
# Usage: python test_video_optimization.py "C:\path\to\video.mkv"

import sys
import subprocess
import json
from pathlib import Path

def test_ffmpeg_installation():
    """Vérifie que FFmpeg est installé"""
    print("🔍 Test 1: Vérification FFmpeg...")
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"   ✅ FFmpeg installé: {version}")
            return True
        else:
            print(f"   ❌ FFmpeg non fonctionnel")
            return False
    except FileNotFoundError:
        print(f"   ❌ FFmpeg non trouvé dans PATH")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_gpu_encoders():
    """Détecte les encodeurs GPU disponibles"""
    print("\n🎮 Test 2: Détection encodeurs GPU...")
    
    encoders = {
        'h264_nvenc': 'NVIDIA NVENC',
        'h264_qsv': 'Intel Quick Sync',
        'h264_amf': 'AMD AMF'
    }
    
    found_gpu = False
    for encoder, name in encoders.items():
        try:
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if encoder in result.stdout:
                print(f"   ✅ {name} détecté ({encoder})")
                found_gpu = True
            else:
                print(f"   ❌ {name} non disponible")
        except Exception as e:
            print(f"   ❌ Erreur détection {name}: {e}")
    
    if not found_gpu:
        print(f"   💻 Aucun GPU détecté - Utilisation CPU (libx264)")
    
    return found_gpu

def analyze_video_file(video_path):
    """Analyse un fichier vidéo avec FFprobe"""
    print(f"\n📹 Test 3: Analyse du fichier vidéo...")
    print(f"   Fichier: {video_path}")
    
    if not Path(video_path).exists():
        print(f"   ❌ Fichier introuvable: {video_path}")
        return None
    
    try:
        # Taille du fichier
        size_mb = Path(video_path).stat().st_size / 1024 / 1024
        print(f"   📦 Taille: {size_mb:.1f} MB")
        
        # Analyse FFprobe
        probe_cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_streams", "-show_format", str(video_path)
        ]
        
        result = subprocess.run(
            probe_cmd,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode != 0:
            print(f"   ❌ Erreur FFprobe: {result.stderr}")
            return None
        
        data = json.loads(result.stdout)
        
        # Analyser stream vidéo
        video_streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'video']
        if video_streams:
            v = video_streams[0]
            codec = v.get('codec_name', 'unknown')
            profile = v.get('profile', '')
            width = v.get('width', 0)
            height = v.get('height', 0)
            
            print(f"   🎬 Codec vidéo: {codec.upper()} {profile}")
            print(f"   📐 Résolution: {width}x{height}")
            
            # Vérifier compatibilité HTML5
            compatible_codecs = ['h264', 'hevc', 'vp9']
            needs_transcode = codec not in compatible_codecs
            
            if needs_transcode:
                print(f"   ⚠️  TRANSCODAGE REQUIS (codec incompatible)")
            else:
                print(f"   ✅ COPIE DIRECTE possible (codec compatible)")
        
        # Analyser streams audio
        audio_streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'audio']
        if audio_streams:
            for i, a in enumerate(audio_streams):
                codec = a.get('codec_name', 'unknown')
                channels = a.get('channels', 0)
                lang = a.get('tags', {}).get('language', 'unknown')
                
                print(f"   🎵 Audio {i+1}: {codec.upper()} {channels}ch ({lang})")
                
                compatible_audio = ['aac', 'mp3', 'ac3', 'eac3', 'opus']
                if codec not in compatible_audio:
                    print(f"      ⚠️  Conversion AAC requise")
                elif channels > 2:
                    print(f"      ⚠️  Downmix stéréo recommandé")
        
        # Analyser sous-titres
        subtitle_streams = [s for s in data.get('streams', []) if s.get('codec_type') == 'subtitle']
        if subtitle_streams:
            print(f"   📝 {len(subtitle_streams)} piste(s) de sous-titres détectée(s)")
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"   ❌ Erreur parsing JSON: {e}")
        return None
    except Exception as e:
        print(f"   ❌ Erreur analyse: {e}")
        return None

def test_transcode_speed(video_path, gpu_available):
    """Test la vitesse de transcodage sur 10 secondes"""
    print(f"\n⚡ Test 4: Vitesse de transcodage (10 secondes)...")
    
    if not Path(video_path).exists():
        print(f"   ⚠️  Test ignoré - fichier introuvable")
        return
    
    encoder = "h264_nvenc" if gpu_available else "libx264"
    print(f"   🎬 Encodeur: {encoder}")
    
    try:
        import time
        
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-t", "10",  # 10 secondes seulement
            "-c:v", encoder,
            "-preset", "medium",
            "-crf", "21",
            "-c:a", "aac",
            "-b:a", "128k",
            "-f", "null",
            "-"
        ]
        
        start = time.time()
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        elapsed = time.time() - start
        
        if result.returncode == 0:
            speed = 10 / elapsed
            print(f"   ✅ Transcodage réussi en {elapsed:.1f}s")
            print(f"   📊 Vitesse: {speed:.2f}x temps réel")
            
            if speed >= 5:
                print(f"   🚀 Excellent (GPU)")
            elif speed >= 2:
                print(f"   ✅ Très bon")
            elif speed >= 1:
                print(f"   ⚠️  Acceptable")
            else:
                print(f"   ❌ Trop lent (< 1x)")
        else:
            print(f"   ❌ Échec transcodage")
            # Afficher dernières lignes stderr
            stderr_lines = result.stderr.split('\n')
            for line in stderr_lines[-5:]:
                if line.strip():
                    print(f"      {line}")
    
    except subprocess.TimeoutExpired:
        print(f"   ❌ Timeout - transcodage trop lent")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def main():
    print("=" * 70)
    print("🎬 TEST DES OPTIMISATIONS LECTEUR VIDÉO")
    print("=" * 70)
    
    # Test 1: FFmpeg installé
    ffmpeg_ok = test_ffmpeg_installation()
    if not ffmpeg_ok:
        print("\n❌ ARRÊT: FFmpeg requis")
        return
    
    # Test 2: GPU disponible
    gpu_available = test_gpu_encoders()
    
    # Test 3: Analyser fichier si fourni
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        video_data = analyze_video_file(video_path)
        
        if video_data:
            # Test 4: Vitesse de transcodage
            test_transcode_speed(video_path, gpu_available)
    else:
        print("\n💡 Usage: python test_video_optimization.py \"C:\\path\\to\\video.mkv\"")
        print("   (fichier vidéo optionnel pour analyse complète)")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ")
    print("=" * 70)
    print(f"FFmpeg: {'✅ OK' if ffmpeg_ok else '❌ Manquant'}")
    print(f"GPU: {'✅ Détecté' if gpu_available else '💻 CPU uniquement'}")
    
    if len(sys.argv) > 1 and Path(sys.argv[1]).exists():
        print(f"Analyse vidéo: ✅ Complétée")
    else:
        print(f"Analyse vidéo: ⚠️  Aucun fichier fourni")
    
    print("\n✅ Tests terminés")
    print("=" * 70)

if __name__ == "__main__":
    main()
