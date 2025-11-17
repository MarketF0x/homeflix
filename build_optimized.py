"""
Script de build optimisé complet pour Homeflix
- Nettoie les caches
- Optimise les images
- Build le client
- Copie vers Electron
- Mesure l'économie d'espace
"""
import subprocess
import shutil
from pathlib import Path
import sys

def run_command(cmd, cwd=None):
    """Execute une commande shell"""
    print(f"\n▶ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Erreur: {result.stderr}")
        return False
    if result.stdout:
        print(result.stdout)
    return True

def get_dir_size(directory):
    """Calcule la taille d'un dossier"""
    total = 0
    try:
        for item in Path(directory).rglob('*'):
            if item.is_file():
                total += item.stat().st_size
    except:
        pass
    return total

def main():
    root = Path(__file__).parent
    client_dir = root / "client"
    electron_dist = root / "electron" / "dist" / "win-unpacked" / "resources"
    
    print("=" * 80)
    print("🚀 BUILD OPTIMISÉ HOMEFLIX")
    print("=" * 80)
    
    # 1. Mesure initiale
    print("\n📊 ANALYSE INITIALE")
    if electron_dist.exists():
        initial_size = get_dir_size(electron_dist)
        print(f"Taille actuelle de l'app: {initial_size/1024/1024:.2f} MB")
    
    # 2. Nettoyage
    print("\n🧹 NETTOYAGE")
    
    # Supprimer les logs
    log_count = 0
    for log_file in root.rglob('*.log'):
        try:
            log_file.unlink()
            log_count += 1
        except:
            pass
    print(f"✅ {log_count} fichiers log supprimés")
    
    # Supprimer __pycache__
    cache_count = 0
    for pycache in root.rglob('__pycache__'):
        try:
            shutil.rmtree(pycache)
            cache_count += 1
        except:
            pass
    print(f"✅ {cache_count} dossiers __pycache__ supprimés")
    
    # 3. Optimisation des images
    print("\n🎨 OPTIMISATION DES IMAGES")
    thumbs_dir = electron_dist / "data" / "thumbs"
    
    if thumbs_dir.exists():
        print(f"Dossier: {thumbs_dir}")
        
        # Lancer l'optimisation
        optimize_script = root / "optimize_thumbnails.py"
        if optimize_script.exists():
            cmd = f'python "{optimize_script}" --yes'
            subprocess.run(cmd, shell=True)
        else:
            print("⚠️  Script d'optimisation introuvable, ignoré")
    else:
        print("ℹ️  Aucun dossier de miniatures à optimiser")
    
    # 4. Build du client
    print("\n📦 BUILD DU CLIENT")
    if not run_command("npm install", cwd=client_dir):
        print("❌ Échec de l'installation des dépendances")
        return False
    
    if not run_command("npm run build", cwd=client_dir):
        print("❌ Échec du build")
        return False
    
    print("✅ Build client terminé")
    
    # 5. Copie vers Electron
    print("\n📋 COPIE VERS ELECTRON")
    client_dist = client_dir / "dist"
    electron_client = electron_dist / "client" / "dist"
    
    if client_dist.exists() and electron_client.parent.exists():
        # Supprimer l'ancien
        if electron_client.exists():
            shutil.rmtree(electron_client)
        
        # Copier le nouveau
        shutil.copytree(client_dist, electron_client)
        print(f"✅ Client copié vers {electron_client}")
    else:
        print("⚠️  Dossiers introuvables, copie ignorée")
    
    # 6. Mesure finale
    print("\n📊 RÉSULTATS")
    if electron_dist.exists():
        final_size = get_dir_size(electron_dist)
        saved = initial_size - final_size
        percent = (saved / initial_size * 100) if initial_size > 0 else 0
        
        print(f"Taille initiale:  {initial_size/1024/1024:.2f} MB")
        print(f"Taille finale:    {final_size/1024/1024:.2f} MB")
        print(f"Économie:         {saved/1024/1024:.2f} MB ({percent:.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ BUILD OPTIMISÉ TERMINÉ")
    print("=" * 80)
    
    print("\n🔄 Prochaines étapes:")
    print("   1. Tester l'application: electron\\dist\\win-unpacked\\Homeflix.exe")
    print("   2. Vérifier que tout fonctionne")
    print("   3. Rebuild l'installateur si nécessaire")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
