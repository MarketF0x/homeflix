import os
import logging
import traceback
from datetime import datetime
from pathlib import Path

# Créer le logger
logger = logging.getLogger('homeflix')
logger.setLevel(logging.DEBUG)

# Définir le chemin du fichier de log
log_path = Path(__file__).parent.parent / 'error.log'

# Handler fichier
fh = logging.FileHandler(str(log_path), encoding='utf-8')
fh.setLevel(logging.DEBUG)

# Formatteur avec timestamp
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

def log_exception(e: Exception, context: str = None):
    """Log une exception avec son traceback et un contexte optionnel"""
    msg = f"\n{'='*80}\nException"
    if context:
        msg += f" dans {context}"
    msg += f":\n{str(e)}\n\nTraceback:\n"
    msg += traceback.format_exc()
    msg += f"\n{'='*80}"
    logger.error(msg)

def log_data(data: dict, context: str):
    """Log des données avec un contexte"""
    msg = f"\n{'-'*40}\n{context}:\n"
    for k, v in data.items():
        msg += f"{k}: {v}\n"
    msg += f"{'-'*40}"
    logger.info(msg)