"""
Module de gestion des quotas pour l'API Gemini.
Permet de contrôler l'utilisation de l'API et de gérer les erreurs de quota.
"""

import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import threading

class QuotaManager:
    """
    Gère les quotas et les limites de taux pour l'API Gemini.
    - Implémente un backoff exponentiel pour les erreurs 429
    - Surveille l'utilisation pour éviter d'atteindre les limites
    - Stocke les statistiques d'utilisation
    """
    
    # Chemin du fichier de statistiques d'utilisation
    USAGE_FILE = "api_usage_stats.json"
    
    # Verrouillage pour assurer l'accès thread-safe aux statistiques
    _lock = threading.Lock()
    
    def __init__(self, max_retries: int = 3, initial_delay: float = 2.0):
        """
        Initialise le gestionnaire de quota.
        
        Args:
            max_retries: Nombre maximum de tentatives en cas d'erreur de quota
            initial_delay: Délai initial (en secondes) avant de réessayer
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.usage_stats = self._load_usage_stats()
    
    def _load_usage_stats(self) -> Dict[str, Any]:
        """Charge les statistiques d'utilisation depuis le fichier"""
        if os.path.exists(self.USAGE_FILE):
            try:
                with open(self.USAGE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erreur lors du chargement des statistiques: {e}")
        
        # Statistiques par défaut si le fichier n'existe pas
        return {
            "total_requests": 0,
            "quota_errors": 0,
            "last_error_time": None,
            "daily_usage": {},
            "hourly_limits": {}
        }
    
    def _save_usage_stats(self) -> None:
        """Sauvegarde les statistiques d'utilisation dans le fichier"""
        with self._lock:
            try:
                with open(self.USAGE_FILE, 'w') as f:
                    json.dump(self.usage_stats, f, indent=2)
            except Exception as e:
                print(f"Erreur lors de la sauvegarde des statistiques: {e}")
    
    def update_usage(self, success: bool = True, quota_error: bool = False) -> None:
        """
        Met à jour les statistiques d'utilisation.
        
        Args:
            success: Si la requête a réussi
            quota_error: Si l'erreur est due à une limite de quota
        """
        with self._lock:
            # Mettre à jour les compteurs globaux
            self.usage_stats["total_requests"] += 1
            
            if quota_error:
                self.usage_stats["quota_errors"] += 1
                self.usage_stats["last_error_time"] = datetime.now().isoformat()
            
            # Mettre à jour l'utilisation quotidienne
            today = datetime.now().strftime("%Y-%m-%d")
            if today not in self.usage_stats["daily_usage"]:
                self.usage_stats["daily_usage"][today] = {"requests": 0, "errors": 0}
            
            self.usage_stats["daily_usage"][today]["requests"] += 1
            if quota_error:
                self.usage_stats["daily_usage"][today]["errors"] += 1
            
            # Limiter l'historique à 30 jours
            dates = list(self.usage_stats["daily_usage"].keys())
            if len(dates) > 30:
                oldest_dates = sorted(dates)[:-30]
                for date in oldest_dates:
                    self.usage_stats["daily_usage"].pop(date, None)
            
            # Sauvegarder les statistiques mises à jour
            self._save_usage_stats()
    
    def should_throttle(self) -> Tuple[bool, float]:
        """
        Vérifie si les requêtes doivent être limitées en fonction de l'historique récent.
        
        Returns:
            Tuple[bool, float]: (Faut-il limiter?, Délai recommandé en secondes)
        """
        with self._lock:
            # Si aucune erreur récente, pas besoin de limiter
            if self.usage_stats.get("last_error_time") is None:
                return False, 0
            
            # Vérifier si une erreur s'est produite récemment (dernière heure)
            try:
                last_error = datetime.fromisoformat(self.usage_stats["last_error_time"])
                now = datetime.now()
                time_since_error = (now - last_error).total_seconds()
                
                # Si l'erreur est récente, suggérer un délai
                if time_since_error < 3600:  # Moins d'une heure
                    # Plus l'erreur est récente, plus le délai est long
                    suggested_delay = max(1.0, 60 * (1 - time_since_error/3600))
                    return True, suggested_delay
            except Exception:
                pass
            
            return False, 0
    
    def handle_request(self, request_func, *args, **kwargs) -> Any:
        """
        Gère une requête API avec retry et backoff exponentiel.
        
        Args:
            request_func: Fonction à exécuter pour la requête API
            *args, **kwargs: Arguments à passer à request_func
            
        Returns:
            Any: Le résultat de request_func si réussi
            
        Raises:
            Exception: Si toutes les tentatives échouent
        """
        # Vérifier s'il faut limiter les requêtes
        should_limit, delay = self.should_throttle()
        if should_limit:
            print(f"⚠️ Limitation préventive des requêtes. Attente de {delay:.1f} secondes...")
            time.sleep(delay)
        
        retry_count = 0
        delay = self.initial_delay
        
        while retry_count <= self.max_retries:
            try:
                result = request_func(*args, **kwargs)
                # Mettre à jour les statistiques en cas de succès
                self.update_usage(success=True)
                return result
                
            except Exception as e:
                error_msg = str(e).lower()
                is_quota_error = "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg
                
                # Mettre à jour les statistiques
                self.update_usage(success=False, quota_error=is_quota_error)
                
                if is_quota_error and retry_count < self.max_retries:
                    retry_count += 1
                    wait_time = delay * (2 ** (retry_count - 1))  # Backoff exponentiel
                    
                    # Extraire le délai suggéré si disponible
                    suggested_delay = None
                    if "retry_delay" in error_msg:
                        try:
                            # Tentative d'extraction du délai suggéré (Google API)
                            import re
                            match = re.search(r"retry_delay\s*{\s*seconds:\s*(\d+)", error_msg)
                            if match:
                                suggested_delay = int(match.group(1))
                        except Exception:
                            pass
                    
                    # Utiliser le délai suggéré s'il est disponible
                    if suggested_delay is not None and suggested_delay > 0:
                        wait_time = suggested_delay
                    
                    print(f"⚠️ Erreur de quota API (tentative {retry_count}/{self.max_retries}). "
                          f"Nouvelle tentative dans {wait_time:.1f} secondes...")
                    time.sleep(wait_time)
                else:
                    # Relancer l'exception si ce n'est pas une erreur de quota
                    # ou si nous avons épuisé nos tentatives
                    raise
        
        # Ne devrait jamais arriver ici, mais par sécurité
        raise Exception(f"Toutes les tentatives ont échoué ({self.max_retries + 1} essais)")
    
    def get_usage_report(self) -> Dict[str, Any]:
        """
        Génère un rapport d'utilisation pour l'API.
        
        Returns:
            Dict[str, Any]: Statistiques d'utilisation
        """
        with self._lock:
            today = datetime.now().strftime("%Y-%m-%d")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            today_stats = self.usage_stats["daily_usage"].get(today, {"requests": 0, "errors": 0})
            yesterday_stats = self.usage_stats["daily_usage"].get(yesterday, {"requests": 0, "errors": 0})
            
            return {
                "total_requests": self.usage_stats["total_requests"],
                "total_quota_errors": self.usage_stats["quota_errors"],
                "today": today_stats,
                "yesterday": yesterday_stats,
                "last_error": self.usage_stats.get("last_error_time"),
            }

# Instance globale pour faciliter l'importation
quota_manager = QuotaManager()
