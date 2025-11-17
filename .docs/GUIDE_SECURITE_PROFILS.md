# 🔐 Guide de Sécurité des Profils

## Vue d'ensemble

Le système de profils Homeflix intègre une protection par mot de passe pour le profil principal, avec un système de récupération par question secrète.

---

## 🛡️ Fonctionnalités de sécurité

### Protection par mot de passe

- **Profil principal uniquement** : Seul le profil principal peut être protégé par mot de passe
- **Hachage SHA-256** : Les mots de passe sont stockés de manière sécurisée (jamais en clair)
- **Validation au démarrage** : Le mot de passe est demandé lors de la sélection du profil
- **Indicateur visuel** : Icône 🔒 affichée sur les profils protégés

### Récupération de mot de passe

- **Question secrète** : Configurée lors de la définition du mot de passe
- **Réinitialisation sécurisée** : Accès via "Mot de passe oublié"
- **Vérification de la réponse** : La réponse doit correspondre exactement

---

## 📖 Utilisation

### 1. Définir un mot de passe

**À l'installation :**
- Le profil principal est créé avec le mot de passe par défaut : `0`
- **Important** : Changez ce mot de passe dès la première utilisation !

**Pour changer le mot de passe :**

1. Sélectionnez le profil principal
2. Entrez le mot de passe actuel (par défaut : `0`)
3. Cliquez sur "Gérer les profils"
4. Cliquez sur "✏️ Modifier" à côté du profil principal
5. Remplissez les champs :
   - **Nouveau mot de passe** : Votre mot de passe sécurisé
   - **Question secrète** : Une question dont vous seul connaissez la réponse
   - **Réponse secrète** : La réponse exacte à votre question
6. Cliquez sur "Modifier"

### 2. Utiliser la protection

**Lors de la sélection du profil :**

```
1. Écran de sélection → Cliquez sur le profil principal (🔒)
2. Fenêtre de mot de passe → Saisissez votre mot de passe
3. Cliquez sur "Valider" → Accès accordé
```

**Accès refusé :**
- Message d'erreur affiché en rouge
- Le champ de saisie reste actif
- Vous pouvez réessayer ou annuler

### 3. Récupération en cas d'oubli

**Procédure de réinitialisation :**

1. Cliquez sur "Mot de passe oublié" sous le champ de saisie
2. Votre question secrète s'affiche
3. Saisissez la réponse exacte (sensible à la casse)
4. Entrez votre nouveau mot de passe
5. Cliquez sur "Réinitialiser"

**En cas d'échec :**
- Vérifiez l'exactitude de votre réponse (majuscules, espaces, accents)
- Si la réponse est incorrecte, le message d'erreur s'affiche
- Vous pouvez réessayer ou annuler

---

## 🔧 Configuration technique

### Base de données

**Table `profiles` :**
```sql
- password_hash TEXT        -- Hash SHA-256 du mot de passe
- security_question TEXT    -- Question de sécurité
- security_answer TEXT      -- Réponse hashée (SHA-256)
```

### API Endpoints

**Vérification du mot de passe :**
```http
POST /api/profiles/verify-password
Content-Type: application/json

{
  "profile_id": 1,
  "password": "votre_mot_de_passe"
}

→ { "ok": true } ou { "ok": false, "error": "Mot de passe incorrect" }
```

**Réinitialisation :**
```http
POST /api/profiles/reset-password
Content-Type: application/json

{
  "profile_id": 1,
  "security_answer": "votre_réponse",
  "new_password": "nouveau_mot_de_passe"
}

→ { "ok": true } ou { "ok": false, "error": "Réponse incorrecte" }
```

### Composants React

**PasswordPrompt.jsx :**
- Gère la saisie du mot de passe
- Interface de récupération
- Validation en temps réel

**ProfileSelector.jsx :**
- Détecte les profils protégés (`has_password`)
- Affiche l'icône 🔒
- Déclenche PasswordPrompt au clic

---

## 🛠️ Administration

### Script de migration

**migrate_profiles.py :**
```python
# Ajoute automatiquement les colonnes de sécurité
# Définit le mot de passe par défaut "0" pour le profil principal
# Compatible avec les installations existantes
```

**Exécution :**
```powershell
python server/migrate_profiles.py
```

### Mot de passe par défaut

**Profil principal :**
- Mot de passe : `0` (zéro)
- Aucune question/réponse définie
- **Action requise** : Changez immédiatement ce mot de passe !

### Réinitialisation manuelle

**Via SQLite :**
```sql
-- Réinitialiser au mot de passe par défaut "0"
UPDATE profiles 
SET password_hash = '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9',
    security_question = NULL,
    security_answer = NULL
WHERE is_main = 1;
```

---

## 🔒 Bonnes pratiques

### Sécurité du mot de passe

✅ **À FAIRE :**
- Choisir un mot de passe unique et mémorisable
- Définir une question secrète pertinente
- Changer le mot de passe par défaut immédiatement
- Éviter les mots de passe trop simples

❌ **À ÉVITER :**
- Utiliser le même mot de passe qu'ailleurs
- Laisser le mot de passe par défaut `0`
- Choisir une question trop évidente
- Partager votre mot de passe

### Question secrète

**Exemples de bonnes questions :**
- "Quelle est votre couleur préférée ?"
- "Quel est le nom de votre premier animal ?"
- "Dans quelle ville êtes-vous né(e) ?"
- "Quel est votre film préféré ?"

**Critères :**
- Réponse unique et personnelle
- Facile à retenir pour vous
- Difficile à deviner pour les autres
- Insensible aux variations (choisissez une orthographe fixe)

### Gestion multi-utilisateurs

**Profils secondaires :**
- Ne nécessitent pas de mot de passe
- Restrictions applicables (mode enfants, contenu adulte masqué)
- Accessibles depuis l'écran de sélection

**Organisation recommandée :**
```
Profil Principal (🔒)     → Administrateur (vous)
Profil Enfant             → Mode enfants activé
Profil Invité             → Contenu adulte masqué
```

---

## 🚨 Dépannage

### "Mot de passe incorrect"

**Causes possibles :**
- Majuscules/minuscules incorrectes
- Espaces en trop
- Mot de passe oublié

**Solutions :**
1. Vérifier la saisie (majuscules, espaces)
2. Utiliser "Mot de passe oublié"
3. En dernier recours : réinitialisation manuelle SQL

### "Réponse incorrecte" lors de la récupération

**Causes possibles :**
- Orthographe différente
- Majuscules/minuscules
- Caractères spéciaux ou accents

**Solutions :**
1. Réessayer avec différentes variantes
2. Vérifier les accents et la ponctuation
3. Réinitialisation manuelle si nécessaire

### Base de données corrompue

**Symptômes :**
- Erreur au démarrage
- Profil inaccessible
- Migration échouée

**Solution :**
```powershell
# Sauvegarder la base actuelle
Copy-Item server/homeflix.db server/homeflix.db.backup

# Relancer la migration
python server/migrate_profiles.py

# En cas d'échec : recréer la table
sqlite3 server/homeflix.db
DROP TABLE profiles;
.quit
python server/migrate_profiles.py
```

---

## 📊 Statistiques et logs

### Événements journalisés

**Backend (homeflix.log) :**
```
✓ Mot de passe vérifié avec succès - Profil #1
✗ Échec vérification mot de passe - Profil #1
✓ Mot de passe réinitialisé - Profil #1
✗ Réponse secrète incorrecte - Profil #1
```

### Monitoring

**Commandes utiles :**
```powershell
# Voir les 20 dernières lignes des logs
Get-Content server/homeflix.log -Tail 20

# Filtrer les événements de sécurité
Select-String -Path server/homeflix.log -Pattern "mot de passe|password"

# Vérifier l'état des profils
sqlite3 server/homeflix.db "SELECT id, name, is_main, password_hash IS NOT NULL as has_password FROM profiles;"
```

---

## 🔄 Migrations et mises à jour

### Version 1.1.0

**Nouveautés :**
- Ajout des colonnes `password_hash`, `security_question`, `security_answer`
- Mot de passe par défaut "0" pour le profil principal
- Composant PasswordPrompt
- API de vérification et réinitialisation

**Migration automatique :**
```powershell
# Exécutée automatiquement par start-homeflix.ps1
# Ou manuellement :
python server/migrate_profiles.py
```

### Compatibilité

✅ **Compatible avec :**
- Installations existantes (sans mot de passe)
- Profils créés avant la v1.1.0
- Bases de données Homeflix 1.0.x

---

## 📝 Notes de version

### v1.1.0 (2025-01-XX)

**Ajouté :**
- Protection par mot de passe du profil principal
- Système de récupération par question secrète
- Mot de passe par défaut "0"
- Indicateur visuel 🔒 sur les profils protégés
- Interface de gestion des profils séparée

**Modifié :**
- ProfileSelector : retrait des icônes de modification/suppression
- ProfileManager : vue liste + formulaire d'édition
- Schéma de base de données : 3 nouvelles colonnes

**Sécurité :**
- Hachage SHA-256 pour les mots de passe
- Hachage SHA-256 pour les réponses secrètes
- Pas de stockage en clair des données sensibles

---

## 📞 Support

**En cas de problème :**

1. Consultez ce guide (section Dépannage)
2. Vérifiez les logs : `server/homeflix.log`
3. Testez la migration : `python server/migrate_profiles.py`
4. Consultez le CHANGELOG.md pour les notes de version

**Fichiers de référence :**
- `GUIDE_PROFILS.md` : Gestion générale des profils
- `CHANGELOG.md` : Historique des modifications
- `README.md` : Documentation principale

---

**Dernière mise à jour :** 2025-01-XX  
**Version :** 1.1.0  
**Auteur :** Homeflix Team
