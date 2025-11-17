# 🚀 Guide de sauvegarde GitHub - Homeflix

## ✅ Votre code est déjà préparé et commité !

Le commit a été créé avec succès :
- **Message** : "Sauvegarde version stable - Nov 2025 - Carousel CSS fixé + optimisations"
- **Branche** : dev
- **Fichiers** : Tous vos fichiers sont prêts à être poussés

---

## 📋 ÉTAPES SIMPLES (5 minutes)

### 1️⃣ Créer le dépôt GitHub (1 min)

1. Ouvrez https://github.com/new dans votre navigateur
2. **Nom du repository** : `homeflix`
3. ✅ **Cochez "Private"** (important pour la confidentialité !)
4. ❌ **Laissez tout le reste décoché** (pas de README, pas de .gitignore)
5. Cliquez sur **"Create repository"**

### 2️⃣ Créer un Token d'accès (2 min)

1. Allez sur https://github.com/settings/tokens
2. Cliquez sur **"Generate new token"** → **"Generate new token (classic)"**
3. Donnez un nom : `Homeflix-Backup`
4. Cochez uniquement : ☑️ **`repo`** (Full control of private repositories)
5. Cliquez sur **"Generate token"**
6. ⚠️ **COPIEZ LE TOKEN** (vous ne pourrez plus le voir après !)

### 3️⃣ Connecter et pousser (2 min)

Ouvrez PowerShell dans `C:\Users\fparo\Desktop\homeflix` et exécutez :

```powershell
# Remplacez VOTRE_USERNAME par votre nom d'utilisateur GitHub
git remote add origin https://github.com/VOTRE_USERNAME/homeflix.git

# Pousser votre code
git push -u origin dev
```

**Quand on vous demande :**
- **Username** : Votre nom d'utilisateur GitHub
- **Password** : Collez le TOKEN que vous avez copié (pas votre mot de passe !)

---

## 🎉 C'est terminé !

Votre code sera sauvegardé sur GitHub en privé. Vous pourrez :
- ✅ Accéder à votre code de n'importe où
- ✅ Voir l'historique des modifications
- ✅ Revenir à des versions antérieures
- ✅ Collaborer si besoin

---

## ❓ Problèmes courants

### "remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/VOTRE_USERNAME/homeflix.git
```

### "Authentication failed"
- Vérifiez que vous utilisez le TOKEN (pas le mot de passe)
- Recréez un nouveau token si nécessaire

### "rejected - non-fast-forward"
```powershell
git push -u origin dev --force
```

---

**Besoin d'aide ? Dites-moi quel message d'erreur vous voyez !**
