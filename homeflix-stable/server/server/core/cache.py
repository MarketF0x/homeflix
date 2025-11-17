"""
Système de cache simple en mémoire pour optimiser les performances
"""
from typing import Any, Optional, Callable
from functools import wraps
import time
import hashlib
import json

class Cache:
    """Cache en mémoire avec TTL"""
    
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        if key not in self._cache:
            return None
        
        # Vérifier l'expiration
        if time.time() - self._timestamps[key] > self.ttl:
            del self._cache[key]
            del self._timestamps[key]
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any):
        """Stocke une valeur dans le cache"""
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def delete(self, key: str):
        """Supprime une valeur du cache"""
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]
    
    def clear(self):
        """Vide tout le cache"""
        self._cache.clear()
        self._timestamps.clear()
    
    def invalidate_pattern(self, pattern: str):
        """Invalide toutes les clés correspondant à un pattern"""
        keys_to_delete = [k for k in self._cache.keys() if pattern in k]
        for key in keys_to_delete:
            self.delete(key)

# Instances de cache globales
video_cache = Cache(ttl=300)  # 5 minutes pour les vidéos
metadata_cache = Cache(ttl=3600)  # 1 heure pour les métadonnées
thumbnail_cache = Cache(ttl=7200)  # 2 heures pour les thumbnails

def cache_result(cache_instance: Cache, key_prefix: str = "", ttl: Optional[int] = None):
    """
    Décorateur pour mettre en cache le résultat d'une fonction
    
    Usage:
        @cache_result(video_cache, "videos")
        def get_all_videos():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer une clé unique basée sur les arguments
            key_parts = [key_prefix, func.__name__]
            
            # Ajouter les args à la clé
            if args:
                args_str = json.dumps(args, default=str)
                args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
                key_parts.append(args_hash)
            
            # Ajouter les kwargs à la clé
            if kwargs:
                kwargs_str = json.dumps(sorted(kwargs.items()), default=str)
                kwargs_hash = hashlib.md5(kwargs_str.encode()).hexdigest()[:8]
                key_parts.append(kwargs_hash)
            
            cache_key = ":".join(key_parts)
            
            # Vérifier le cache
            cached_value = cache_instance.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Calculer et mettre en cache
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator

def invalidate_cache_on_update(cache_instance: Cache, pattern: str):
    """
    Décorateur pour invalider le cache après une mise à jour
    
    Usage:
        @invalidate_cache_on_update(video_cache, "videos")
        def update_video(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cache_instance.invalidate_pattern(pattern)
            return result
        return wrapper
    return decorator
