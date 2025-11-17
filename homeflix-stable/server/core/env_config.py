"""
Gestion de la configuration via variables d'environnement
Support de .env pour une meilleure sécurité
"""
import os
from pathlib import Path
from typing import Optional

class EnvironmentConfig:
    """Configuration basée sur les variables d'environnement"""
    
    def __init__(self):
        self._load_env_file()
    
    def _load_env_file(self):
        """Charge le fichier .env s'il existe"""
        env_path = Path(__file__).parent.parent.parent / '.env'
        
        if not env_path.exists():
            return
        
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Ignorer les commentaires et lignes vides
                if not line or line.startswith('#'):
                    continue
                
                # Parser KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Ne pas écraser les variables déjà définies
                    if key not in os.environ:
                        os.environ[key] = value
    
    @property
    def tmdb_api_key(self) -> Optional[str]:
        """Clé API TMDb"""
        return os.getenv('TMDB_API_KEY')
    
    @property
    def host(self) -> str:
        """Hôte du serveur"""
        return os.getenv('HOST', '0.0.0.0')
    
    @property
    def port(self) -> int:
        """Port du serveur"""
        return int(os.getenv('PORT', '8000'))
    
    @property
    def debug(self) -> bool:
        """Mode debug"""
        return os.getenv('DEBUG', 'false').lower() == 'true'
    
    @property
    def database_path(self) -> Path:
        """Chemin vers la base de données"""
        db_path = os.getenv('DATABASE_PATH', './homeflix.db')
        return Path(__file__).parent.parent / db_path
    
    @property
    def log_level(self) -> str:
        """Niveau de log"""
        return os.getenv('LOG_LEVEL', 'INFO').upper()
    
    @property
    def log_file(self) -> str:
        """Fichier de log"""
        return os.getenv('LOG_FILE', 'homeflix.log')
    
    @property
    def max_upload_size(self) -> int:
        """Taille maximale d'upload en bytes"""
        size_str = os.getenv('MAX_UPLOAD_SIZE', '100MB')
        
        # Parser les suffixes MB, GB, etc.
        multipliers = {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
        
        for suffix, multiplier in multipliers.items():
            if size_str.upper().endswith(suffix):
                number = float(size_str[:-len(suffix)])
                return int(number * multiplier)
        
        return int(size_str)  # Assume bytes si pas de suffixe
    
    @property
    def enable_cache(self) -> bool:
        """Activer le cache"""
        return os.getenv('ENABLE_CACHE', 'true').lower() == 'true'
    
    @property
    def cache_ttl(self) -> int:
        """TTL du cache en secondes"""
        return int(os.getenv('CACHE_TTL', '3600'))

# Instance globale
env_config = EnvironmentConfig()
