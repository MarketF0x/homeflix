"""
Middleware de validation et sécurité pour l'API Homeflix
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import time
from collections import defaultdict
from typing import Dict
import re

# Rate limiting simple (en mémoire)
class RateLimiter:
    def __init__(self, max_requests: int = 100, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        # Nettoyer les anciennes requêtes
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window
        ]
        
        # Vérifier la limite
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        self.requests[client_id].append(now)
        return True

rate_limiter = RateLimiter(max_requests=100, window=60)

async def rate_limit_middleware(request: Request, call_next):
    """Middleware de rate limiting"""
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"}
        )
    
    response = await call_next(request)
    return response

def validate_file_path(file_path: str) -> Path:
    """
    Valide un chemin de fichier pour éviter les path traversal attacks
    """
    try:
        path = Path(file_path).resolve()
        
        # Vérifier que le chemin ne contient pas de ..
        if '..' in str(path):
            raise ValueError("Path traversal detected")
        
        return path
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid file path")

def sanitize_filename(filename: str) -> str:
    """
    Nettoie un nom de fichier pour éviter les injections
    """
    # Garder seulement les caractères alphanumériques, espaces, points, tirets et underscores
    sanitized = re.sub(r'[^\w\s\-\.]', '', filename)
    return sanitized

def validate_url(url: str) -> bool:
    """
    Valide une URL pour éviter les SSRF
    """
    # Pattern pour URLs HTTP/HTTPS valides
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False
    
    # Bloquer les IPs privées pour éviter SSRF
    private_ips = [
        r'^https?://127\.',
        r'^https?://10\.',
        r'^https?://172\.(1[6-9]|2[0-9]|3[01])\.',
        r'^https?://192\.168\.',
        r'^https?://localhost',
    ]
    
    for pattern in private_ips:
        if re.match(pattern, url, re.IGNORECASE):
            return False
    
    return True
