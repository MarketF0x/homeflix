"""
Helper pour exécuter des subprocess sans fenêtre visible (Windows)
Centralise la gestion CREATE_NO_WINDOW pour tous les appels subprocess
"""

import subprocess
import sys
from typing import List, Optional, Any

# Flag Windows pour masquer la fenêtre console
if sys.platform == "win32":
    _STARTUPINFO = subprocess.STARTUPINFO()
    _STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    _STARTUPINFO.wShowWindow = subprocess.SW_HIDE
    _CREATE_NO_WINDOW = 0x08000000
else:
    _STARTUPINFO = None
    _CREATE_NO_WINDOW = 0


def run_hidden(
    cmd: List[str],
    capture_output: bool = False,
    text: bool = True,
    check: bool = False,
    timeout: Optional[float] = None,
    **kwargs
) -> subprocess.CompletedProcess:
    """
    Exécute une commande subprocess sans afficher de fenêtre (Windows).
    
    Args:
        cmd: Commande et arguments
        capture_output: Capturer stdout/stderr
        text: Mode texte (vs binaire)
        check: Lever exception si erreur
        timeout: Timeout en secondes
        **kwargs: Arguments supplémentaires pour subprocess.run
    
    Returns:
        CompletedProcess
    """
    if sys.platform == "win32":
        kwargs.setdefault('creationflags', _CREATE_NO_WINDOW)
        kwargs.setdefault('startupinfo', _STARTUPINFO)
    
    return subprocess.run(
        cmd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        **kwargs
    )


def popen_hidden(
    cmd: List[str],
    stdout=None,
    stderr=None,
    stdin=None,
    **kwargs
) -> subprocess.Popen:
    """
    Crée un Popen subprocess sans afficher de fenêtre (Windows).
    
    Args:
        cmd: Commande et arguments
        stdout: Redirection stdout
        stderr: Redirection stderr
        stdin: Redirection stdin
        **kwargs: Arguments supplémentaires pour subprocess.Popen
    
    Returns:
        Popen instance
    """
    if sys.platform == "win32":
        kwargs.setdefault('creationflags', _CREATE_NO_WINDOW)
        kwargs.setdefault('startupinfo', _STARTUPINFO)
    
    return subprocess.Popen(
        cmd,
        stdout=stdout,
        stderr=stderr,
        stdin=stdin,
        **kwargs
    )


def popen_visible(
    cmd: List[str],
    stdout=None,
    stderr=None,
    stdin=None,
    **kwargs
) -> subprocess.Popen:
    """
    Crée un Popen subprocess AVEC fenêtre visible (pour lecteurs vidéo).
    Cache uniquement la console de lancement, pas la fenêtre de l'application.
    
    Args:
        cmd: Commande et arguments
        stdout: Redirection stdout
        stderr: Redirection stderr
        stdin: Redirection stdin
        **kwargs: Arguments supplémentaires pour subprocess.Popen
    
    Returns:
        Popen instance
    """
    if sys.platform == "win32":
        # CREATE_NO_WINDOW cache la console mais pas l'app graphique
        kwargs.setdefault('creationflags', _CREATE_NO_WINDOW)
        # On ne met PAS de startupinfo pour laisser la fenêtre visible
    
    return subprocess.Popen(
        cmd,
        stdout=stdout,
        stderr=stderr,
        stdin=stdin,
        **kwargs
    )
