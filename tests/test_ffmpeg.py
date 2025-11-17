#!/usr/bin/env python3
"""
Script de test pour vérifier la commande FFmpeg de transcodage.
Teste si l'audio est bien présent et synchronisé.
"""

import sys
import subprocess
from pathlib import Path

# Exemple : python test_ffmpeg.py "I:\FILM\Judge.Dredd.1995.PROPER.1080p.BluRay.H264.AAC-RARBG\Judge Dredd.mp4"

if len(sys.argv) < 2:
    print("Usage: python test_ffmpeg.py <chemin_video>")
    print("Exemple: python test_ffmpeg.py 'I:\\FILM\\test.mkv'")
    sys.exit(1)

video_path = Path(sys.argv[1])

if not video_path.exists():
    print(f"❌ Fichier introuvable: {video_path}")
    sys.exit(1)

print(f"🎬 Test FFmpeg pour: {video_path.name}")
print(f"   Taille: {video_path.stat().st_size / 1024 / 1024:.1f} MB")
print()

# D'abord, analyser le fichier
print("📊 ANALYSE DU FICHIER (ffprobe):")
print("-" * 80)

probe_cmd = [
    "ffprobe",
    "-v", "quiet",
    "-print_format", "json",
    "-show_streams",
    "-show_format",
    str(video_path)
]

try:
    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    import json
    data = json.loads(result.stdout)
    
    print(f"Format: {data['format']['format_long_name']}")
    print(f"Durée: {float(data['format']['duration']):.1f}s")
    print()
    
    video_streams = [s for s in data['streams'] if s['codec_type'] == 'video']
    audio_streams = [s for s in data['streams'] if s['codec_type'] == 'audio']
    subtitle_streams = [s for s in data['streams'] if s['codec_type'] == 'subtitle']
    
    print(f"📹 Pistes VIDÉO: {len(video_streams)}")
    for i, s in enumerate(video_streams):
        print(f"   [{i}] {s['codec_name']} - {s.get('width', '?')}x{s.get('height', '?')} - {s.get('bit_rate', 'N/A')} bps")
    
    print()
    print(f"🔊 Pistes AUDIO: {len(audio_streams)}")
    for i, s in enumerate(audio_streams):
        lang = s.get('tags', {}).get('language', 'unknown')
        title = s.get('tags', {}).get('title', '')
        channels = s.get('channels', '?')
        sample_rate = s.get('sample_rate', '?')
        print(f"   [{i}] {s['codec_name']} - {channels} canaux - {sample_rate} Hz - Langue: {lang} - {title}")
    
    print()
    print(f"📝 Pistes SOUS-TITRES: {len(subtitle_streams)}")
    for i, s in enumerate(subtitle_streams):
        lang = s.get('tags', {}).get('language', 'unknown')
        title = s.get('tags', {}).get('title', '')
        print(f"   [{i}] {s['codec_name']} - Langue: {lang} - {title}")
    
except Exception as e:
    print(f"❌ Erreur ffprobe: {e}")

print()
print("=" * 80)
print("🔄 TEST DE TRANSCODAGE:")
print("-" * 80)

# Test de la commande FFmpeg
# Test de la commande FFmpeg
output_file = video_path.parent / f"test_transcode_{video_path.stem}.mp4"

# Détecter les codecs audio
audio_streams = [s for s in data['streams'] if s['codec_type'] == 'audio']
mp4_compatible_audio = ['aac', 'mp3', 'ac3', 'eac3', 'opus']
needs_audio_conversion = any(
    s.get('codec_name', '') not in mp4_compatible_audio 
    for s in audio_streams
)

audio_codec = "aac" if needs_audio_conversion else "copy"
audio_params = []

if needs_audio_conversion:
    print(f"⚠️ Audio incompatible MP4 - Conversion en AAC")
    audio_params = ["-b:a", "320k", "-ar", "48000"]
else:
    print(f"✅ Audio compatible - Copie directe")

ffmpeg_cmd = [
    "ffmpeg",
    "-y",  # Écraser fichier existant
    "-analyzeduration", "5M",
    "-probesize", "5M",
    "-fflags", "+genpts+igndts",
    "-i", str(video_path),
    "-map", "0:v",      # TOUTES les vidéos
    "-map", "0:a",      # TOUTES les pistes audio
    "-map", "0:s?",     # TOUS les sous-titres
    "-c:v", "copy",
    "-c:a", audio_codec,
    *audio_params,
    "-c:s", "mov_text",
    "-f", "mp4",
    "-movflags", "frag_keyframe+empty_moov+default_base_moof+faststart",
    "-max_muxing_queue_size", "9999",
    "-avoid_negative_ts", "make_zero",
    "-threads", "0",
    "-t", "10",  # Seulement 10 secondes pour test
    str(output_file)
]

print("Commande FFmpeg:")
print(" ".join(ffmpeg_cmd))
print()
print("⏳ Transcodage des 10 premières secondes...")

try:
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print(f"✅ Transcodage réussi!")
        print(f"   Fichier créé: {output_file}")
        print(f"   Taille: {output_file.stat().st_size / 1024:.1f} KB")
        print()
        print("📊 Vérification du fichier transcodé:")
        
        # Analyser le fichier de sortie
        probe_out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", str(output_file)],
            capture_output=True,
            text=True
        )
        
        data_out = json.loads(probe_out.stdout)
        audio_out = [s for s in data_out['streams'] if s['codec_type'] == 'audio']
        video_out = [s for s in data_out['streams'] if s['codec_type'] == 'video']
        subtitle_out = [s for s in data_out['streams'] if s['codec_type'] == 'subtitle']
        
        print(f"   Vidéo: {video_out[0]['codec_name'] if video_out else 'AUCUNE'}")
        print(f"   Audio: {len(audio_out)} pistes")
        for i, a in enumerate(audio_out):
            lang = a.get('tags', {}).get('language', 'unknown')
            channels = a.get('channels', '?')
            print(f"      [{i}] {a['codec_name']} - {channels} canaux - Langue: {lang}")
        
        print(f"   Sous-titres: {len(subtitle_out)} pistes")
        for i, s in enumerate(subtitle_out):
            lang = s.get('tags', {}).get('language', 'unknown')
            print(f"      [{i}] {s['codec_name']} - Langue: {lang}")
        
        if audio_out:
            print(f"   ✅ {len(audio_out)} PISTE(S) AUDIO PRÉSENTE(S)")
        else:
            print(f"   ❌ AUDIO MANQUANT!")
        
        print()
        print("🎬 Pour tester la lecture:")
        print(f"   vlc \"{output_file}\"")
        
    else:
        print(f"❌ Transcodage échoué!")
        print()
        print("STDERR:")
        print(result.stderr)
        
except subprocess.TimeoutExpired:
    print("❌ Timeout! Le transcodage prend trop de temps.")
except Exception as e:
    print(f"❌ Erreur: {e}")
