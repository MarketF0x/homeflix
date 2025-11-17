import os
import time
import subprocess
import shutil
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from server.main import app, HLS_BASE_DIR


def _ffmpeg_path():
    return shutil.which("ffmpeg")


@pytest.mark.skipif(_ffmpeg_path() is None, reason="FFmpeg requis pour le test HLS")
def test_start_hls_session_smoke():
    client = TestClient(app)

    # 1) Générer une petite vidéo MP4 de 2s pour le test
    tmpdir = tempfile.mkdtemp(prefix="hls_test_")
    try:
        sample_path = Path(tmpdir) / "sample.mp4"
        cmd = [
            _ffmpeg_path(), "-y",
            "-f", "lavfi", "-i", "testsrc=size=640x360:rate=25",
            "-f", "lavfi", "-i", "sine=frequency=1000",
            "-t", "12",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-movflags", "+faststart",
            str(sample_path)
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        assert sample_path.exists(), f"Échec génération sample mp4: {proc.stderr}"

        # 2) Démarrer la session HLS
        r = client.get(
            "/api/stream/hls/start",
            params={"path": str(sample_path), "audio_track": 1, "quality": "fast"}
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("ok") is True
        sid = data.get("sid")
        playlist_url = data.get("playlist_url")  # ex: /api/stream/hls/<sid>/master.m3u8
        assert sid and playlist_url

        # 3) Attendre la dispo de la master ou de la playlist (via API ou FS)
        playlist_ok = False
        used_playlist = None
        for _ in range(100):  # ~20s max
            resp = client.get(playlist_url)
            if resp.status_code == 200 and "#EXTM3U" in resp.text:
                playlist_ok = True
                used_playlist = playlist_url
                break
            # Essayer la playlist de niveau
            resp2 = client.get(f"/api/stream/hls/{sid}/playlist.m3u8")
            if resp2.status_code == 200 and "#EXTM3U" in resp2.text:
                playlist_ok = True
                used_playlist = f"/api/stream/hls/{sid}/playlist.m3u8"
                pl_resp = resp2
                break
            # Vérifier directement sur le disque (cas timing)
            session_dir = (HLS_BASE_DIR / sid)
            master_file = session_dir / "master.m3u8"
            playlist_file = session_dir / "playlist.m3u8"
            if master_file.exists() or playlist_file.exists():
                playlist_ok = True
                used_playlist = f"/api/stream/hls/{sid}/playlist.m3u8"
                break
            time.sleep(0.2)
        assert playlist_ok, "Playlist HLS non disponible à temps"

        # 4) Charger la playlist de niveau (souvent playlist.m3u8 référencée par master)
        #    On essaie d'accéder directement à playlist.m3u8 dans la session.
        if used_playlist is None:
            pl_resp = client.get(f"/api/stream/hls/{sid}/playlist.m3u8")
        else:
            pl_resp = client.get(used_playlist)
        assert pl_resp.status_code == 200
        assert "#EXTM3U" in pl_resp.text
        # Tenter de lire un segment référencé
        seg_name = None
        for line in pl_resp.text.splitlines():
            line = line.strip()
            if line and line.endswith(".ts"):
                seg_name = line
                break
        if seg_name:
            # Attendre un premier segment
            seg_ok = False
            for _ in range(50):
                s = client.get(f"/api/stream/hls/{sid}/{seg_name}")
                if s.status_code == 200 and len(s.content) > 0:
                    seg_ok = True
                    break
                time.sleep(0.2)
            assert seg_ok, "Aucun segment HLS lisible"

        # 5) Stopper la session
        stop = client.get("/api/stream/hls/stop", params={"sid": sid})
        assert stop.status_code == 200
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
