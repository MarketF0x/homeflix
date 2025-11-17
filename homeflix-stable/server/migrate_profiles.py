"""
Migration pour créer la table profiles
"""
import sqlite3
import os
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "homeflix.db")

def hash_password(password):
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def migrate():
    """Crée la table profiles et ajoute le profil principal par défaut"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Vérifier si la table existe déjà
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='profiles'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # Vérifier si les colonnes de mot de passe existent
            cursor.execute("PRAGMA table_info(profiles)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'password_hash' not in columns:
                print("⚙️  Ajout des colonnes de sécurité...")
                cursor.execute("ALTER TABLE profiles ADD COLUMN password_hash TEXT")
                cursor.execute("ALTER TABLE profiles ADD COLUMN security_question TEXT")
                cursor.execute("ALTER TABLE profiles ADD COLUMN security_answer TEXT")
                
                # Définir mot de passe par défaut "0" pour le profil principal existant
                default_password_hash = hash_password("0")
                cursor.execute("""
                    UPDATE profiles 
                    SET password_hash = ?, 
                        security_question = 'Quel est votre mot de passe par défaut ?',
                        security_answer = '0'
                    WHERE is_main = 1
                """, (default_password_hash,))
                print("✓ Colonnes de sécurité ajoutées - mot de passe par défaut: 0")
        else:
            # Créer la table profiles complète
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    avatar TEXT NOT NULL,
                    is_main INTEGER DEFAULT 0,
                    restrictions TEXT DEFAULT '{}',
                    password_hash TEXT,
                    security_question TEXT,
                    security_answer TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✓ Table profiles créée")
        
        # Vérifier si le profil principal existe déjà
        cursor.execute("SELECT COUNT(*) FROM profiles WHERE is_main = 1")
        main_profile_exists = cursor.fetchone()[0] > 0
        
        if not main_profile_exists:
            # Créer le profil principal par défaut avec mot de passe "0"
            default_password_hash = hash_password("0")
            cursor.execute("""
                INSERT INTO profiles (name, avatar, is_main, restrictions, password_hash, security_question, security_answer)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "Principal", 
                "avatar_01.svg", 
                1, 
                "{}",
                default_password_hash,
                "Quel est votre mot de passe par défaut ?",
                "0"
            ))
            print("✓ Profil principal créé (mot de passe par défaut: 0)")
        else:
            print("✓ Profil principal déjà existant")
        
        conn.commit()
        print("✓ Migration des profils terminée")
        
    except Exception as e:
        print(f"✗ Erreur lors de la migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
