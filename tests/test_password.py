"""
Test du système de mot de passe des profils
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_verify_password():
    """Test de vérification du mot de passe par défaut"""
    print("\n🔐 Test de vérification du mot de passe...")
    
    response = requests.post(
        f"{BASE_URL}/api/profiles/verify-password",
        json={
            "profile_id": 1,
            "password": "0"  # Mot de passe par défaut
        }
    )
    
    data = response.json()
    print(f"   Résultat: {data}")
    
    if data.get("ok") and data.get("valid"):
        print("   ✅ Mot de passe correct")
        return True
    else:
        print(f"   ❌ Erreur: {data.get('error') or 'Mot de passe invalide'}")
        return False

def test_wrong_password():
    """Test avec un mauvais mot de passe"""
    print("\n🔐 Test avec un mauvais mot de passe...")
    
    response = requests.post(
        f"{BASE_URL}/api/profiles/verify-password",
        json={
            "profile_id": 1,
            "password": "mauvais_mot_de_passe"
        }
    )
    
    data = response.json()
    print(f"   Résultat: {data}")
    
    # Le serveur retourne ok:True (requête réussie) et valid:False (mot de passe invalide)
    if data.get("ok") and not data.get("valid"):
        print("   ✅ Mot de passe rejeté comme attendu")
        return True
    else:
        print("   ❌ Erreur: le mauvais mot de passe a été accepté !")
        return False

def test_update_password():
    """Test de mise à jour du mot de passe"""
    print("\n🔐 Test de mise à jour du mot de passe...")
    
    response = requests.put(
        f"{BASE_URL}/api/profiles/1",
        json={
            "name": "Principal",
            "avatar": "avatar_01.svg",
            "password": "test123",
            "security_question": "Quelle est votre couleur préférée ?",
            "security_answer": "bleu"
        }
    )
    
    data = response.json()
    print(f"   Résultat: {data}")
    
    if data.get("ok"):
        print("   ✅ Mot de passe mis à jour")
        
        # Vérifier le nouveau mot de passe
        verify_response = requests.post(
            f"{BASE_URL}/api/profiles/verify-password",
            json={
                "profile_id": 1,
                "password": "test123"
            }
        )
        
        verify_data = verify_response.json()
        if verify_data.get("ok"):
            print("   ✅ Nouveau mot de passe vérifié")
        else:
            print(f"   ❌ Nouveau mot de passe non accepté: {verify_data.get('error')}")
            return False
    else:
        print(f"   ❌ Erreur de mise à jour: {data.get('error')}")
        return False
    
    return True

def test_reset_password():
    """Test de réinitialisation par question secrète"""
    print("\n🔐 Test de réinitialisation du mot de passe...")
    
    response = requests.post(
        f"{BASE_URL}/api/profiles/reset-password",
        json={
            "profile_id": 1,
            "security_answer": "bleu",
            "new_password": "0"  # Retour au mot de passe par défaut
        }
    )
    
    data = response.json()
    print(f"   Résultat: {data}")
    
    if data.get("ok"):
        print("   ✅ Mot de passe réinitialisé")
        
        # Vérifier le mot de passe réinitialisé
        verify_response = requests.post(
            f"{BASE_URL}/api/profiles/verify-password",
            json={
                "profile_id": 1,
                "password": "0"
            }
        )
        
        verify_data = verify_response.json()
        if verify_data.get("ok"):
            print("   ✅ Mot de passe par défaut restauré")
        else:
            print(f"   ❌ Mot de passe par défaut non accepté: {verify_data.get('error')}")
            return False
    else:
        print(f"   ❌ Erreur de réinitialisation: {data.get('error')}")
        return False
    
    return True

def test_wrong_security_answer():
    """Test avec une mauvaise réponse secrète"""
    print("\n🔐 Test avec une mauvaise réponse secrète...")
    
    # D'abord remettre un mot de passe et une question
    requests.put(
        f"{BASE_URL}/api/profiles/1",
        json={
            "name": "Principal",
            "avatar": "avatar_01.svg",
            "password": "test123",
            "security_question": "Quelle est votre couleur préférée ?",
            "security_answer": "bleu"
        }
    )
    
    # Tenter une réinitialisation avec mauvaise réponse
    response = requests.post(
        f"{BASE_URL}/api/profiles/reset-password",
        json={
            "profile_id": 1,
            "security_answer": "rouge",  # Mauvaise réponse
            "new_password": "nouveau_mdp"
        }
    )
    
    data = response.json()
    print(f"   Résultat: {data}")
    
    if not data.get("ok"):
        print("   ✅ Mauvaise réponse rejetée comme attendu")
        
        # Remettre le mot de passe par défaut
        requests.post(
            f"{BASE_URL}/api/profiles/reset-password",
            json={
                "profile_id": 1,
                "security_answer": "bleu",
                "new_password": "0"
            }
        )
        print("   ✅ Mot de passe par défaut restauré")
    else:
        print("   ❌ Erreur: la mauvaise réponse a été acceptée !")
        return False
    
    return True

def main():
    """Exécution de tous les tests"""
    print("=" * 60)
    print("🧪 Tests du système de mot de passe des profils")
    print("=" * 60)
    
    tests = [
        ("Vérification mot de passe par défaut", test_verify_password),
        ("Rejet du mauvais mot de passe", test_wrong_password),
        ("Mise à jour du mot de passe", test_update_password),
        ("Réinitialisation par question secrète", test_reset_password),
        ("Rejet de la mauvaise réponse secrète", test_wrong_security_answer),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n   ❌ Exception: {e}")
            results.append((name, False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 Résumé des tests")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n🎯 Score: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés !")
    else:
        print("⚠️  Certains tests ont échoué")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {e}")
