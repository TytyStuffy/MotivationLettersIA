#!/usr/bin/env python3
"""
Outil pour vérifier l'état des quotas API et générer un rapport.
"""
import sys
import json
from datetime import datetime, timedelta
from quota_manager import quota_manager

def display_report():
    """Affiche un rapport détaillé sur l'utilisation de l'API"""
    try:
        report = quota_manager.get_usage_report()
        
        print("\n===== RAPPORT D'UTILISATION DE L'API GEMINI =====\n")
        
        print(f"Requêtes totales effectuées: {report['total_requests']}")
        print(f"Erreurs de quota rencontrées: {report['total_quota_errors']}")
        
        # Afficher les détails quotidiens
        print("\nUtilisation récente:")
        print(f"- Aujourd'hui: {report['today']['requests']} requêtes, {report['today']['errors']} erreurs")
        print(f"- Hier: {report['yesterday']['requests']} requêtes, {report['yesterday']['errors']} erreurs")
        
        # Afficher les informations sur la dernière erreur
        if report['last_error']:
            try:
                error_time = datetime.fromisoformat(report['last_error'])
                now = datetime.now()
                hours_since = (now - error_time).total_seconds() / 3600
                
                print("\nDernière erreur de quota:")
                print(f"- Date: {error_time.strftime('%d/%m/%Y %H:%M:%S')}")
                print(f"- Il y a: {hours_since:.1f} heures")
                
                if hours_since < 24:
                    print("\n⚠️ ATTENTION: Des erreurs de quota récentes peuvent indiquer que vous avez")
                    print("atteint votre limite d'utilisation. Google applique généralement des")
                    print("limites sur des périodes de 24 heures ou 60 secondes.")
                    
                    if hours_since < 1:
                        print("\n🛑 RECOMMANDATION: Attendez au moins une heure avant de faire")
                        print("de nouvelles requêtes pour éviter des délais supplémentaires.")
                    else:
                        print("\n⚠️ RECOMMANDATION: Limitez le nombre de requêtes dans les prochaines heures.")
                else:
                    print("\n✅ Bon à savoir: Votre dernière erreur de quota remonte à plus de 24 heures.")
                    print("Vous ne devriez pas rencontrer de problèmes immédiats de limitation.")
            except Exception as e:
                print(f"\nErreur lors de l'analyse de la date de dernière erreur: {e}")
        else:
            print("\n✅ Aucune erreur de quota n'a été enregistrée jusqu'à présent.")
        
        print("\n===== CONSEILS D'UTILISATION =====")
        print("- Les quotas Google Gemini sont généralement basés sur des périodes de 24h et 60s")
        print("- Pour éviter les erreurs, espacez vos générations de plusieurs minutes")
        print("- Si vous rencontrez des erreurs, attendez quelques heures avant de réessayer")
        print("- Considérez une mise à niveau vers un plan payant pour plus de requêtes\n")
        
    except Exception as e:
        print(f"Erreur lors de la génération du rapport: {e}")
        return 1
    
    return 0

def reset_stats():
    """Réinitialise les statistiques d'utilisation"""
    try:
        confirm = input("Êtes-vous sûr de vouloir réinitialiser toutes les statistiques d'utilisation? (oui/non): ")
        if confirm.lower() != "oui":
            print("Opération annulée.")
            return 0
            
        # Réinitialiser les statistiques
        quota_manager.usage_stats = {
            "total_requests": 0,
            "quota_errors": 0,
            "last_error_time": None,
            "daily_usage": {},
            "hourly_limits": {}
        }
        quota_manager._save_usage_stats()
        print("Les statistiques d'utilisation ont été réinitialisées avec succès.")
        return 0
    except Exception as e:
        print(f"Erreur lors de la réinitialisation des statistiques: {e}")
        return 1

def main():
    """Fonction principale"""
    # Analyser les arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        return reset_stats()
    else:
        return display_report()

if __name__ == "__main__":
    sys.exit(main())
