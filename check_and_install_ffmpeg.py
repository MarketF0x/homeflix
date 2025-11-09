#!/usr/bin/env python3
"""
Vérificateur et installateur automatique de FFmpeg pour HomeOne
Vérifie si FFmpeg est installé, sinon propose de l'installer automatiquement
"""

import subprocess
import sys
import platform
from pathlib import Path

def check_ffmpeg():
    """Vérifie si FFmpeg est installé et accessible."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            return True, version_line
        return False, None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, None

def check_chocolatey():
    """Vérifie si Chocolatey est installé (Windows)."""
    try:
        result = subprocess.run(
            ["choco", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def install_ffmpeg_windows():
    """Installe FFmpeg sur Windows."""
    print("\n" + "="*60)
    print("  Installation de FFmpeg sur Windows")
    print("="*60 + "\n")
    
    # Vérifier Chocolatey
    if check_chocolatey():
        print("📦 Chocolatey détecté - Installation via Chocolatey...")
        print("\n⚠️  Une fenêtre PowerShell va s'ouvrir.")
        print("   Attendez que l'installation se termine.\n")
        
        # Lancer le script PowerShell
        ps_script = Path(__file__).parent / "install_ffmpeg.ps1"
        if ps_script.exists():
            subprocess.run([
                "powershell",
                "-ExecutionPolicy", "Bypass",
                "-File", str(ps_script)
            ])
        else:
            # Fallback : installation directe via choco
            subprocess.run(["choco", "install", "ffmpeg", "-y"])
    else:
        print("📥 Installation manuelle recommandée")
        print("\nPour installer FFmpeg automatiquement :")
        print("  1. Exécutez : .\\install_ffmpeg.ps1")
        print("\nOu installez manuellement :")
        print("  1. Téléchargez : https://www.gyan.dev/ffmpeg/builds/")
        print("  2. Extrayez dans C:\\ffmpeg")
        print("  3. Ajoutez C:\\ffmpeg\\bin au PATH")

def install_ffmpeg_macos():
    """Installe FFmpeg sur macOS."""
    print("\n📦 Installation de FFmpeg sur macOS...\n")
    print("Exécution de : brew install ffmpeg\n")
    subprocess.run(["brew", "install", "ffmpeg"])

def install_ffmpeg_linux():
    """Installe FFmpeg sur Linux."""
    print("\n📦 Installation de FFmpeg sur Linux...\n")
    
    # Détecter la distribution
    distros = {
        "ubuntu": ["sudo", "apt", "update", "&&", "sudo", "apt", "install", "-y", "ffmpeg"],
        "debian": ["sudo", "apt", "update", "&&", "sudo", "apt", "install", "-y", "ffmpeg"],
        "fedora": ["sudo", "dnf", "install", "-y", "ffmpeg"],
        "arch": ["sudo", "pacman", "-S", "--noconfirm", "ffmpeg"],
    }
    
    print("Commandes d'installation selon votre distribution :")
    for distro, cmd in distros.items():
        print(f"\n{distro.capitalize()}: {' '.join(cmd)}")

def main():
    """Point d'entrée principal."""
    print("\n" + "="*60)
    print("  🎬 HomeOne - Vérification FFmpeg")
    print("="*60)
    
    # Vérifier FFmpeg
    installed, version = check_ffmpeg()
    
    if installed:
        print(f"\n✅ FFmpeg est déjà installé !")
        print(f"   {version}\n")
        return 0
    
    print("\n⚠️  FFmpeg n'est pas installé")
    print("\nFFmpeg est nécessaire pour :")
    print("  • Générer des miniatures depuis vos vidéos")
    print("  • Extraire des métadonnées (durée, résolution)")
    print("  • Avoir 100% de miniatures fonctionnelles\n")
    
    # Demander confirmation
    response = input("Voulez-vous installer FFmpeg maintenant ? (o/n) : ").strip().lower()
    
    if response not in ['o', 'oui', 'y', 'yes']:
        print("\n❌ Installation annulée")
        print("\nVous pouvez l'installer plus tard avec :")
        print("  • Windows : .\\install_ffmpeg.ps1")
        print("  • macOS   : brew install ffmpeg")
        print("  • Linux   : sudo apt install ffmpeg\n")
        return 1
    
    # Installation selon l'OS
    system = platform.system()
    
    if system == "Windows":
        install_ffmpeg_windows()
    elif system == "Darwin":
        install_ffmpeg_macos()
    elif system == "Linux":
        install_ffmpeg_linux()
    else:
        print(f"\n❌ Système d'exploitation non supporté : {system}")
        return 1
    
    # Revérifier
    print("\n🔍 Vérification de l'installation...")
    installed, version = check_ffmpeg()
    
    if installed:
        print(f"\n✅ FFmpeg installé avec succès !")
        print(f"   {version}")
        print("\n📝 Prochaine étape : Générer les miniatures")
        print("   Exécutez : python repair_thumbnails.py\n")
        return 0
    else:
        print("\n⚠️  FFmpeg n'est pas encore accessible")
        print("   Redémarrez votre terminal et réessayez\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
