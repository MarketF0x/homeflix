# 🌐 Partage Homeflix sur le Réseau WiFi Local

## ✅ Configuration terminée !

Homeflix est maintenant configuré pour être accessible depuis tous les appareils connectés sur votre réseau WiFi local (PC, Mac, smartphones, tablettes).

---

## 📋 Comment utiliser Homeflix sur le réseau

### 1️⃣ **Démarrer Homeflix sur votre PC principal**

Sur l'ordinateur qui contient vos vidéos (votre PC actuel), lancez Homeflix normalement :

```powershell
.\start-dev.ps1
```

ou double-cliquez sur `start.bat`

### 2️⃣ **Trouver l'adresse IP de votre PC**

Ouvrez PowerShell et tapez :

```powershell
ipconfig
```

Cherchez la ligne **"Adresse IPv4"** sous votre carte WiFi. Elle ressemble à :
- `192.168.1.45` (réseau classique)
- `192.168.0.123` (selon votre routeur)
- `10.0.0.15` (certains réseaux)

**Exemple :**
```
Carte réseau sans fil Wi-Fi :
   Adresse IPv4. . . . . . . . : 192.168.1.45
```

➡️ **Notez cette adresse IP !**

### 3️⃣ **Se connecter depuis un autre appareil**

Sur n'importe quel appareil connecté au **même réseau WiFi** :

#### 🖥️ **Depuis un PC/Mac :**
Ouvrez un navigateur web (Chrome, Firefox, Safari, Edge) et allez à :

```
http://[VOTRE-IP]:5173
```

**Exemple concret :**
```
http://192.168.1.45:5173
```

#### 📱 **Depuis un smartphone/tablette :**
Même chose ! Ouvrez le navigateur et tapez l'adresse ci-dessus.

---

## 🎯 Exemples d'utilisation

### Scénario 1 : Regarder sur votre Mac
1. Votre PC Windows (IP: 192.168.1.45) exécute Homeflix
2. Sur votre Mac, ouvrez Safari
3. Allez sur `http://192.168.1.45:5173`
4. ✅ Vous voyez toute votre bibliothèque de films !

### Scénario 2 : Regarder sur votre smartphone
1. Votre PC exécute Homeflix
2. Votre smartphone est connecté au même WiFi
3. Ouvrez Chrome/Safari sur le téléphone
4. Tapez `http://192.168.1.45:5173`
5. ✅ Vous pouvez naviguer et lire les vidéos !

---

## 🔥 Configuration du Pare-feu Windows (IMPORTANT)

La première fois, Windows va vous demander d'autoriser l'accès réseau. **Cliquez sur "Autoriser l'accès"**.

Si vous avez des problèmes de connexion, autorisez manuellement les ports :

### Méthode rapide (PowerShell en Administrateur) :

```powershell
# Autoriser le port 5173 (client Vite)
New-NetFirewallRule -DisplayName "Homeflix Client" -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow

# Autoriser le port 8000 (serveur FastAPI)
New-NetFirewallRule -DisplayName "Homeflix Server" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

### Méthode manuelle (interface graphique) :

1. Ouvrez **Pare-feu Windows Defender**
2. Cliquez sur **Paramètres avancés**
3. **Règles de trafic entrant** → **Nouvelle règle**
4. Choisissez **Port** → Suivant
5. **TCP** → Ports spécifiques : `5173, 8000`
6. **Autoriser la connexion** → Suivant
7. Cochez **Domaine, Privé, Public** → Suivant
8. Nom : `Homeflix` → Terminer

---

## ⚠️ Points importants

### ✅ Ce qui fonctionne :
- **Navigation** : parcourir tous vos films/séries depuis n'importe quel appareil
- **Lecture vidéo** : regarder les vidéos en streaming
- **Interface complète** : toutes les fonctionnalités (recherche, filtres, etc.)

### ⚠️ À savoir :
- **Le PC principal doit rester allumé** : c'est lui qui héberge les vidéos et le serveur
- **Même réseau WiFi obligatoire** : tous les appareils doivent être sur le même réseau
- **Performance** : dépend de votre WiFi (un bon WiFi 5 GHz est recommandé pour la HD)
- **Sécurité** : Homeflix est accessible **uniquement** sur votre réseau local (pas sur Internet)

### 🚫 Ce qui ne marche PAS :
- Accès depuis l'extérieur de votre domicile (Internet)
- Connexion si le PC principal est éteint
- Connexion depuis un autre réseau WiFi

---

## 🔧 Dépannage

### ❌ "Impossible de se connecter"

1. **Vérifiez que Homeflix est démarré** sur le PC principal
2. **Vérifiez l'IP** : elle peut changer (refaites `ipconfig`)
3. **Pare-feu** : autorisez les ports 5173 et 8000
4. **Même réseau** : vérifiez que les deux appareils sont sur le même WiFi

### ❌ "La page charge mais les vidéos ne s'affichent pas"

1. Vérifiez le port 8000 aussi : `http://[VOTRE-IP]:8000`
2. Autorisez le port 8000 dans le pare-feu

### 🔄 Trouver votre IP rapidement

Créez un raccourci avec cette commande :

```powershell
ipconfig | findstr /i "IPv4"
```

---

## 📊 Architecture réseau

```
┌─────────────────────────────────────────┐
│         Réseau WiFi Local               │
│         (192.168.1.x)                   │
├─────────────────────────────────────────┤
│                                         │
│  🖥️ PC Principal (192.168.1.45)        │
│     ├─ Serveur FastAPI :8000           │
│     ├─ Client Vite :5173               │
│     └─ Fichiers vidéos (C:, D:, etc.)  │
│                                         │
│  💻 Mac (192.168.1.78)                 │
│     └─ Navigateur → http://192.168.1.45:5173
│                                         │
│  📱 iPhone (192.168.1.102)             │
│     └─ Safari → http://192.168.1.45:5173
│                                         │
│  🖥️ PC Portable (192.168.1.56)         │
│     └─ Chrome → http://192.168.1.45:5173
│                                         │
└─────────────────────────────────────────┘
```

---

## 🎬 Profitez de vos films partout chez vous !

Vous pouvez maintenant :
- Regarder un film sur votre Mac pendant que le PC est au bureau
- Lancer une série sur votre tablette dans le salon
- Parcourir votre bibliothèque depuis votre smartphone dans le canapé
- Partager l'accès avec votre famille sur le même réseau

**Bon visionnage ! 🍿**
