"""Script pour arrêter proprement le serveur"""
import os
import signal
import psutil

print("🛑 Arrêt du serveur Homeflix...")
print("=" * 70)

# Trouver le processus sur le port 8000
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        # Vérifier si c'est un processus Python qui écoute sur le port 8000
        connections = proc.net_connections()
        for conn in connections:
            if conn.laddr.port == 8000 and conn.status == 'LISTEN':
                print(f"✅ Processus trouvé: PID {proc.pid} - {proc.name()}")
                print(f"   Commande: {' '.join(proc.cmdline())}")
                
                # Terminer proprement
                print(f"\n🛑 Arrêt du processus {proc.pid}...")
                proc.terminate()
                
                # Attendre la fin (max 5 secondes)
                try:
                    proc.wait(timeout=5)
                    print("✅ Serveur arrêté proprement")
                except psutil.TimeoutExpired:
                    print("⚠️  Timeout - forçage de l'arrêt...")
                    proc.kill()
                    print("✅ Serveur forcé à s'arrêter")
                
                print("\n" + "=" * 70)
                print("✅ Serveur arrêté")
                print("\nPour redémarrer:")
                print("  cd c:\\Users\\fparo\\Desktop\\homeflix")
                print("  .\\start.ps1")
                print("\nOu:")
                print("  cd server")
                print("  python main.py")
                exit(0)
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        continue

print("⚠️  Aucun serveur trouvé sur le port 8000")
print("\nLe serveur n'est peut-être pas démarré.")
