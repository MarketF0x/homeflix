"""
Migration: Gestion de la reprise de lecture par profil

Cette migration crée une nouvelle table `watch_progress` pour stocker
la position de lecture de chaque vidéo pour chaque profil utilisateur.

Ancien système: last_position dans la table videos (global)
Nouveau système: table watch_progress avec (profile_id, video_id, position)
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "homeflix.db"


def migrate():
    """Migre le système de reprise vers un modèle par profil"""
    print("🔄 Migration: Reprise de lecture par profil")
    print("=" * 60)
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # 1. Vérifier si la table watch_progress existe déjà
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='watch_progress'
    """)
    
    if cursor.fetchone():
        print("✅ Table 'watch_progress' existe déjà")
        conn.close()
        return
    
    # 2. Créer la nouvelle table watch_progress
    print("\n📦 Création de la table 'watch_progress'...")
    cursor.execute("""
        CREATE TABLE watch_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            video_id INTEGER NOT NULL,
            position INTEGER NOT NULL DEFAULT 0,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profile_id) REFERENCES profiles (id) ON DELETE CASCADE,
            FOREIGN KEY (video_id) REFERENCES videos (id) ON DELETE CASCADE,
            UNIQUE(profile_id, video_id)
        )
    """)
    print("   ✓ Table créée")
    
    # 3. Créer les index pour optimiser les requêtes
    print("\n📊 Création des index...")
    cursor.execute("""
        CREATE INDEX idx_watch_progress_profile 
        ON watch_progress(profile_id)
    """)
    cursor.execute("""
        CREATE INDEX idx_watch_progress_video 
        ON watch_progress(video_id)
    """)
    cursor.execute("""
        CREATE INDEX idx_watch_progress_updated 
        ON watch_progress(updated_at DESC)
    """)
    print("   ✓ Index créés")
    
    # 4. Migrer les données existantes vers le profil principal
    print("\n🔄 Migration des données existantes...")
    
    # Vérifier si la table videos existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='videos'
    """)
    
    has_videos_table = cursor.fetchone() is not None
    
    if not has_videos_table:
        print("   ℹ️  Table 'videos' non trouvée")
        print("   → Système sans cache vidéo - aucune donnée à migrer")
        print("   → Le système démarre avec une table watch_progress vide")
    else:
        # Trouver le profil principal
        cursor.execute("SELECT id FROM profiles WHERE is_main = 1 LIMIT 1")
        main_profile = cursor.fetchone()
        
        if main_profile:
            main_profile_id = main_profile[0]
            print(f"   → Profil principal trouvé (ID: {main_profile_id})")
            
            # Migrer toutes les vidéos avec une position > 0
            cursor.execute("""
                SELECT id, last_position, last_position_updated 
                FROM videos 
                WHERE last_position > 0
            """)
            videos_with_position = cursor.fetchall()
            
            migrated = 0
            for video_id, position, updated_at in videos_with_position:
                try:
                    cursor.execute("""
                        INSERT INTO watch_progress (profile_id, video_id, position, updated_at)
                        VALUES (?, ?, ?, ?)
                    """, (
                        main_profile_id,
                        video_id,
                        position,
                        updated_at or datetime.utcnow().isoformat()
                    ))
                    migrated += 1
                except sqlite3.IntegrityError:
                    # Déjà migré, ignorer
                    pass
            
            print(f"   ✓ {migrated} positions de lecture migrées vers le profil principal")
        else:
            print("   ⚠️  Aucun profil principal trouvé - migration des données ignorée")
    
    # 5. Option: Garder les colonnes last_position pour compatibilité
    #    (on peut les supprimer plus tard si tout fonctionne)
    print("\n💡 Note: Les colonnes 'last_position' et 'last_position_updated'")
    print("   sont conservées dans la table 'videos' pour compatibilité.")
    print("   Elles peuvent être supprimées ultérieurement si nécessaire.")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Migration terminée avec succès!")
    print("\n📝 Prochaines étapes:")
    print("   1. L'API utilise maintenant watch_progress par profil")
    print("   2. Chaque profil a sa propre liste de reprises")
    print("   3. Les anciennes colonnes sont conservées (compatibilité)")
    print("")


if __name__ == "__main__":
    migrate()
