# 🏠 Guide : Utiliser "homeone.local" au lieu de l'adresse IP

Ce guide explique comment accéder à votre serveur Homeflix via le nom **homeone.local** au lieu de l'adresse IP.

---

## 🎯 Objectif

Au lieu de taper `http://192.168.1.5:5173` ou `http://100.72.164.87:5173`, vous pourrez utiliser :
- `http://homeone.local:5173`
- `https://homeone.local:5173`

---

## 📋 Solutions disponibles

### ✅ Solution 1 : Tailscale MagicDNS (RECOMMANDÉ)

**Avantages :**
- ✅ Fonctionne depuis n'importe où (même hors de chez vous)
- ✅ Configuration automatique sur tous les appareils
- ✅ Aucune modification manuelle nécessaire
- ✅ Sécurisé et chiffré

**Configuration :**

1. **Exécutez le script (clic droit > Exécuter en tant qu'administrateur) :**
   ```powershell
   .\setup-tailscale-dns.ps1
   ```

2. **Le script va :**
   - Vérifier que Tailscale est installé et connecté
   - Proposer de renommer votre PC en "homeone"
   - Afficher votre nom MagicDNS (ex: `homeone.tail1234.ts.net`)

3. **Sur votre téléphone :**
   - Installez Tailscale (App Store / Google Play)
   - Connectez-vous avec le même compte
   - Ouvrez : `http://homeone:5173`

**Résultat :** Accès via `http://homeone:5173` depuis tous vos appareils Tailscale

---

### ✅ Solution 2 : Fichier hosts local

**Avantages :**
- ✅ Simple et rapide sur Windows
- ✅ Pas besoin de logiciel supplémentaire
- ✅ Fonctionne immédiatement sur ce PC

**Inconvénients :**
- ❌ Nécessite configuration sur chaque appareil
- ❌ Fonctionne uniquement sur le réseau local

**Configuration :**

1. **Exécutez le script (clic droit > Exécuter en tant qu'administrateur) :**
   ```powershell
   .\setup-homeone-domain.ps1
   ```

2. **Le script va :**
   - Détecter votre adresse IP locale
   - Modifier le fichier `C:\Windows\System32\drivers\etc\hosts`
   - Ajouter l'entrée : `192.168.x.x homeone.local`
   - Vider le cache DNS

3. **Sur ce PC, vous pouvez maintenant utiliser :**
   - `http://homeone.local:5173`

**Configuration sur téléphone/tablette :**

Vous avez 3 options :

#### Option A : Application DNS Override (le plus simple)
1. Installez une app comme "DNS Override" ou "Hosts Editor"
2. Ajoutez : `192.168.x.x → homeone.local`
3. Activez l'override

#### Option B : Pi-hole ou AdGuard Home (pour toute la maison)
1. Installez Pi-hole ou AdGuard Home sur un Raspberry Pi ou PC
2. Configurez votre routeur pour utiliser ce DNS
3. Ajoutez l'entrée DNS : `homeone.local → 192.168.x.x`
4. Tous les appareils de la maison auront accès automatiquement

#### Option C : Modification DNS manuelle (non recommandé)
- Sur Android : Paramètres > WiFi > IP statique > DNS
- Sur iOS : Réglages > WiFi > Configurer DNS

---

### ✅ Solution 3 : Routeur avec DNS personnalisé

**Avantages :**
- ✅ Configuration une seule fois
- ✅ Tous les appareils du réseau local en profitent
- ✅ Pas besoin de configurer chaque appareil

**Inconvénients :**
- ❌ Nécessite accès à l'interface du routeur
- ❌ Tous les routeurs ne supportent pas cette fonction

**Configuration :**

1. Connectez-vous à votre routeur (généralement `192.168.1.1` ou `192.168.0.1`)

2. Cherchez la section DNS ou "Local DNS" ou "Static DNS"

3. Ajoutez une entrée :
   - Nom : `homeone.local`
   - IP : `192.168.x.x` (votre IP locale)

4. Sauvegardez et redémarrez le routeur si nécessaire

**Marques populaires :**
- **TP-Link** : Advanced > DHCP > Address Reservation + DNS
- **Netgear** : Advanced > Setup > DNS
- **Asus** : LAN > DHCP Server > DNS Server
- **Fritz!Box** : Network > Network Connections > Add DNS

---

## 🔒 Configuration HTTPS avec le nom de domaine

Une fois le nom configuré, activez HTTPS :

1. **Générez les certificats SSL :**
   ```powershell
   .\setup-https.ps1
   ```

2. **Redémarrez le serveur**

3. **Accédez via :**
   - `https://homeone.local:5173`

4. **Acceptez l'avertissement de sécurité** (certificat auto-signé)

---

## 🧪 Test de configuration

**Sur Windows (PowerShell) :**
```powershell
# Test DNS
nslookup homeone.local

# Test ping
ping homeone.local

# Test HTTP
Start-Process "http://homeone.local:5173"
```

**Sur téléphone :**
1. Ouvrez le navigateur
2. Tapez : `http://homeone.local:5173`
3. Si ça ne fonctionne pas, essayez : `https://homeone.local:5173`

---

## 🔧 Dépannage

### ❌ "homeone.local" ne se résout pas

**Sur Windows :**
```powershell
# Vider le cache DNS
ipconfig /flushdns

# Vérifier le fichier hosts
notepad C:\Windows\System32\drivers\etc\hosts
```

**Sur téléphone :**
- Vérifiez que vous êtes sur le même réseau WiFi
- Redémarrez l'appareil
- Vérifiez la configuration DNS

### ❌ "Connexion refusée"

**Vérifiez le firewall :**
```powershell
# Vérifier les règles firewall
netsh advfirewall firewall show rule name="Homeflix FastAPI"

# Créer la règle si nécessaire
.\configure-network-access.ps1
```

**Vérifiez que le serveur tourne :**
```powershell
netstat -ano | findstr ":5173"
netstat -ano | findstr ":8000"
```

### ❌ Certificat SSL invalide

C'est **normal** avec un certificat auto-signé.

**Solutions :**
1. Acceptez l'avertissement sur chaque appareil (une seule fois)
2. Importez le certificat dans les appareils
3. Utilisez HTTP au lieu de HTTPS (moins sécurisé)

---

## 📊 Comparaison des solutions

| Solution | Difficulté | Portée | Automatique | Hors réseau |
|----------|------------|--------|-------------|-------------|
| **Tailscale MagicDNS** | Facile | Globale | ✅ | ✅ |
| **Fichier hosts** | Facile | Par appareil | ❌ | ❌ |
| **Routeur DNS** | Moyenne | Réseau local | ✅ | ❌ |
| **Serveur DNS** | Difficile | Réseau local | ✅ | ❌ |

---

## 🎯 Recommandation

**Pour la plupart des utilisateurs :**
→ Utilisez **Tailscale MagicDNS** (Solution 1)

**Pourquoi ?**
- Configuration simple
- Fonctionne partout (même hors de chez vous)
- Automatique sur tous les appareils
- Sécurisé et chiffré

**Commencez par :**
```powershell
.\setup-tailscale-dns.ps1
```

---

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez que le serveur fonctionne : `http://localhost:5173`
2. Vérifiez le firewall : `.\configure-network-access.ps1`
3. Testez avec l'IP directe : `http://192.168.x.x:5173`
4. Vérifiez les logs du serveur

---

**Fait avec ❤️ pour HomeOne**
