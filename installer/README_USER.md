# 🎬 HomeFlix - Installation Complète

## ✅ Installation réussie !

Félicitations, HomeFlix est maintenant installé sur votre ordinateur.

---

## 🚀 Démarrage rapide

### Lancer HomeFlix

**Méthode 1 - Raccourci bureau**
- Double-cliquez sur l'icône "HomeFlix" sur votre bureau

**Méthode 2 - Menu Démarrer**
- Recherchez "HomeFlix" dans le menu Démarrer
- Cliquez sur l'application

**Méthode 3 - Ligne de commande**
```powershell
cd "C:\Program Files\HomeFlix"
.\homeflix-launcher.exe
```

### Premier lancement

1. **L'application démarre automatiquement** le serveur backend
2. **Votre navigateur s'ouvre** sur http://localhost:8000
3. **Patientez quelques secondes** le temps que tout se charge

---

## 📱 Accès depuis d'autres appareils

### Sur votre réseau local

Vous pouvez accéder à HomeFlix depuis :
- Votre téléphone
- Votre tablette
- Un autre ordinateur
- Votre TV connectée

**Adresse à utiliser :** `http://[IP-DE-VOTRE-PC]:8000`

### Trouver votre adresse IP

**Windows :**
```powershell
# Ouvrir PowerShell et taper :
Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" }
```

**Ou via l'interface :**
1. Paramètres Windows → Réseau et Internet
2. Wi-Fi ou Ethernet (selon votre connexion)
3. Propriétés → Chercher "Adresse IPv4"

**Exemple :** Si votre IP est `192.168.1.100`, accédez à `http://192.168.1.100:8000`

---

## ⚙️ Configuration

### Fichier de configuration

Situé dans : `C:\Program Files\HomeFlix\settings.yaml`

```yaml
# Dossiers à scanner pour les vidéos
video_directories:
  - "C:\Users\VotreNom\Videos"
  - "D:\Films"
  - "E:\Series"

# Clé API TMDb (pour les affiches et métadonnées)
tmdb_api_key: "votre_cle_api_ici"

# Durées minimales/maximales pour différencier films/séries
min_film_minutes: 75      # Films >= 75 min
max_series_minutes: 55    # Séries entre 20 et 55 min

# Mode de session par défaut
session_mode: mixed       # mixed | films | series

# Langue de l'interface
language: fr              # fr | en | es
```

### Obtenir une clé API TMDb (GRATUIT)

1. Créez un compte sur https://www.themoviedb.org
2. Allez dans Paramètres → API
3. Demandez une clé API (usage personnel)
4. Copiez la clé dans `settings.yaml`

**Sans clé API :** Les vidéos seront détectées mais sans affiches automatiques.

---

## 🔧 Utilisation

### Scanner vos vidéos

**Scan automatique :**
- HomeFlix scanne vos dossiers au démarrage
- Les nouvelles vidéos sont détectées automatiquement

**Scan manuel :**
1. Ouvrez HomeFlix
2. Cliquez sur "Scan" dans le menu
3. Attendez la fin du scan

### Organisation

**Par collections :**
- Les films d'une même saga sont groupés automatiquement
- Exemple : "Harry Potter", "Star Wars", etc.

**Par année :**
- Filtrez par année de sortie

**Par genre :**
- Action, Comédie, Drame, etc.

**Reprendre la lecture :**
- HomeFlix mémorise où vous vous êtes arrêté
- Reprenez vos vidéos où vous voulez

---

## 🔥 Pare-feu Windows

### Si le pare-feu bloque

**Autoriser HomeFlix :**

```powershell
# Ouvrir PowerShell en Administrateur et exécuter :
New-NetFirewallRule -DisplayName "HomeFlix Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
New-NetFirewallRule -DisplayName "HomeFlix Frontend" -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow
```

**Ou via l'interface :**
1. Paramètres Windows → Pare-feu
2. Autoriser une application
3. Ajouter HomeFlix

---

## 🛠️ Dépannage

### Le serveur ne démarre pas

**Vérifier Python :**
```powershell
python --version
# Doit afficher : Python 3.10.x ou supérieur
```

**Vérifier les ports :**
```powershell
netstat -ano | findstr ":8000"
# Si occupé, fermer l'application qui l'utilise
```

**Logs d'erreur :**
```powershell
# Consulter les logs
Get-Content "C:\Program Files\HomeFlix\server\homeflix.log" -Tail 50
```

### Les vidéos ne s'affichent pas

1. **Vérifier les dossiers** dans `settings.yaml`
2. **Lancer un scan manuel**
3. **Vérifier les formats** : `.mp4`, `.mkv`, `.avi`, `.mov`, `.m4v`, `.webm`

### Pas d'affiches

1. **Ajouter une clé API TMDb** dans `settings.yaml`
2. **Relancer le scan**
3. **Vérifier la connexion Internet**

### L'accès réseau ne fonctionne pas

1. **Vérifier le pare-feu** (voir section ci-dessus)
2. **Vérifier l'adresse IP** (peut changer si DHCP)
3. **Être sur le même réseau WiFi/Ethernet**

---

## 📁 Emplacements importants

| Fichier | Emplacement |
|---------|-------------|
| **Application** | `C:\Program Files\HomeFlix\` |
| **Configuration** | `C:\Program Files\HomeFlix\settings.yaml` |
| **Base de données** | `C:\Program Files\HomeFlix\server\homeflix.db` |
| **Logs** | `C:\Program Files\HomeFlix\server\homeflix.log` |
| **Affiches** | `C:\Program Files\HomeFlix\data\posters\` |
| **Miniatures** | `C:\Program Files\HomeFlix\data\thumbs\` |

---

## 🔄 Mise à jour

### Vérifier les mises à jour

HomeFlix vérifie automatiquement les nouvelles versions au démarrage.

### Installer une mise à jour

1. **Télécharger** le nouvel installateur
2. **Exécuter** `HomeFlix-Setup-X.X.X.exe`
3. L'installateur **préserve** vos données et configuration
4. **Redémarrer** HomeFlix

---

## 🗑️ Désinstallation

### Désinstaller proprement

**Via le Panneau de configuration :**
1. Paramètres Windows → Applications
2. Chercher "HomeFlix"
3. Cliquer sur "Désinstaller"

**Ou via l'installateur :**
1. Aller dans `C:\Program Files\HomeFlix\`
2. Exécuter `unins000.exe`

### Ce qui est conservé

- ❌ **L'application est supprimée**
- ✅ **Vos vidéos restent intactes** (ne sont JAMAIS supprimées)
- ⚠️ **Base de données** : Option de conservation proposée
- ⚠️ **Configuration** : Option de conservation proposée

---

## 📞 Support & Aide

### Documentation complète

- 📚 Guide utilisateur : https://github.com/homeflix/wiki
- 🎓 Tutoriels vidéo : https://github.com/homeflix/tutorials
- ❓ FAQ : https://github.com/homeflix/faq

### Signaler un problème

Ouvrez une issue sur GitHub :
https://github.com/homeflix/issues

**Incluez :**
- Version de HomeFlix
- Version de Windows
- Description du problème
- Logs si possible

### Communauté

- 💬 Discord : https://discord.gg/homeflix
- 🐦 Twitter : @homeflix_app
- 📧 Email : support@homeflix.app

---

## 📄 Licence

HomeFlix est un logiciel libre sous licence MIT.

**Ce que vous pouvez faire :**
- ✅ Utiliser gratuitement
- ✅ Modifier le code
- ✅ Distribuer
- ✅ Usage commercial

**Mentions légales :**
- Ce produit utilise l'API TMDb mais n'est ni approuvé ni certifié par TMDb
- Les affiches et métadonnées appartiennent à leurs propriétaires respectifs

---

## 🎉 Profitez de HomeFlix !

Merci d'avoir choisi HomeFlix pour gérer votre bibliothèque vidéo !

**N'oubliez pas de :**
- ⭐ Mettre une étoile sur GitHub
- 📣 Partager avec vos amis
- 💡 Proposer des améliorations

**Bon visionnage ! 🍿**
