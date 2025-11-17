# 🌐 Configuration de l'accès réseau pour Homeflix

Ce guide vous aide à configurer Homeflix pour un accès depuis d'autres appareils sur votre réseau local (Wi-Fi/LAN).

---

## 📋 Prérequis

- ✅ Homeflix installé et fonctionnel en local
- ✅ Tous les appareils connectés au même réseau Wi-Fi/routeur
- ✅ Droits administrateur Windows (pour la configuration du pare-feu)

---

## ⚡ Configuration rapide (3 étapes)

### 1️⃣ Configurer le pare-feu Windows

**Exécutez en tant qu'administrateur :**

```powershell
# Clic droit sur PowerShell → "Exécuter en tant qu'administrateur"
cd C:\Users\fparo\Desktop\homeflix
.\configure-firewall.ps1
```

Ce script va :
- ✅ Créer une règle pour le port **5173** (client Vite)
- ✅ Créer une règle pour le port **8000** (serveur API)
- ✅ Afficher votre adresse IP locale

### 2️⃣ Démarrer les serveurs

```powershell
# Dans PowerShell normal (pas besoin d'admin)
.\start-dev.ps1
```

Attendez que les deux serveurs démarrent :
- 🟢 Serveur API : `http://0.0.0.0:8000`
- 🟢 Client Vite : `http://0.0.0.0:5173`

### 3️⃣ Accéder depuis un appareil distant

Sur votre téléphone/tablette/autre PC, ouvrez le navigateur et accédez à :

```
http://192.168.1.5:5173
```

> ⚠️ Remplacez `192.168.1.5` par l'IP affichée lors de l'étape 1

---

## 🔍 Vérifications en cas de problème

### ✅ Le pare-feu est-il configuré ?

```powershell
Get-NetFirewallRule -DisplayName "Homeflix*" | Format-Table DisplayName, Enabled, Direction, Action
```

Vous devez voir 2 règles **Enabled** :
- `Homeflix - Client Vite (5173)`
- `Homeflix - Serveur API (8000)`

### ✅ Les serveurs sont-ils démarrés ?

```powershell
netstat -ano | findstr ":5173 :8000"
```

Vous devez voir deux lignes avec `LISTENING` :
```
TCP    0.0.0.0:5173    0.0.0.0:0    LISTENING    12345
TCP    0.0.0.0:8000    0.0.0.0:0    LISTENING    67890
```

### ✅ Quelle est mon adresse IP ?

```powershell
ipconfig | findstr "IPv4"
```

Cherchez l'adresse sous **Wi-Fi** ou **Ethernet** (ex: `192.168.1.x`)

---

## 🛠️ Dépannage

### Erreur : "Impossible de se connecter au serveur"

**Causes possibles :**

1. **Le pare-feu bloque toujours** → Relancez `configure-firewall.ps1` en admin
2. **Mauvaise IP** → Vérifiez avec `ipconfig`
3. **Réseau différent** → Les appareils doivent être sur le même Wi-Fi
4. **Serveur non démarré** → Vérifiez avec `netstat`

### Les vidéos ne s'affichent pas

Si l'utilisateur distant voit l'interface mais pas les miniatures :

1. Vérifiez que le serveur API répond :
   ```
   http://192.168.1.5:8000/api/videos?mode=mixed
   ```
   
2. Testez une miniature :
   ```
   http://192.168.1.5:8000/api/thumbnail?path=C%3A%2Fvideos%2Ffilm.mp4
   ```

3. Redémarrez le serveur si nécessaire

### Le pare-feu de ma box/routeur bloque

Certains routeurs ont un pare-feu intégré. Consultez :
- Interface d'administration de votre box (généralement `192.168.1.1` ou `192.168.0.1`)
- Section "Pare-feu" ou "Sécurité"
- Autorisez les ports `5173` et `8000` en **TCP entrant**

---

## 🔒 Sécurité

### ⚠️ Important

- **N'exposez PAS** ces ports sur Internet (via redirection de ports)
- **Utilisez uniquement** sur votre réseau local privé
- **Aucun mot de passe** n'est configuré par défaut
- **Tous les utilisateurs** du réseau ont accès complet

### 🛡️ Pour un accès sécurisé depuis Internet

Si vous souhaitez vraiment accéder depuis l'extérieur :
1. Utilisez un VPN (OpenVPN, WireGuard, etc.)
2. OU configurez un tunnel sécurisé (ngrok, Tailscale, etc.)

---

## 📱 Appareils testés

| Appareil | Navigateur | Statut |
|----------|-----------|--------|
| Android | Chrome | ✅ |
| iOS | Safari | ✅ |
| Windows | Chrome/Edge | ✅ |
| macOS | Safari/Chrome | ✅ |
| Smart TV | Navigateur intégré | ⚠️ Partiel |

---

## 💡 Astuces

### Créer un raccourci sur mobile

1. Ouvrez `http://192.168.1.5:5173` dans le navigateur
2. **Android** : Menu → "Ajouter à l'écran d'accueil"
3. **iOS** : Partager → "Sur l'écran d'accueil"

### Nom de domaine local (optionnel)

Au lieu d'utiliser l'IP, configurez un nom dans votre fichier `hosts` :

**Windows :** `C:\Windows\System32\drivers\etc\hosts`
```
192.168.1.5    homeflix.local
```

Accès via : `http://homeflix.local:5173`

---

## 📞 Support

Des problèmes ? Vérifiez dans l'ordre :

1. ✅ Pare-feu Windows configuré
2. ✅ Serveurs démarrés (`start-dev.ps1`)
3. ✅ IP correcte (`ipconfig`)
4. ✅ Même réseau Wi-Fi
5. ✅ Message d'erreur détaillé dans le navigateur

Le client affiche maintenant des messages d'erreur détaillés avec instructions !

---

**Version :** 2.4  
**Dernière mise à jour :** Novembre 2025
