# 🌍 Accès à Homeflix depuis Internet

## ⚠️ AVERTISSEMENTS DE SÉCURITÉ

**ATTENTION :** Exposer votre serveur Homeflix sur Internet comporte des risques :
- Vos vidéos seront accessibles depuis n'importe où dans le monde
- Risque de consommation excessive de bande passante
- Risque de sécurité si mal configuré
- Possible violation de votre contrat avec votre FAI

**RECOMMANDÉ :** Utilisez plutôt un VPN pour accéder à votre réseau local depuis l'extérieur.

---

## 📋 Prérequis

1. ✅ Pare-feu Windows configuré (ports 5173 et 8000 ouverts)
2. ✅ Serveurs Homeflix fonctionnels
3. 🔑 Accès administrateur à votre box/routeur
4. 🌐 Une adresse IP publique (fournie par votre FAI)

---

## 🔧 Étape 1 : Trouver votre IP publique

Votre IP publique est l'adresse que le monde extérieur voit. Pour la trouver :

### Option A : Via un site web
1. Allez sur : https://www.whatismyip.com/
2. Notez l'adresse IPv4 affichée (ex: `203.0.113.45`)

### Option B : Via PowerShell
```powershell
(Invoke-WebRequest -Uri "https://api.ipify.org").Content
```

⚠️ **Note :** Cette IP peut changer à chaque redémarrage de votre box (IP dynamique).

---

## 🔀 Étape 2 : Configuration du Port Forwarding

Le port forwarding redirige le trafic Internet vers votre PC local.

### Sur votre Box/Routeur :

1. **Accéder à l'interface de votre box**
   - Box Orange : http://192.168.1.1
   - Freebox : http://mafreebox.freebox.fr
   - SFR Box : http://192.168.1.1
   - Bouygues : http://192.168.1.254

2. **Se connecter** (login/mot de passe généralement indiqué au dos de la box)

3. **Trouver la section "NAT" ou "Redirection de ports"**
   - Orange : "NAT/PAT" ou "Serveurs de jeux"
   - Free : "Paramètres de la Freebox" > "Mode avancé" > "Redirections de ports"
   - SFR : "Réseau" > "NAT/PAT"
   - Bouygues : "Configuration avancée" > "NAT"

4. **Créer 2 redirections de ports :**

   **Redirection 1 : Client Vite**
   - Nom : Homeflix Client
   - Port externe : 5173
   - Port interne : 5173
   - Protocole : TCP
   - IP locale : `192.168.1.5` (l'IP de votre PC)
   
   **Redirection 2 : Serveur API**
   - Nom : Homeflix API
   - Port externe : 8000
   - Port interne : 8000
   - Protocole : TCP
   - IP locale : `192.168.1.5` (l'IP de votre PC)

5. **Enregistrer/Valider** les modifications

---

## 🔒 Étape 3 (Optionnel) : IP Dynamique → DNS Dynamique

Si votre IP publique change régulièrement, utilisez un service de DNS dynamique gratuit :

### Services gratuits recommandés :
- **DuckDNS** (simple, gratuit) : https://www.duckdns.org/
- **No-IP** : https://www.noip.com/
- **Dynu** : https://www.dynu.com/

### Configuration avec DuckDNS (exemple) :

1. Créez un compte sur https://www.duckdns.org/
2. Créez un sous-domaine (ex: `monhomeflix.duckdns.org`)
3. Notez votre token d'authentification
4. Sur votre PC, créez un script pour mettre à jour l'IP automatiquement

**Script PowerShell (à exécuter au démarrage) :**

```powershell
# update-duckdns.ps1
$domain = "monhomeflix"  # Votre sous-domaine
$token = "VOTRE-TOKEN-ICI"

while ($true) {
    Invoke-WebRequest -Uri "https://www.duckdns.org/update?domains=$domain&token=$token&ip="
    Start-Sleep -Seconds 300  # Met à jour toutes les 5 minutes
}
```

**Ajouter au démarrage Windows :**
1. Appuyez sur `Win + R`
2. Tapez `shell:startup`
3. Créez un raccourci vers ce script

---

## 🌐 Étape 4 : Accès depuis Internet

Une fois le port forwarding configuré :

### Avec IP publique directe :
```
http://VOTRE-IP-PUBLIQUE:5173
```
Exemple : `http://203.0.113.45:5173`

### Avec DNS dynamique :
```
http://monhomeflix.duckdns.org:5173
```

---

## 🔐 SÉCURITÉ : Ajouter une authentification (TRÈS RECOMMANDÉ)

Par défaut, Homeflix n'a pas d'authentification. **Tout le monde avec l'URL peut accéder à vos vidéos.**

### Option 1 : VPN (RECOMMANDÉ)
- Installez un serveur VPN sur votre réseau (WireGuard, OpenVPN)
- Connectez-vous au VPN avant d'accéder à Homeflix
- Plus sécurisé que l'exposition directe

### Option 2 : Reverse Proxy avec authentification
- Installez nginx ou Caddy
- Ajoutez une authentification basique
- SSL/TLS obligatoire pour sécuriser les connexions

---

## 📊 Vérification

### Test depuis Internet :
1. Désactivez le WiFi sur votre téléphone
2. Utilisez les données mobiles (4G/5G)
3. Accédez à `http://VOTRE-IP:5173`
4. Vous devriez voir Homeflix

### Dépannage :

**❌ "Site inaccessible"**
- Vérifiez que le port forwarding est actif
- Vérifiez que les serveurs Homeflix sont démarrés
- Vérifiez votre IP publique (elle a peut-être changé)

**❌ "ERR_CONNECTION_REFUSED"**
- Pare-feu Windows bloque encore → relancez `configure-firewall.ps1`
- Mauvaise IP locale configurée dans le port forwarding

**❌ "ERR_CONNECTION_TIMED_OUT"**
- Votre FAI bloque peut-être les ports 5173/8000
- Essayez d'autres ports (ex: 8080, 8443)

---

## ⚡ Alternatives plus simples

### 1. **Cloudflare Tunnel** (GRATUIT, plus sûr)
- Pas besoin de port forwarding
- Tunnel sécurisé automatique
- Documentation : https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/

### 2. **Tailscale** (VPN mesh, GRATUIT)
- Crée un réseau privé virtuel
- Zéro configuration
- Plus sécurisé qu'exposition directe
- Site : https://tailscale.com/

### 3. **ngrok** (Tunnel temporaire)
- Parfait pour tests rapides
- Gratuit avec limitations
- Site : https://ngrok.com/

---

## 📝 Résumé

✅ **Méthode simple mais risquée :** Port forwarding direct  
✅ **Méthode recommandée :** VPN (WireGuard/Tailscale)  
✅ **Méthode moderne :** Cloudflare Tunnel  

**Choix recommandé pour votre cas :** 
👉 **Tailscale** - Installation en 5 minutes, gratuit, ultra sécurisé, pas de configuration réseau complexe.

---

## 🆘 Besoin d'aide ?

Si vous choisissez Tailscale ou Cloudflare Tunnel, demandez-moi et je vous fournirai un guide détaillé !
