#!/bin/bash
# Script d'installation automatique HomeOne pour macOS/Linux
# Exécuter avec: chmod +x install.sh && ./install.sh

echo "🎬 Installation de HomeOne - Gestionnaire de bibliothèque vidéo"
echo "================================================================"
echo ""

# Détection de l'OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     OS_TYPE=Linux;;
    Darwin*)    OS_TYPE=Mac;;
    *)          OS_TYPE="UNKNOWN:${OS}"
esac

echo "🖥️  Système détecté: $OS_TYPE"
echo ""

# Vérification de Python
echo "🔍 Vérification de Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python trouvé: $PYTHON_VERSION"
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✅ Python trouvé: $PYTHON_VERSION"
    PYTHON_CMD=python
else
    echo "❌ Python n'est pas installé!"
    echo "   Installation:"
    if [ "$OS_TYPE" = "Mac" ]; then
        echo "   brew install python@3.11"
    else
        echo "   sudo apt install python3.10 python3-pip python3-venv"
    fi
    exit 1
fi

# Vérification de Node.js
echo "🔍 Vérification de Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js trouvé: $NODE_VERSION"
else
    echo "❌ Node.js n'est pas installé!"
    echo "   Installation:"
    if [ "$OS_TYPE" = "Mac" ]; then
        echo "   brew install node"
    else
        echo "   sudo apt install nodejs npm"
    fi
    exit 1
fi

# Vérification de FFmpeg (optionnel)
echo "🔍 Vérification de FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version | head -n 1)
    echo "✅ FFmpeg trouvé: $FFMPEG_VERSION"
else
    echo "⚠️  FFmpeg non trouvé (optionnel)"
    echo "   Les miniatures seront récupérées depuis TMDb uniquement"
    echo "   Pour installer FFmpeg:"
    if [ "$OS_TYPE" = "Mac" ]; then
        echo "   brew install ffmpeg"
    else
        echo "   sudo apt install ffmpeg"
    fi
fi

echo ""
echo "📦 Installation des dépendances..."

# Créer l'environnement virtuel Python
if [ ! -d ".venv" ]; then
    echo "🔧 Création de l'environnement virtuel Python..."
    $PYTHON_CMD -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ Erreur lors de la création de l'environnement virtuel"
        exit 1
    fi
    echo "✅ Environnement virtuel créé"
else
    echo "✅ Environnement virtuel déjà présent"
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source .venv/bin/activate

# Installer les dépendances Python
echo "🔧 Installation des dépendances Python..."
pip install -r server/requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'installation des dépendances Python"
    exit 1
fi
echo "✅ Dépendances Python installées"

# Installer les dépendances Node.js
echo "🔧 Installation des dépendances Node.js..."
cd client
npm install --silent
if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'installation des dépendances Node.js"
    cd ..
    exit 1
fi
cd ..
echo "✅ Dépendances Node.js installées"

# Créer le dossier de configuration si nécessaire
CONFIG_DIR="$HOME/.homeone"
if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
fi

# Vérifier le fichier settings.yaml
echo ""
echo "🔧 Configuration..."
if [ ! -f "settings.yaml" ]; then
    echo "⚠️  Fichier settings.yaml introuvable"
    echo "   Création d'un fichier de configuration par défaut..."
    
    cat > settings.yaml << 'EOF'
# Répertoires à scanner pour les vidéos
video_directories:
  - "~/Movies"
  - "~/Videos"

# Durées minimales/maximales pour filtrer films/séries
min_film_minutes: 75      # >= 1h15 = film
max_series_minutes: 55    # entre 20 et 55 min = série

# Mode de session par défaut (mixed | films | series)
session_mode: mixed

# Clé API TMDb pour récupérer les métadonnées en ligne (gratuit)
# Obtenez votre clé sur: https://www.themoviedb.org/settings/api
tmdb_api_key: ""

# Nettoyage automatique des noms de fichiers (true/false)
auto_clean_filenames: true

# Langue de l'interface (fr/en/de/es)
language: fr
EOF
    
    echo "✅ Fichier settings.yaml créé"
    echo ""
    echo "⚠️  IMPORTANT: Éditez settings.yaml pour:"
    echo "   1. Ajouter vos répertoires vidéo"
    echo "   2. Ajouter votre clé API TMDb (optionnel mais recommandé)"
else
    echo "✅ Fichier settings.yaml trouvé"
fi

echo ""
echo "✨ Installation terminée avec succès!"
echo ""
echo "📝 Prochaines étapes:"
echo "   1. Éditez settings.yaml pour configurer vos répertoires vidéo"
echo "   2. Obtenez une clé API TMDb sur: https://www.themoviedb.org/settings/api"
echo "   3. Démarrez le serveur: source .venv/bin/activate && cd server && python main.py"
echo "   4. Dans un autre terminal, démarrez le client: cd client && npm run dev"
echo "   5. Ouvrez votre navigateur sur: http://localhost:5173"
echo ""
echo "🚀 Pour un lancement rapide, créez un alias dans votre ~/.bashrc ou ~/.zshrc:"
echo "   alias homeone='cd $(pwd) && source .venv/bin/activate && cd server && python main.py'"
echo ""
