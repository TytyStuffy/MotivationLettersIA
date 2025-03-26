#!/usr/bin/env python3
"""
Motivation Letter Generator - Launcher
Main entry point for the application.
"""
import sys
import os
import time
from textwrap import dedent

try:
    from decouple import config
    from quota_manager import quota_manager
except ImportError:
    print("\n❌ ERROR: The 'decouple' module is not installed.")
    print("Please install it using one of the following commands:")
    print("    pip install python-decouple")
    print("    poetry add python-decouple\n")
    sys.exit(1)

def check_quota_status():
    """Vérifie l'état des quotas et affiche un rapport"""
    try:
        report = quota_manager.get_usage_report()
        print("\n--- ÉTAT DE L'UTILISATION API ---")
        print(f"Requêtes totales: {report['total_requests']}")
        print(f"Erreurs de quota: {report['total_quota_errors']}")
        print(f"Aujourd'hui: {report['today']['requests']} requêtes, {report['today']['errors']} erreurs")
        print(f"Hier: {report['yesterday']['requests']} requêtes, {report['yesterday']['errors']} erreurs")
        
        if report['total_quota_errors'] > 0 and report['last_error']:
            try:
                from datetime import datetime
                error_time = datetime.fromisoformat(report['last_error'])
                now = datetime.now()
                hours_since = (now - error_time).total_seconds() / 3600
                if hours_since < 24:
                    print(f"\n⚠️ AVERTISSEMENT: Dernière erreur de quota il y a {hours_since:.1f} heures.")
                    print("Des délais peuvent survenir pendant la génération.")
                    if hours_since < 1:
                        print("Considérez d'attendre un peu avant de générer une nouvelle lettre.")
            except:
                pass
        
        print("--------------------------------\n")
    except Exception as e:
        print(f"Erreur lors de la vérification des quotas: {e}")

def main():
    """Main function that can be imported or run directly"""
    # Message d'introduction
    print("""
┌─────────────────────────────────────────────────────┐
│      Générateur de Lettres de Motivation            │
│                                                     │
│   L'outil idéal pour créer des lettres de           │
│   motivation personnalisées pour Parcoursup         │
└─────────────────────────────────────────────────────┘
""")

    # Vérifier l'état des quotas
    check_quota_status()

    # Exécuter directement l'approche qui fonctionne
    try:
        # Importer ici pour pouvoir vérifier l'existence de sessions
        from user_session import get_available_sessions
        from direct_approach import run_direct_approach
        
        # Vérifier si des sessions existent déjà
        sessions = get_available_sessions()
        
        if sessions:
            print(f"\nNous avons trouvé {len(sessions)} session(s) précédente(s).")
            choice = input("Souhaitez-vous reprendre une session existante, ou en créer une nouvelle ? (e/n): ").lower()
            
            if choice in ['e', 'existante', 'oui', 'o']:
                # L'utilisateur sera redirigé vers l'interface de choix de session dans run_direct_approach
                print("\nRedirection vers les sessions existantes...")
                # Appeler run_direct_approach avec des URLs vides - elles seront demandées à l'utilisateur dans la fonction
                run_direct_approach("", "")
                return 0
        
        # Même dans ce cas, on demande les URLs, mais on les passe à la fonction
        # Les URLs seront à nouveau demandées dans run_direct_approach si vides
        print("\nPour commencer une nouvelle session, nous avons besoin d'informations sur votre candidature.")
        print("-------------------------------")
        parcoursup_url = input("URL Parcoursup du programme: ")
        etablissement_url = input("URL du site web de l'établissement: ")

        print("\nLancement du générateur de lettres de motivation...\n")
        run_direct_approach(parcoursup_url, etablissement_url)
        return 0
    except ImportError:
        print("\n❌ ERROR: Could not import the required modules.")
        print("Please install all dependencies using one of the following commands:")
        print("    pip install -r requirements.txt")
        print("    or")
        print("    poetry install\n")
        return 1
    except Exception as e:
        print(f"Erreur lors de l'exécution: {str(e)}")
        print("Une erreur s'est produite. Veuillez réessayer ultérieurement.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
