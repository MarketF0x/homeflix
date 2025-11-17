"""
Test complet du nouveau système de mot de passe
La réponse à la question secrète devient le mot de passe
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def print_separator(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_1_get_profiles():
    """Test 1: Récupérer la liste des profils"""
    print_separator("TEST 1: Récupération des profils")
    
    response = requests.get(f"{BASE_URL}/api/profiles")
    data = response.json()
    
    print(f"✅ {len(data['profiles'])} profil(s) trouvé(s)")
    
    for profile in data['profiles']:
        print(f"\n  📋 Profil: {profile['name']}")
        print(f"     - ID: {profile['id']}")
        print(f"     - Principal: {profile['is_main']}")
        print(f"     - Protégé: {'🔒 Oui' if profile.get('has_password') else '⭕ Non'}")
    
    return data['profiles'][0] if data['profiles'] else None

def test_2_get_security_question(profile_id):
    """Test 2: Récupérer la question secrète"""
    print_separator("TEST 2: Récupération de la question secrète")
    
    response = requests.get(f"{BASE_URL}/api/profiles/{profile_id}/security-question")
    data = response.json()
    
    if data.get('ok'):
        question = data.get('question')
        if question:
            print(f"✅ Question secrète: {question}")
        else:
            print("⚠️  Aucune question secrète définie")
        return question
    else:
        print(f"❌ Erreur: {data}")
        return None

def test_3_update_password_with_question(profile_id, old_password=None):
    """Test 3: Définir/Modifier le mot de passe via question secrète"""
    print_separator("TEST 3: Définition du mot de passe via question secrète")
    
    # Question et réponse de test
    question = "Quelle est votre couleur préférée ?"
    answer = "bleu"
    
    print(f"\n📝 Question choisie: {question}")
    print(f"📝 Réponse (qui devient le mot de passe): {answer}")
    
    body = {
        "name": "Principal",
        "avatar": "avatar_01.svg",
        "security_question": question,
        "security_answer": answer
    }
    
    if old_password:
        print(f"🔑 Ancien mot de passe fourni: {old_password}")
        body["old_password"] = old_password
    
    response = requests.put(
        f"{BASE_URL}/api/profiles/{profile_id}",
        json=body
    )
    
    data = response.json()
    
    if data.get('ok'):
        print(f"\n✅ Mot de passe défini avec succès!")
        print(f"💡 Le mot de passe est maintenant: '{answer}'")
        return answer
    else:
        print(f"\n❌ Erreur: {data.get('error') or data.get('detail')}")
        return None

def test_4_verify_password(profile_id, password):
    """Test 4: Vérifier le mot de passe"""
    print_separator("TEST 4: Vérification du mot de passe")
    
    print(f"\n🔐 Test du mot de passe: '{password}'")
    
    response = requests.post(
        f"{BASE_URL}/api/profiles/verify-password",
        json={
            "profile_id": profile_id,
            "password": password
        }
    )
    
    data = response.json()
    
    if data.get('ok') and data.get('valid'):
        print(f"✅ Mot de passe VALIDE")
        return True
    elif data.get('ok') and not data.get('valid'):
        print(f"❌ Mot de passe INVALIDE")
        return False
    else:
        print(f"❌ Erreur: {data}")
        return False

def test_5_verify_wrong_password(profile_id):
    """Test 5: Vérifier qu'un mauvais mot de passe est rejeté"""
    print_separator("TEST 5: Test avec mauvais mot de passe")
    
    wrong_password = "mauvais_mot_de_passe"
    print(f"\n🔐 Test du mot de passe: '{wrong_password}'")
    
    response = requests.post(
        f"{BASE_URL}/api/profiles/verify-password",
        json={
            "profile_id": profile_id,
            "password": wrong_password
        }
    )
    
    data = response.json()
    
    if data.get('ok') and not data.get('valid'):
        print(f"✅ Mauvais mot de passe correctement rejeté")
        return True
    else:
        print(f"❌ PROBLÈME: Le mauvais mot de passe a été accepté!")
        return False

def test_6_reset_password(profile_id):
    """Test 6: Réinitialisation via question secrète"""
    print_separator("TEST 6: Réinitialisation du mot de passe")
    
    new_answer = "rouge"
    
    print(f"\n🔄 Nouvelle réponse (nouveau mot de passe): '{new_answer}'")
    print(f"⚠️  On ne connaît pas l'ancien mot de passe, on utilise la réinitialisation")
    
    response = requests.post(
        f"{BASE_URL}/api/profiles/reset-password",
        json={
            "profile_id": profile_id,
            "security_answer": new_answer
        }
    )
    
    data = response.json()
    
    if data.get('ok'):
        print(f"✅ Mot de passe réinitialisé avec succès!")
        print(f"💡 Le nouveau mot de passe est: '{new_answer}'")
        return new_answer
    else:
        print(f"❌ Erreur: {data.get('message')}")
        return None

def test_7_verify_new_password(profile_id, new_password):
    """Test 7: Vérifier le nouveau mot de passe après réinitialisation"""
    print_separator("TEST 7: Vérification du nouveau mot de passe")
    
    print(f"\n🔐 Test du nouveau mot de passe: '{new_password}'")
    
    response = requests.post(
        f"{BASE_URL}/api/profiles/verify-password",
        json={
            "profile_id": profile_id,
            "password": new_password
        }
    )
    
    data = response.json()
    
    if data.get('ok') and data.get('valid'):
        print(f"✅ Nouveau mot de passe VALIDE")
        return True
    else:
        print(f"❌ Nouveau mot de passe INVALIDE")
        return False

def test_8_change_password_with_old(profile_id, old_password):
    """Test 8: Changer le mot de passe en fournissant l'ancien"""
    print_separator("TEST 8: Changement avec ancien mot de passe")
    
    new_question = "Quel est le nom de votre premier animal de compagnie ?"
    new_answer = "rex"
    
    print(f"\n🔑 Ancien mot de passe: '{old_password}'")
    print(f"📝 Nouvelle question: {new_question}")
    print(f"📝 Nouvelle réponse (nouveau mot de passe): '{new_answer}'")
    
    response = requests.put(
        f"{BASE_URL}/api/profiles/{profile_id}",
        json={
            "name": "Principal",
            "avatar": "avatar_01.svg",
            "old_password": old_password,
            "security_question": new_question,
            "security_answer": new_answer
        }
    )
    
    data = response.json()
    
    if data.get('ok'):
        print(f"✅ Mot de passe changé avec succès!")
        print(f"💡 Le nouveau mot de passe est: '{new_answer}'")
        return new_answer
    else:
        print(f"❌ Erreur: {data.get('error') or data.get('detail')}")
        return None

def test_9_verify_final_password(profile_id, final_password):
    """Test 9: Vérification finale"""
    print_separator("TEST 9: Vérification finale")
    
    print(f"\n🔐 Test du mot de passe final: '{final_password}'")
    
    response = requests.post(
        f"{BASE_URL}/api/profiles/verify-password",
        json={
            "profile_id": profile_id,
            "password": final_password
        }
    )
    
    data = response.json()
    
    if data.get('ok') and data.get('valid'):
        print(f"✅ Mot de passe final VALIDE")
        return True
    else:
        print(f"❌ Mot de passe final INVALIDE")
        return False

def test_10_reset_to_default(profile_id):
    """Test 10: Remettre le mot de passe par défaut"""
    print_separator("TEST 10: Remise à zéro (mot de passe '0')")
    
    default_question = "Quelle est votre couleur préférée ?"
    default_answer = "0"
    
    print(f"\n🔄 Remise du mot de passe par défaut: '{default_answer}'")
    
    response = requests.post(
        f"{BASE_URL}/api/profiles/reset-password",
        json={
            "profile_id": profile_id,
            "security_answer": default_answer
        }
    )
    
    data = response.json()
    
    if data.get('ok'):
        print(f"✅ Mot de passe réinitialisé à '0'")
        
        # Mettre à jour la question aussi
        requests.put(
            f"{BASE_URL}/api/profiles/{profile_id}",
            json={
                "name": "Principal",
                "avatar": "avatar_01.svg",
                "old_password": default_answer,
                "security_question": default_question,
                "security_answer": default_answer
            }
        )
        
        return True
    else:
        print(f"❌ Erreur: {data.get('message')}")
        return False

def main():
    """Exécution de tous les tests"""
    print("\n" + "🚀" * 35)
    print("  TEST COMPLET DU SYSTÈME DE MOT DE PASSE")
    print("  (La réponse à la question secrète devient le mot de passe)")
    print("🚀" * 35)
    
    results = []
    
    try:
        # Test 1: Récupérer les profils
        profile = test_1_get_profiles()
        if not profile:
            print("\n❌ Aucun profil trouvé!")
            return
        
        profile_id = profile['id']
        
        # Test 2: Récupérer la question secrète
        question = test_2_get_security_question(profile_id)
        results.append(("Récupération question secrète", question is not None or not profile.get('has_password')))
        
        # Test 3: Définir le mot de passe
        # Si le profil a déjà un mot de passe, on utilise le mot de passe actuel
        old_pwd = "cc" if profile.get('has_password') else None
        password1 = test_3_update_password_with_question(profile_id, old_pwd)
        results.append(("Définition mot de passe via question", password1 is not None))
        
        if not password1:
            print("\n⚠️  Impossible de continuer les tests")
            return
        
        # Test 4: Vérifier le mot de passe
        valid = test_4_verify_password(profile_id, password1)
        results.append(("Vérification mot de passe correct", valid))
        
        # Test 5: Vérifier qu'un mauvais mot de passe est rejeté
        rejected = test_5_verify_wrong_password(profile_id)
        results.append(("Rejet mauvais mot de passe", rejected))
        
        # Test 6: Réinitialisation via question secrète
        password2 = test_6_reset_password(profile_id)
        results.append(("Réinitialisation via question", password2 is not None))
        
        if password2:
            # Test 7: Vérifier le nouveau mot de passe
            valid = test_7_verify_new_password(profile_id, password2)
            results.append(("Vérification nouveau mot de passe", valid))
            
            # Test 8: Changer avec ancien mot de passe
            password3 = test_8_change_password_with_old(profile_id, password2)
            results.append(("Changement avec ancien mot de passe", password3 is not None))
            
            if password3:
                # Test 9: Vérification finale
                valid = test_9_verify_final_password(profile_id, password3)
                results.append(("Vérification finale", valid))
        
        # Test 10: Remise à zéro
        reset = test_10_reset_to_default(profile_id)
        results.append(("Remise à zéro", reset))
        
    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
    
    # Résumé final
    print("\n" + "=" * 70)
    print("  📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "-" * 70)
    print(f"🎯 Score: {passed}/{total} tests réussis ({percentage:.1f}%)")
    print("-" * 70)
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✅ Le système de mot de passe fonctionne correctement")
    else:
        print(f"\n⚠️  {total - passed} test(s) ont échoué")
        print("❌ Vérifiez les erreurs ci-dessus")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
