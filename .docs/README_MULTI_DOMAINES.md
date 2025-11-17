# 🏠 HomeOne - Configuration Multi-Domaines

## 🎯 Vue d'ensemble

HomeOne peut maintenant afficher différents noms de domaine dans la barre d'URL selon votre type de connexion :

| Domaine | Utilisation | Affichage |
|---------|-------------|-----------|
| **homeone.local** | Réseau local (ce PC) | "HomeOne Local" |
| **homeone.wifi** | Connexion WiFi | "HomeOne WiFi" 📡 |
| **homeone.web** | Accès distant (Tailscale) | "HomeOne Web" 🌍 |
| **homeone.lan** | Connexion Ethernet | "HomeOne LAN" 🔌 |

---

## 🚀 Démarrage rapide

### 1. Configuration initiale (une seule fois)

**Exécutez en tant qu'administrateur** (clic droit > Exécuter en tant qu'administrateur) :

```powershell
.\setup-multi-domains.ps1
```

Ce script va :
- ✅ Détecter vos adresses IP (WiFi, Ethernet, Tailscale)
- ✅ Configurer les domaines dans le fichier hosts
- ✅ Générer un certificat SSL pour tous les domaines
- ✅ Afficher les URLs d'accès disponibles

### 2. Démarrage de l'application

**Méthode simple** (double-clic) :

```powershell
.\start-homeone.ps1
```

Ce script va :
- 🔍 Vérifier la configuration
- 🐍 Démarrer le serveur FastAPI
- ⚡ Démarrer le serveur Vite
- 🌐 Ouvrir le navigateur automatiquement
- 📊 Afficher toutes les URLs d'accès

---

## 📱 Configuration sur téléphone/tablette

### Option 1 : Tailscale MagicDNS (RECOMMANDÉ)

**La solution la plus simple et automatique :**

1. Exécutez (en tant qu'administrateur) :
   ```powershell
   .\setup-tailscale-dns.ps1
   ```

2. Sur votre téléphone :
   - Installez Tailscale
   - Connectez-vous avec le même compte
   - Accédez à : `http://homeone:5173`

✅ **Avantage** : Fonctionne partout, même hors de chez vous !

### Option 2 : Application Hosts Editor

**Pour WiFi local uniquement :**

1. Installez une app :
   - Android : "Virtual Hosts" ou "Hosts Editor"
   - iOS : "Surge" (payant) ou "Shadowrocket"

2. Ajoutez l'entrée :
   ```
   192.168.x.x → homeone.wifi
   ```

3. Accédez à : `http://homeone.wifi:5173`

### Option 3 : Serveur DNS (Pi-hole, AdGuard Home)

**Pour toute la maison automatiquement :**

1. Installez Pi-hole ou AdGuard Home
2. Configurez le DNS :
   ```
   homeone.wifi → 192.168.x.x
   homeone.web → 100.72.x.x
   ```
3. Configurez votre routeur pour utiliser ce DNS
4. Tous les appareils auront accès automatiquement !

---

## 🔒 Configuration HTTPS (optionnel)

### Pourquoi HTTPS ?

- 🔐 Connexion sécurisée
- 📱 Certains navigateurs mobiles bloquent HTTP sur réseau distant
- ✅ Meilleure compatibilité

### Comment activer ?

**Déjà fait si vous avez exécuté `setup-multi-domains.ps1` !**

Sinon, exécutez :

```powershell
.\setup-https.ps1
```

Les URLs deviendront :
- `https://homeone.local:5173`
- `https://homeone.wifi:5173`
- `https://homeone.web:5173`

**Note** : Vous devrez accepter l'avertissement de sécurité (certificat auto-signé) une seule fois sur chaque appareil.

---

## 🌐 Pare-feu Windows

Si vous ne pouvez pas vous connecter depuis un autre appareil :

```powershell
.\configure-network-access.ps1
```

Ce script ouvre les ports nécessaires (8000, 8443, 5173).

---

## 🎨 Interface utilisateur

### Badge de connexion

Un badge coloré s'affiche en haut à droite pour indiquer le type de connexion :

- 🏠 **HomeOne Local** (gris) : localhost
- 📡 **HomeOne WiFi** (jaune) : Connexion WiFi
- 🌍 **HomeOne Web** (bleu) : Accès distant (Tailscale)
- 🔌 **HomeOne LAN** (violet) : Connexion Ethernet

Cliquez sur le badge pour voir les détails de connexion.

### Titre de l'onglet

Le titre de l'onglet du navigateur affiche automatiquement le nom selon votre connexion :
- "HomeOne Local"
- "HomeOne WiFi"
- "HomeOne Web"

---

## 🔧 Dépannage

### ❌ "homeone.wifi" ne fonctionne pas

**Sur Windows :**
```powershell
# Vider le cache DNS
ipconfig /flushdns

# Vérifier le fichier hosts
notepad C:\Windows\System32\drivers\etc\hosts
```

**Sur téléphone :**
- Redémarrez l'appareil
- Vérifiez la configuration de l'app Hosts Editor
- Essayez avec l'IP directe : `http://192.168.x.x:5173`

### ❌ Connexion refusée

1. Vérifiez que les serveurs sont démarrés :
   ```powershell
   netstat -ano | findstr ":5173"
   netstat -ano | findstr ":8000"
   ```

2. Configurez le pare-feu :
   ```powershell
   .\configure-network-access.ps1
   ```

3. Vérifiez que vous êtes sur le même réseau WiFi

### ❌ Certificat SSL invalide

C'est **normal** avec un certificat auto-signé.

**Sur navigateur :**
- Chrome/Edge : Cliquez sur "Avancé" → "Continuer"
- Firefox : Cliquez sur "Avancé" → "Accepter le risque"
- Safari : "Afficher les détails" → "Visiter ce site web"

**Sur téléphone :**
- Acceptez l'avertissement (une seule fois par appareil)
- Ou utilisez HTTP au lieu de HTTPS

---

## 📊 Récapitulatif des fichiers

| Fichier | Description | Exécution |
|---------|-------------|-----------|
| `setup-multi-domains.ps1` | Configuration complète (domaines + SSL) | Admin requis |
| `setup-https.ps1` | Génération certificat SSL uniquement | Admin optionnel |
| `setup-tailscale-dns.ps1` | Configuration Tailscale MagicDNS | Normal |
| `configure-network-access.ps1` | Ouverture ports pare-feu | Admin requis |
| `start-homeone.ps1` | Démarrage de l'application | Normal |

---

## 🎯 Exemple d'utilisation

### Sur votre PC (localhost) :

1. Double-cliquez sur `start-homeone.ps1`
2. Le navigateur s'ouvre sur `http://homeone.local:5173`
3. Le badge affiche : **🏠 HomeOne Local**

### Sur votre téléphone (WiFi) :

1. Configurez l'app Hosts Editor : `192.168.1.5 → homeone.wifi`
2. Ouvrez : `http://homeone.wifi:5173`
3. Le badge affiche : **📡 HomeOne WiFi**

### Sur votre téléphone (hors de chez vous via Tailscale) :

1. Connectez Tailscale sur le téléphone
2. Ouvrez : `http://homeone.web:5173`
3. Le badge affiche : **🌍 HomeOne Web**

---

## 💡 Conseils

### Pour une expérience optimale :

1. ✅ Utilisez Tailscale MagicDNS (accès partout)
2. ✅ Activez HTTPS (plus sécurisé)
3. ✅ Configurez le pare-feu (accès réseau)
4. ✅ Utilisez `start-homeone.ps1` (démarrage simplifié)

### URLs recommandées :

- **Sur PC** : `https://homeone.local:5173`
- **Sur téléphone (WiFi)** : `https://homeone.wifi:5173`
- **Sur téléphone (distant)** : `https://homeone.web:5173` (via Tailscale)

---

**Fait avec ❤️ pour HomeOne**

Pour plus d'aide, consultez :
- `GUIDE_HOMEONE_DOMAIN.md` (guide détaillé)
- `homeone-config.txt` (configuration actuelle)
