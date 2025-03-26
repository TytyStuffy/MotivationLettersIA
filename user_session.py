"""
Module de gestion des sessions utilisateur pour le générateur de lettres de motivation.
Permet de sauvegarder et charger les informations des utilisateurs.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

# Dossier pour stocker les sessions utilisateurs
SESSION_DIR = "user_sessions"

def ensure_session_dir():
    """S'assure que le dossier de sessions existe"""
    if not os.path.exists(SESSION_DIR):
        os.makedirs(SESSION_DIR)

def save_user_profile(user_data: Dict[str, Any], session_id: Optional[str] = None) -> str:
    """
    Sauvegarde les données de l'utilisateur dans un fichier JSON.
    
    Args:
        user_data (dict): Données utilisateur à sauvegarder
        session_id (str, optional): Identifiant de session si mise à jour d'une session existante
    
    Returns:
        str: Identifiant de la session
    """
    ensure_session_dir()
    
    # Générer un ID de session si non fourni
    if not session_id:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"session_{timestamp}"
    
    # Ajouter les métadonnées
    if "metadata" not in user_data:
        user_data["metadata"] = {}
    
    user_data["metadata"]["session_id"] = session_id
    user_data["metadata"]["last_updated"] = datetime.now().isoformat()
    
    # Sauvegarder dans le fichier
    file_path = os.path.join(SESSION_DIR, f"{session_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)
    
    return session_id

def load_user_profile(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Charge les données d'une session utilisateur.
    
    Args:
        session_id (str): Identifiant de la session à charger
    
    Returns:
        dict or None: Données utilisateur ou None si non trouvé
    """
    file_path = os.path.join(SESSION_DIR, f"{session_id}.json")
    
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement de la session {session_id}: {str(e)}")
        return None

def get_available_sessions() -> List[Dict[str, Any]]:
    """
    Récupère la liste des sessions disponibles.
    
    Returns:
        list: Liste des sessions disponibles avec leurs métadonnées
    """
    ensure_session_dir()
    
    sessions = []
    for filename in os.listdir(SESSION_DIR):
        if filename.endswith('.json'):
            try:
                session_id = filename[:-5]  # Enlever l'extension .json
                file_path = os.path.join(SESSION_DIR, filename)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extraire les informations essentielles
                metadata = data.get("metadata", {})
                username = data.get("personal_info", {}).get("name", "Utilisateur inconnu")
                last_updated = metadata.get("last_updated", "Date inconnue")
                
                if isinstance(last_updated, str):
                    try:
                        date_obj = datetime.fromisoformat(last_updated)
                        last_updated = date_obj.strftime("%d/%m/%Y %H:%M")
                    except:
                        pass
                
                # Ajouter à la liste des sessions
                sessions.append({
                    "session_id": session_id,
                    "username": username,
                    "last_updated": last_updated,
                    "program": data.get("program_info", {}).get("name", "Programme inconnu")
                })
            except Exception as e:
                print(f"Erreur lors de la lecture de {filename}: {str(e)}")
    
    # Trier par date de mise à jour (la plus récente d'abord)
    return sorted(sessions, key=lambda x: x["session_id"], reverse=True)

def delete_session(session_id: str) -> bool:
    """
    Supprime une session utilisateur.
    
    Args:
        session_id (str): Identifiant de la session à supprimer
    
    Returns:
        bool: True si la suppression a réussi, False sinon
    """
    file_path = os.path.join(SESSION_DIR, f"{session_id}.json")
    
    if not os.path.exists(file_path):
        return False
    
    try:
        os.remove(file_path)
        return True
    except Exception as e:
        print(f"Erreur lors de la suppression de la session {session_id}: {str(e)}")
        return False
