# ❓ FAQ - Questions Fréquentes

## 📦 Installation et Configuration

### Comment installer Homeflix ?

Double-cliquez sur `INSTALLER.ps1`. Le script installe automatiquement toutes les dépendances nécessaires.

### Quels sont les prérequis ?

- **Windows 10/11** (64 bits)
- **Python 3.8+** - [Télécharger](https://www.python.org/downloads/)
- **Node.js 16+** - [Télécharger](https://nodejs.org/)
- **FFmpeg** (optionnel mais recommandé) - [Télécharger](https://ffmpeg.org/download.html)

### Où obtenir la clé API TMDb ?

1. Créez un compte gratuit sur [themoviedb.org](https://www.themoviedb.org)
2. Allez dans **Paramètres → API**
3. Demandez une clé API (approuvée instantanément)
4. Copiez la clé dans votre fichier `settings.yaml`

### Homeflix est-il vraiment gratuit ?

Oui ! Homeflix est **100% gratuit et open-source** sous licence MIT. Vous pouvez l'utiliser, le modifier et le distribuer librement.

---

## 🎬 Utilisation

### Comment ajouter mes vidéos ?

1. Ouvrez le fichier `settings.yaml`
2. Ajoutez vos dossiers sous `video_folders:`
3. Relancez Homeflix
4. Les vidéos seront scannées automatiquement

### Pourquoi mes vidéos ne s'affichent pas ?

**Vérifiez :**
- Les chemins dans `settings.yaml` sont corrects
- Les dossiers contiennent bien des fichiers vidéo (.mp4, .mkv, .avi, etc.)
- Vous avez relancé l'application après modification
- Les permissions d'accès aux dossiers

**Solution rapide :**
Aller dans l'interface → Paramètres → Forcer un nouveau scan

### Les affiches ne se téléchargent pas

**Causes possibles :**
- Clé API TMDb manquante ou invalide
- Pas de connexion Internet
- Nom de fichier non reconnu par TMDb

**Solutions :**
1. Vérifiez votre clé API dans `settings.yaml`
2. Vérifiez votre connexion Internet
3. Renommez vos fichiers correctement : `Film (2020).mp4`
4. Assignez manuellement via l'interface

### Comment organiser mes vidéos en collections ?

**Automatique :**
Homeflix détecte automatiquement certaines franchises (Marvel, Star Wars, etc.)

**Manuel :**
1. Clic droit sur une vidéo → "Ajouter à une collection"
2. Sélectionnez ou créez une collection
3. Répétez pour toutes les vidéos de la collection

### Comment créer un profil utilisateur ?

1. Cliquez sur l'icône profil (coin supérieur droit)
2. "Gérer les profils"
3. "Créer un nouveau profil"
4. Entrez le nom et optionnellement un mot de passe
5. Validez

---

## 🎥 Lecteur Vidéo

### Mes vidéos ne se lisent pas

**Solutions par ordre de priorité :**

1. **Installez FFmpeg** (recommandé)
   - Téléchargez depuis [ffmpeg.org](https://ffmpeg.org/download.html)
   - Ajoutez FFmpeg au PATH Windows

2. **Activez le transcodage**
   - Dans le lecteur → Paramètres → Activer le transcodage

3. **Vérifiez le format vidéo**
   - Formats supportés nativement : MP4 (H.264)
   - Autres formats nécessitent FFmpeg

### Pas de son dans mes vidéos

**Cause :** Piste audio incompatible avec le navigateur

**Solution :**
1. Activez le **transcodage FFmpeg** dans les paramètres du lecteur
2. Ou convertissez vos vidéos en MP4 avec audio AAC

### Les sous-titres ne s'affichent pas

**Vérifiez :**
1. Le fichier de sous-titres a le **même nom** que la vidéo
   - Exemple : `Film.mp4` → `Film.fr.srt`
2. Le format est supporté (SRT, VTT)
3. L'encodage est UTF-8

**Solution si encodage incorrect :**
```powershell
# Convertir en UTF-8
Get-Content fichier.srt | Set-Content fichier.srt -Encoding UTF8
```

### Comment changer la qualité de lecture ?

1. Ouvrez le lecteur vidéo
2. Cliquez sur ⚙️ (Paramètres)
3. Sélectionnez la qualité (720p, 1080p, Original)
4. La vidéo se recharge automatiquement

### La progression ne se sauvegarde pas

**Causes :**
- Aucun profil sélectionné
- Cookie bloqué
- Erreur serveur

**Solutions :**
1. Sélectionnez un profil avant de lire
2. Autorisez les cookies pour localhost
3. Vérifiez les logs serveur

---

## 🔧 Problèmes Techniques

### Erreur "Port déjà utilisé"

**Signification :** Un autre programme utilise le port 5173 ou 8000

**Solution :**
```powershell
# Trouver le processus
netstat -ano | findstr :5173

# Arrêter le processus (remplacez XXXX par le PID)
Stop-Process -Id XXXX -Force
```

### L'application ne démarre pas

**Checklist de diagnostic :**

1. ✅ Python installé ?
   ```powershell
   python --version
   ```

2. ✅ Node.js installé ?
   ```powershell
   node --version
   ```

3. ✅ Dépendances installées ?
   ```powershell
   cd client
   npm install
   cd ../server
   pip install -r requirements.txt
   ```

4. ✅ Ports libres ?
   ```powershell
   netstat -ano | findstr ":5173 :8000"
   ```

### Base de données corrompue

**Symptômes :**
- Erreurs au démarrage
- Vidéos disparues
- Profils manquants

**Solution :**
1. **Sauvegarde** : Copiez `homeflix.db` ailleurs
2. **Réparation** :
   ```powershell
   cd server
   python migrate_db.py
   ```
3. **Si échec** : Supprimez `homeflix.db` (recréé automatiquement)

⚠️ **Attention** : Supprimer la DB efface profils, collections et progression

### Erreur "Module not found"

**Cause :** Dépendances manquantes

**Solution :**
```powershell
# Client
cd client
npm install

# Serveur
cd ../server
pip install -r requirements.txt
```

---

## 🚀 Performance

### L'interface est lente

**Optimisations :**

1. **Limitez les vidéos affichées**
   - Utilisez les filtres et la recherche
   - Organisez en collections

2. **Désactivez les miniatures**
   - Dans `settings.yaml` : `generate_thumbnails: false`

3. **Optimisez les images**
   ```powershell
   python optimize_images.py
   ```

### Le scan est lent

**Causes :**
- Beaucoup de vidéos
- Disque lent
- Métadonnées TMDb

**Solutions :**
1. Réduisez le nombre de dossiers scannés
2. Utilisez un SSD
3. Scannez en arrière-plan (automatique)

### Consommation mémoire élevée

**Normal si :**
- Bibliothèque volumineuse (>1000 vidéos)
- Transcodage actif
- Plusieurs utilisateurs simultanés

**Optimisation :**
```yaml
# settings.yaml
performance:
  cache_size: 100  # Réduire le cache
  max_concurrent_scans: 2
```

---

## 🔐 Sécurité et Confidentialité

### Mes données sont-elles sécurisées ?

**Oui !** Homeflix fonctionne **100% en local** :
- ✅ Aucune donnée envoyée à des serveurs externes
- ✅ Mots de passe chiffrés avec bcrypt
- ✅ API TMDb utilisée uniquement pour métadonnées publiques
- ✅ Pas de tracking ni analytics

### Puis-je utiliser Homeflix sur mon réseau local ?

**Oui !** Homeflix est accessible depuis tous les appareils du réseau :

1. Trouvez votre IP locale :
   ```powershell
   ipconfig
   # Cherchez "Adresse IPv4"
   ```

2. Accédez depuis un autre appareil :
   ```
   http://VOTRE_IP:5173
   ```

**Recommandation sécurité :**
- Activez HTTPS (voir documentation)
- Utilisez des mots de passe forts sur les profils

### Comment protéger l'accès à Homeflix ?

**Méthodes :**

1. **Mots de passe sur profils**
   - Protège l'accès aux profils individuels

2. **Pare-feu Windows**
   - Bloquez les ports 5173/8000 pour l'extérieur
   - Autorisez uniquement le réseau local

3. **VPN** (avancé)
   - Utilisez un VPN pour accès distant sécurisé

---

## 🌐 Accès Distant

### Puis-je accéder à Homeflix depuis l'extérieur ?

**Oui**, mais **non recommandé sans sécurité** :

**Option 1 : VPN (Recommandé)**
- Installez WireGuard ou OpenVPN
- Connectez-vous à votre réseau local
- Accédez normalement à Homeflix

**Option 2 : Redirection de port (Risqué)**
- Configurez votre routeur
- ⚠️ **Activez HTTPS obligatoirement**
- ⚠️ **Utilisez des mots de passe forts**

**Option 3 : Cloudflare Tunnel (Avancé)**
- Gratuit et sécurisé
- Configuration plus complexe

---

## 📱 Compatibilité

### Quels navigateurs sont supportés ?

**Recommandés :**
- ✅ Google Chrome 90+
- ✅ Microsoft Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+

**Fonctionnalités avancées** (transcodage, sous-titres) peuvent nécessiter Chrome/Edge.

### Puis-je utiliser Homeflix sur mobile ?

**Oui !** L'interface est responsive :
- 📱 iPhone/iPad (Safari)
- 📱 Android (Chrome)

**Limitations :**
- Certains formats vidéo peuvent ne pas fonctionner
- Privilégiez MP4/H.264 pour compatibilité maximale

### Homeflix fonctionne-t-il sur Mac/Linux ?

**Actuellement :** Windows uniquement

**Futur :** Support Mac/Linux prévu si la communauté le demande

**Alternative temporaire :**
- Exécutez manuellement serveur (Python) et client (Node)
- Compatible Mac/Linux avec quelques ajustements

---

## 🆘 Support

### Où signaler un bug ?

[Ouvrir un ticket GitHub](https://github.com/MarketF0x/homeflix/issues)

**Informations utiles :**
- Version de Homeflix
- Version de Windows
- Logs (dans `server/homeflix.log`)
- Étapes pour reproduire

### Comment proposer une fonctionnalité ?

[Créer une issue GitHub](https://github.com/MarketF0x/homeflix/issues) avec le tag `enhancement`

### Où trouver de l'aide ?

1. **Documentation** : [GUIDE_UTILISATEUR.md](GUIDE_UTILISATEUR.md)
2. **FAQ** : Ce fichier
3. **Issues GitHub** : Questions existantes
4. **Créer une issue** : Pour questions spécifiques

---

## 🔄 Mises à Jour

### Comment mettre à jour Homeflix ?

1. Téléchargez la nouvelle version
2. Exécutez `INSTALLER.ps1`
3. Choisissez "Réparation"
4. Vos données sont conservées ✅

### Comment connaître ma version actuelle ?

Interface → Paramètres → À propos

Ou dans `package.json` : `"version": "1.0.0"`

### Les mises à jour sont-elles automatiques ?

Pas encore. Vérifiez manuellement sur GitHub ou activez les notifications.

---

## 🗑️ Désinstallation

### Comment désinstaller Homeflix ?

```powershell
.\DESINSTALLER.ps1
```

**Options :**
- Par défaut : Tout supprimer (DB incluse)
- `-KeepData` : Conserver la base de données
- `-Force` : Pas de confirmation

### Comment réinitialiser complètement ?

```powershell
# Supprimer tous les fichiers
.\DESINSTALLER.ps1 -Force

# Réinstaller
.\INSTALLER.ps1
```

---

**Vous ne trouvez pas votre réponse ?**
[Créez une issue GitHub](https://github.com/MarketF0x/homeflix/issues) - nous sommes là pour vous aider ! 🚀
