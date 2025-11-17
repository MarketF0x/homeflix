# 🔑 Guide d'Obtention de la Clé API TMDb

## 📋 Pourquoi ai-je besoin d'une clé API TMDb ?

Homeflix utilise l'API The Movie Database (TMDb) pour :
- ✅ Récupérer les affiches de films et séries
- ✅ Obtenir les métadonnées (résumé, notes, acteurs, etc.)
- ✅ Enrichir votre bibliothèque vidéo automatiquement

**Important** : Chaque utilisateur doit obtenir sa propre clé API gratuite pour utiliser Homeflix.

---

## ⚠️ Note Importante sur l'Usage Commercial

D'après les conditions d'utilisation de TMDb :

### ✅ Usage NON-Commercial (GRATUIT)
- Application personnelle gratuite
- Pas de frais pour l'utilisateur
- Pas de publicité ni revenus
- **→ Clé API gratuite suffisante**

### ⚠️ Usage Commercial (PAYANT)
Si vous utilisez Homeflix dans un cadre commercial :
- Application payante
- Site web avec revenus (publicité, abonnements)
- Service commercial

**→ Vous devez contacter TMDb pour une licence commerciale** :
- Site : https://www.themoviedb.org/api-for-business
- Email : Via https://www.themoviedb.org/about/staying-in-touch

---

## 🚀 Procédure d'Obtention (Usage NON-Commercial)

### ⚡ Méthode Rapide (Recommandée)

**Utilisez le script automatisé** :
```powershell
.\setup-tmdb-key.ps1
```

Le script vous guidera et ouvrira directement : **https://www.themoviedb.org/settings/api**

### 📝 Méthode Manuelle

### Étape 1 : Créer un Compte TMDb (si nécessaire)

1. Aller sur : **https://www.themoviedb.org/settings/api**
2. Si vous n'êtes pas connecté, cliquez sur **"Sign Up"**
3. Remplir le formulaire d'inscription :
   - Nom d'utilisateur
   - Email valide
   - Mot de passe
4. Confirmer votre email (vérifier votre boîte de réception)
5. Se connecter à votre compte

### Étape 2 : Demander une Clé API

1. Sur la page **https://www.themoviedb.org/settings/api**

2. Cliquer sur **"Request an API Key"** (Demander une clé API)

3. Choisir le type : **Developer** (Développeur)

4. Accepter les conditions d'utilisation

### Étape 3 : Remplir le Formulaire

Vous devez fournir quelques informations :

**Type d'utilisation** : Sélectionner **"Personal"** (Personnel)

**Détails de l'application** :
```
Application Name: Homeflix Personal Server
Application Summary: Personal video streaming server for home use
Application URL: http://localhost:5173 (ou votre domaine personnel)
```

**Informations personnelles** :
- Votre nom complet
- Numéro de téléphone (optionnel mais recommandé)

### Étape 4 : Récupérer Votre Clé API

Une fois le formulaire validé (généralement instantané) :

1. Vous verrez deux clés :
   - **API Key (v3 auth)** ← **C'est celle-ci que vous devez copier**
   - API Read Access Token (v4 auth) ← Ne pas utiliser

2. **Copier la clé API (v3)** 
   - Format : 32 caractères hexadécimaux
   - Exemple : `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

---

## ⚙️ Configuration dans Homeflix

### Méthode 1 : Via le fichier `settings.yaml` (Recommandé)

1. Ouvrir le fichier `settings.yaml` à la racine du projet

2. Localiser la ligne :
   ```yaml
   tmdb_api_key: ''
   ```

3. Remplacer par votre clé :
   ```yaml
   tmdb_api_key: 'VOTRE_CLE_API_ICI'
   ```

4. Sauvegarder le fichier

5. Redémarrer Homeflix :
   ```powershell
   .\start-homeflix.ps1 -Mode production
   ```

### Méthode 2 : Via le fichier `.env`

1. Ouvrir le fichier `.env` à la racine du projet

2. Localiser la ligne :
   ```env
   TMDB_API_KEY=your_api_key_here
   ```

3. Remplacer par :
   ```env
   TMDB_API_KEY=VOTRE_CLE_API_ICI
   ```

4. Sauvegarder et redémarrer

**Note** : Le fichier `.env` a la priorité sur `settings.yaml`

---

## ✅ Vérification de la Configuration

### Test Automatique

Après avoir configuré votre clé, lancez le script de test :

```powershell
cd server
python -c "from core.config_manager import load_settings; settings = load_settings(); print('✅ Clé TMDb configurée!' if settings.tmdb_api_key else '❌ Clé TMDb manquante')"
```

### Test Manuel

1. Démarrer Homeflix
2. Ouvrir l'interface web
3. Vérifier qu'une vidéo affiche :
   - ✅ Une affiche/poster
   - ✅ Un résumé
   - ✅ Une note

Si vous voyez ces informations, la clé fonctionne ! 🎉

---

## 🔒 Sécurité de Votre Clé API

### ⚠️ IMPORTANT - Ne JAMAIS :

❌ **Partager votre clé publiquement**
❌ **Commiter votre clé dans Git** (elle est dans `.gitignore`)
❌ **Publier votre clé sur des forums/réseaux sociaux**
❌ **Donner votre clé à d'autres personnes**

### ✅ TOUJOURS :

✅ **Garder votre clé privée**
✅ **Utiliser le fichier `.env` ou `settings.yaml`**
✅ **Révoquer et régénérer si compromise**
✅ **Chaque utilisateur obtient sa propre clé**

### En cas de Compromission

Si votre clé a été exposée :

1. Aller sur : https://www.themoviedb.org/settings/api
2. Cliquer sur **"Reset API Key"**
3. Confirmer la régénération
4. Mettre à jour votre configuration avec la nouvelle clé

---

## 📊 Limites de l'API Gratuite

L'API TMDb gratuite a des limites de requêtes :

- **40 requêtes par 10 secondes**
- **Pas de limite quotidienne**

Homeflix respecte automatiquement ces limites avec :
- Cache local des métadonnées
- Temporisation entre les requêtes
- Stockage en base de données

**→ Usage normal : Aucun problème** ✅

---

## 🆘 Problèmes Fréquents

### ❌ "API Key Invalid"

**Causes** :
- Clé mal copiée (espaces, caractères manquants)
- Clé pas encore activée (attendre 5-10 minutes)
- Mauvaise clé utilisée (v4 au lieu de v3)

**Solutions** :
1. Re-copier la clé API (v3 auth)
2. Vérifier qu'il n'y a pas d'espaces avant/après
3. Attendre quelques minutes après la création
4. Retourner sur https://www.themoviedb.org/settings/api

### ❌ "Too Many Requests"

**Cause** : Trop de requêtes simultanées

**Solution** : 
- Patienter 10 secondes
- Homeflix gère cela automatiquement normalement

### ❌ Affiches ne s'affichent pas

**Causes** :
- Clé API manquante ou invalide
- Connexion internet coupée
- Nom de fichier mal formaté

**Solutions** :
1. Vérifier la clé API dans `settings.yaml`
2. Tester la connexion internet
3. Nettoyer les noms de fichiers : `.\clean_filenames.py`

---

## 📚 Ressources Officielles

- **Inscription TMDb** : https://www.themoviedb.org/signup
- **Paramètres API** : https://www.themoviedb.org/settings/api
- **Documentation API** : https://developer.themoviedb.org/docs
- **Conditions d'utilisation** : https://www.themoviedb.org/api-terms-of-use
- **Support TMDb** : https://www.themoviedb.org/talk

---

## 🎯 Résumé Rapide

### Pour Commencer (5 minutes)

1. **Créer un compte** → https://www.themoviedb.org/signup
2. **Confirmer l'email**
3. **Demander une clé API** → https://www.themoviedb.org/settings/api
4. **Choisir "Developer" + "Personal"**
5. **Copier la clé API (v3)**
6. **Coller dans `settings.yaml`** :
   ```yaml
   tmdb_api_key: 'VOTRE_CLE_ICI'
   ```
7. **Redémarrer Homeflix**
8. **Profiter ! 🎬**

---

## 💡 Conseils

- ✅ **Gratuit à vie** pour usage personnel
- ✅ **Activation instantanée** (parfois 5-10 min)
- ✅ **Illimité** pour usage raisonnable
- ✅ **Très stable** et fiable
- ✅ **Excellente base de données** de films/séries

---

## 📞 Besoin d'Aide ?

Si vous rencontrez des problèmes :

1. **Relire ce guide** attentivement
2. **Vérifier les problèmes fréquents** ci-dessus
3. **Consulter** `TMDB_TERMS_SUMMARY.md` pour les conditions
4. **Support TMDb** : https://www.themoviedb.org/talk

---

*Guide créé pour Homeflix - Dernière mise à jour : Novembre 2025*
