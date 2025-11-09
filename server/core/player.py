# core/player.py
import os
import subprocess
import platform
from pathlib import Path


def open_with_default(path: str, fullscreen: bool = True):
    """Ouvre un fichier avec le lecteur par défaut selon l'OS, en plein écran si possible."""
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    system = platform.system()

    try:
        if system == "Windows":
            # Essaie d'ouvrir avec VLC en plein écran si disponible, sinon lecteur par défaut
            vlc_paths = [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
            ]
            vlc_found = None
            for vlc_path in vlc_paths:
                if Path(vlc_path).exists():
                    vlc_found = vlc_path
                    break
            
            if vlc_found and fullscreen:
                # VLC avec plein écran et lecture automatique
                subprocess.Popen([vlc_found, "--fullscreen", "--play-and-exit", str(path_obj)])
            else:
                # Lecteur par défaut
                os.startfile(str(path_obj))
                
        elif system == "Darwin":  # macOS
            if fullscreen:
                # Essaie d'ouvrir avec VLC ou IINA en plein écran
                subprocess.run(["open", "-a", "VLC", "--args", "--fullscreen", str(path_obj)], check=False)
            else:
                subprocess.run(["open", str(path_obj)], check=True)
        else:  # Linux et autres
            if fullscreen:
                # Essaie VLC, sinon mpv, sinon défaut
                try:
                    subprocess.Popen(["vlc", "--fullscreen", str(path_obj)])
                except FileNotFoundError:
                    try:
                        subprocess.Popen(["mpv", "--fullscreen", str(path_obj)])
                    except FileNotFoundError:
                        subprocess.run(["xdg-open", str(path_obj)], check=True)
            else:
                subprocess.run(["xdg-open", str(path_obj)], check=True)
    except Exception as e:
        raise RuntimeError(f"Impossible d'ouvrir le fichier : {e}")
