#!/bin/bash
# Script de lancement rapide HomeOne pour macOS/Linux
# Lance automatiquement le serveur et le client

echo ""
echo "========================================"
echo "  HomeOne - Lancement automatique"
echo "========================================"
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d ".venv" ]; then
    echo "[ERREUR] Environnement virtuel non trouvé"
    echo "Veuillez d'abord exécuter install.sh"
    exit 1
fi

# Fonction pour détecter l'OS
detect_os() {
    case "$(uname -s)" in
        Darwin*)    echo "mac";;
        Linux*)     echo "linux";;
        *)          echo "unknown";;
    esac
}

OS_TYPE=$(detect_os)

# Activer l'environnement virtuel
source .venv/bin/activate

# Démarrer le serveur en arrière-plan
echo "[1/2] Démarrage du serveur backend..."
cd server
python main.py &
SERVER_PID=$!
cd ..

# Attendre que le serveur démarre
sleep 3

# Démarrer le client en arrière-plan
echo "[2/2] Démarrage de l'interface web..."
cd client
npm run dev &
CLIENT_PID=$!
cd ..

echo ""
echo "========================================"
echo "  HomeOne est maintenant actif !"
echo "========================================"
echo ""
echo "Serveur: http://localhost:8000"
echo "Interface: http://localhost:5173"
echo ""
echo "PIDs: Server=$SERVER_PID, Client=$CLIENT_PID"
echo ""

# Ouvrir le navigateur
sleep 2
if [ "$OS_TYPE" = "mac" ]; then
    open http://localhost:5173
elif [ "$OS_TYPE" = "linux" ]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:5173
    elif command -v firefox &> /dev/null; then
        firefox http://localhost:5173 &
    elif command -v google-chrome &> /dev/null; then
        google-chrome http://localhost:5173 &
    fi
fi

echo "Pour arrêter HomeOne, appuyez sur Ctrl+C"
echo ""

# Attendre un signal d'arrêt
trap "echo 'Arrêt de HomeOne...'; kill $SERVER_PID $CLIENT_PID; exit" SIGINT SIGTERM

# Garder le script actif
wait
