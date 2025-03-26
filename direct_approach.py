import os
import sys
import json
from typing import Dict, Optional, Any, Tuple, List

try:
    import google.generativeai as genai
    from decouple import config
    from textwrap import dedent
    from tools.scraping_tools import scrape_parcoursup, scrape_etablissement
    from user_session import save_user_profile, load_user_profile, get_available_sessions
except ImportError as e:
    module_name = str(e).split("'")[-2]
    print(f"\n❌ ERROR: The '{module_name}' module is not installed.")
    print("Please install all dependencies using one of the following commands:")
    print("    pip install -r requirements.txt")
    print("    or")
    print("    poetry install\n")
    sys.exit(1)

# Configuration de l'API
try:
    API_KEY = config("GOOGLE_API_KEY")
    if not API_KEY:
        print("❌ ERROR: GOOGLE_API_KEY is not set in your .env file.")
        print("Please create a .env file with your Google API key.")
        print("Example: GOOGLE_API_KEY=your_api_key_here")
        sys.exit(1)
    os.environ["GOOGLE_API_KEY"] = API_KEY  # Aussi définir la variable d'environnement pour être sûr
except Exception as e:
    print(f"❌ ERROR: Failed to load GOOGLE_API_KEY from .env file: {e}")
    print("Please make sure you have a .env file with your Google API key.")
    print("Example: GOOGLE_API_KEY=your_api_key_here")
    sys.exit(1)

# Importer le gestionnaire de quota
from quota_manager import quota_manager

def generate_text(prompt, temperature=0.7):
    """Fonction simple pour générer du texte avec Gemini"""
    try:
        # Utiliser le gestionnaire de quota pour gérer les requêtes API
        def request_function():
            model = genai.GenerativeModel('gemini-pro', generation_config={"temperature": temperature})
            response = model.generate_content(prompt)
            return response.text
        
        # Utiliser le gestionnaire de quotas pour gérer les limites de taux
        return quota_manager.handle_request(request_function)
    except Exception as e:
        print(f"Erreur lors de la génération de texte: {str(e)}")
        return f"Une erreur est survenue: {str(e)}"

def load_previous_session() -> Optional[Dict[str, Any]]:
    """Permet à l'utilisateur de choisir une session précédente"""
    sessions = get_available_sessions()
    
    if not sessions:
        print("Aucune session précédente trouvée.")
        return None
    
    print("\n--- SESSIONS PRÉCÉDENTES ---")
    print("0. Créer une nouvelle session")
    
    for i, session in enumerate(sessions, 1):
        print(f"{i}. {session['username']} - Programme: {session['program']} (Mis à jour: {session['last_updated']})")
    
    try:
        choice = input("\nVeuillez choisir une option (0-" + str(len(sessions)) + "): ")
        choice = int(choice)
        
        if choice == 0:
            return None
        elif 1 <= choice <= len(sessions):
            session_id = sessions[choice-1]["session_id"]
            user_data = load_user_profile(session_id)
            if user_data:
                print(f"Session '{sessions[choice-1]['username']}' chargée avec succès.")
                return user_data
            else:
                print("Erreur lors du chargement de la session.")
                return None
        else:
            print("Option invalide, création d'une nouvelle session.")
            return None
    except ValueError:
        print("Entrée invalide, création d'une nouvelle session.")
        return None
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return None

def ask_personal_info() -> Dict[str, str]:
    """Demande des informations personnelles à l'utilisateur"""
    print("\n--- INFORMATIONS PERSONNELLES ---")
    print("Ces informations nous aideront à personnaliser votre lettre.")
    
    info = {}
    
    try:
        info["name"] = input("Votre nom complet: ").strip()
        info["email"] = input("Votre email: ").strip()
        info["phone"] = input("Votre numéro de téléphone: ").strip()
        info["address"] = input("Votre adresse: ").strip()
        
        print("\nMerci pour ces informations!\n")
        return info
    except Exception as e:
        print(f"Erreur lors de la saisie des informations: {str(e)}")
        return {}

def interview_student(parcoursup_info, etablissement_info, previous_responses=None) -> Tuple[str, List[Dict[str, str]]]:
    """Simule l'entretien avec l'étudiant et retourne les réponses structurées"""
    prompt = dedent(f"""
    Tu es un intervieweur empathique spécialisé dans l'aide aux étudiants pour
    identifier et articuler leurs forces, motivations et expériences.
    
    Conduis une session de questions-réponses avec l'étudiant pour recueillir toutes les informations personnelles
    nécessaires à une lettre de motivation convaincante.
    
    Utilise les informations déjà collectées sur le programme :
    
    Information sur le programme :
    {parcoursup_info}
    
    Information sur l'établissement :
    {etablissement_info}
    
    Pose des questions sur :
    1. Parcours académique et réalisations
    2. Compétences et expériences pertinentes
    3. Pourquoi ils s'intéressent à ce programme spécifique
    4. Comment ce programme s'aligne avec leurs objectifs de carrière
    5. Qualités personnelles qui font d'eux un bon candidat
    6. Projets, expériences ou réalisations spécifiques qui démontrent leur passion
    7. Défis qu'ils ont surmontés et qui démontrent leur détermination
    8. Parcours professionnel, expériences associatives ou engagements bénévoles
    
    Sois conversationnel et adapte tes questions en fonction de leurs réponses.
    """)

    print("\n--- DÉBUT DE L'ENTRETIEN ---\n")
    print("Agent: Bonjour ! Je suis là pour vous aider à préparer votre lettre de motivation.")
    print("Agent: Commençons par discuter de votre parcours et de vos motivations.\n")
    
    student_profile = []
    response_data = []
    
    # Simuler plusieurs questions
    questions = [
        "Pourriez-vous me parler de votre parcours académique jusqu'à présent ?",
        "Quelles sont vos compétences ou expériences qui selon vous correspondent à ce programme ?",
        "Pourquoi êtes-vous intéressé(e) par ce programme spécifique ?",
        "Comment ce programme s'inscrit-il dans votre projet professionnel ?",
        "Quelles qualités personnelles pensez-vous apporter à ce programme ?",
        "Avez-vous des réalisations ou projets dont vous êtes particulièrement fier(e) ?",
        "Avez-vous dû surmonter des défis importants dans votre parcours ?",
        "Pouvez-vous me parler de vos expériences professionnelles, associatives ou de bénévolat qui pourraient être pertinentes pour cette candidature ?"
    ]
    
    # Gestion sécurisée des entrées avec option de réponses par défaut
    try:
        use_default = input("Souhaitez-vous utiliser des réponses prédéfinies pour le test ? (o/n): ").lower() in ['o', 'oui']
    except Exception:
        print("Erreur lors de la saisie. Utilisation des réponses prédéfinies par défaut.")
        use_default = True
    
    default_answers = [
        "J'ai obtenu un baccalauréat scientifique avec mention bien. Actuellement, je suis en classe préparatoire scientifique où j'étudie les mathématiques, la physique et l'informatique.",
        "J'ai développé des compétences analytiques solides et une capacité à résoudre des problèmes complexes. J'ai également participé à plusieurs projets informatiques qui m'ont permis de développer mes compétences en programmation et en travail d'équipe.",
        "Ce programme m'intéresse particulièrement pour son approche pluridisciplinaire et sa réputation d'excellence. La possibilité de combiner théorie et pratique correspond parfaitement à ma façon d'apprendre.",
        "Ce programme s'inscrit parfaitement dans mon projet de devenir ingénieur/analyste de données. Les compétences que je pourrai y développer me permettront d'avoir une carrière dans un domaine en constante évolution.",
        "Je suis rigoureux, persévérant et j'ai une grande capacité d'adaptation. Je suis également curieux et toujours désireux d'apprendre de nouvelles choses.",
        "J'ai développé une application mobile qui a remporté un prix dans un concours étudiant. Ce projet m'a permis de mettre en pratique mes connaissances théoriques et de développer mes compétences en gestion de projet.",
        "J'ai dû concilier mes études et un emploi à temps partiel pour financer ma scolarité. Cette expérience m'a appris à gérer mon temps efficacement et à rester déterminé face aux défis.",
        "J'ai été membre actif de l'association informatique de mon école où j'ai organisé des ateliers de programmation. J'ai également effectué un stage de 3 mois dans une entreprise de développement logiciel où j'ai participé à la création d'une application web. Ces expériences m'ont permis de développer mes compétences en leadership et en communication."
    ]
    
    for i, question in enumerate(questions):
        print(f"Agent: {question}")
        
        # Si nous avons des réponses précédentes, utilisons-les
        if previous_responses and i < len(previous_responses):
            answer = previous_responses[i]["answer"]
            print(f"Vous: {answer} (réponse précédente)")
        elif use_default:
            answer = default_answers[i]
            print(f"Vous: {answer} (réponse prédéfinie)")
        else:
            try:
                answer = input("Vous: ")
                if not answer.strip():  # Si la réponse est vide
                    answer = default_answers[i]
                    print(f"Réponse vide, utilisation de la réponse par défaut: {answer}")
            except Exception as e:
                answer = default_answers[i]
                print(f"Erreur lors de la saisie: {e}")
                print(f"Utilisation de la réponse par défaut: {answer}")
        
        student_profile.append(f"Question: {question}\nRéponse: {answer}")
        response_data.append({"question": question, "answer": answer})
    
    print("\n--- FIN DE L'ENTRETIEN ---\n")
    
    # Compiler le profil étudiant
    full_profile = "\n\n".join(student_profile)
    return full_profile, response_data

def generate_formal_letter(parcoursup_info, etablissement_info, student_info):
    """Génère une lettre de motivation formelle"""
    prompt = dedent(f"""
    Crée une lettre de motivation formelle et structurée pour l'étudiant en te basant sur toutes les informations collectées.
    
    Information sur le programme :
    {parcoursup_info}
    
    Information sur l'établissement :
    {etablissement_info}
    
    Profil de l'étudiant :
    {student_info}
    
    Ta lettre doit :
    1. Suivre un format professionnel traditionnel
    2. Démontrer clairement comment l'étudiant répond aux exigences du programme
    3. Mettre en valeur les réalisations académiques, expériences professionnelles, associatives et pertinentes
    4. Établir un lien entre le parcours global de l'étudiant et les objectifs du programme
    5. Être bien structurée avec une introduction, des paragraphes de développement et une conclusion
    6. Utiliser un langage formel tout en restant personnalisée
    7. NE PAS inclure les informations du destinataire, ni l'en-tête avec le nom, prénom, adresse, téléphone, etc.
    8. NE PAS inclure de signature ou de formule de politesse finale comme "Veuillez agréer..."
    
    IMPORTANT: 
    - UTILISER EXACTEMENT 1490 caractères (espaces compris). PAS PLUS NI MOINS.
    - Donne UNIQUEMENT le texte de la lettre sans aucun formatage supplémentaire (pas d'en-tête, pas de signature).
    - Sois concis et va à l'essentiel tout en étant convaincant.
    - Incorpore des termes et phrases spécifiques tirés des descriptions du programme et de l'établissement.
    - Utilise des mots-clés du domaine d'études concerné.
    - Fais référence explicitement à des éléments précis mentionnés sur le site du programme.
    
    Concentre-toi sur la création d'un argumentaire efficace expliquant pourquoi cet étudiant est qualifié et réussira dans ce programme.
    Assure-toi d'intégrer harmonieusement les expériences professionnelles, associatives ou bénévoles si elles sont mentionnées.
    """)
    
    letter = generate_text(prompt, temperature=0.7)
    
    # Vérifier et ajuster la longueur
    letter = adjust_letter_length(letter, 1490)
    
    return letter

def generate_creative_letter(parcoursup_info, etablissement_info, student_info):
    """Génère une lettre de motivation créative"""
    prompt = dedent(f"""
    Crée une lettre de motivation engageante et narrative pour l'étudiant en te basant sur toutes les informations collectées.
    
    Information sur le programme :
    {parcoursup_info}
    
    Information sur l'établissement :
    {etablissement_info}
    
    Profil de l'étudiant :
    {student_info}
    
    Ta lettre doit :
    1. Commencer par une introduction captivante
    2. Raconter une histoire convaincante sur le parcours complet de l'étudiant (académique, professionnel et associatif)
    3. Utiliser des exemples vivants et des anecdotes spécifiques tirées de ses diverses expériences
    4. Mettre en valeur la passion et les qualités uniques de l'étudiant
    5. Démontrer une connaissance claire du programme tout en maintenant un ton personnel
    6. Se terminer par une conclusion mémorable
    7. NE PAS inclure les informations du destinataire, ni l'en-tête avec le nom, prénom, adresse, téléphone, etc.
    8. NE PAS inclure de signature ou de formule de politesse finale comme "Veuillez agréer..."
    
    IMPORTANT: 
    - UTILISER EXACTEMENT 1490 caractères (espaces compris). PAS PLUS NI MOINS.
    - Donne UNIQUEMENT le texte de la lettre sans aucun formatage supplémentaire (pas d'en-tête, pas de signature).
    - Sois concis mais percutant en te concentrant sur les éléments les plus marquants.
    - Incorpore des termes et phrases spécifiques tirés des descriptions du programme et de l'établissement.
    - Fais référence à l'environnement d'apprentissage, aux valeurs ou à la réputation de l'établissement.
    - Mentionne des éléments spécifiques et distinctifs du programme que l'étudiant a trouvés attrayants.
    
    Concentre-toi sur la création d'une lettre authentique et mémorable qui révèle la personne derrière la candidature.
    Si l'étudiant a mentionné des expériences professionnelles, associatives ou bénévoles, utilise-les pour illustrer 
    des compétences transversales comme le leadership, le travail d'équipe ou l'engagement.
    """)
    
    letter = generate_text(prompt, temperature=0.9)
    
    # Vérifier et ajuster la longueur
    letter = adjust_letter_length(letter, 1490)
    
    return letter

def fusion_letters(letter1, letter2):
    """Fusionne les deux versions de la lettre"""
    prompt = dedent(f"""
    Analyse les deux versions de lettre de motivation et crée une version finale optimisée.
    
    Version 1 (formelle) :
    {letter1}
    
    Version 2 (créative) :
    {letter2}
    
    Ta tâche :
    1. Identifie les points forts de chaque lettre
    2. Compare comment chaque lettre répond aux exigences du programme et aux qualités de l'étudiant
    3. Sélectionne la structure, le ton et l'approche les plus efficaces
    4. Combine les meilleurs éléments des deux lettres
    5. Assure-toi que la lettre finale est cohérente, convaincante et authentique
    6. Vérifie si des opportunités ont été manquées dans les deux versions originales
    7. NE PAS inclure les informations du destinataire, ni l'en-tête avec le nom, prénom, adresse, téléphone, etc.
    8. NE PAS inclure de signature ou de formule de politesse finale comme "Veuillez agréer..."
    
    IMPORTANT: 
    - UTILISER EXACTEMENT 1490 caractères (espaces compris). PAS PLUS NI MOINS.
    - Donne UNIQUEMENT le texte final sans aucun formatage supplémentaire (pas d'en-tête, pas de signature).
    - Crée une lettre finale soignée (en français) qui maximise les chances d'admission de l'étudiant.
    - Incorpore des termes et phrases spécifiques tirés des deux lettres ET des descriptions du programme.
    - Assure-toi de faire référence à des éléments précis de l'établissement et du programme.
    - Utilise le vocabulaire du domaine d'études concerné.
    
    La lettre doit se lire comme un tout cohérent, et non comme des morceaux disparates.
    """)
    
    letter = generate_text(prompt, temperature=0.7)
    
    # Vérifier et ajuster la longueur
    letter = adjust_letter_length(letter, 1490)
    
    return letter

def adjust_letter_length(letter, target_length=1490):
    """
    Ajuste précisément la longueur de la lettre au nombre de caractères cible.
    """
    current_length = len(letter)
    
    # Si la différence est minime (±30 caractères), c'est acceptable
    if abs(current_length - target_length) <= 30:
        print(f"✓ Lettre générée: {current_length} caractères (proche de la cible)")
        return letter
    
    if current_length > target_length:
        # Si trop longue, demander une version plus courte
        print(f"⚠️ Lettre trop longue ({current_length} caractères). Ajustement...")
        shortened_prompt = dedent(f"""
        Voici une lettre de motivation qui est trop longue ({current_length} caractères).
        Raccourcis-la pour atteindre EXACTEMENT {target_length} caractères (espaces compris),
        tout en préservant les points clés et la qualité du contenu.
        
        Lettre à raccourcir:
        {letter}
        """)
        
        letter = generate_text(shortened_prompt, temperature=0.4)
    else:
        # Si trop courte, demander une version plus longue
        print(f"⚠️ Lettre trop courte ({current_length} caractères). Ajustement...")
        extended_prompt = dedent(f"""
        Voici une lettre de motivation qui est trop courte ({current_length} caractères).
        Étends-la pour atteindre EXACTEMENT {target_length} caractères (espaces compris),
        en ajoutant des détails pertinents, des exemples concrets ou des références spécifiques
        au programme ou à l'établissement. Maintiens le même ton et style.
        
        Lettre à étendre:
        {letter}
        """)
        
        letter = generate_text(extended_prompt, temperature=0.4)
    
    # Vérifier la nouvelle longueur
    new_length = len(letter)
    print(f"✓ Lettre ajustée: {new_length} caractères")
    
    # Si toujours loin de la cible, faire un ajustement manuel
    if abs(new_length - target_length) > 30:
        if new_length > target_length:
            letter = letter[:target_length]
        else:
            # Ajouter des points si nécessaire
            letter = letter + "." * (target_length - new_length)
    
    return letter

def run_direct_approach(parcoursup_url, etablissement_url):
    # Configurer Gemini une seule fois
    genai.configure(api_key=API_KEY)
    
    try:
        # Vérifier l'état des quotas et afficher un avertissement si nécessaire
        usage_report = quota_manager.get_usage_report()
        if usage_report["total_quota_errors"] > 0:
            last_error_time = usage_report.get("last_error")
            if last_error_time:
                try:
                    from datetime import datetime
                    error_time = datetime.fromisoformat(last_error_time)
                    now = datetime.now()
                    hours_since = (now - error_time).total_seconds() / 3600
                    if hours_since < 24:
                        print(f"\n⚠️ AVERTISSEMENT: Des erreurs de quota ont été détectées "
                              f"récemment ({hours_since:.1f} heures). "
                              f"Des délais peuvent survenir pendant le processus.")
                except:
                    pass
        
        # Vérifier si l'utilisateur souhaite charger une session précédente
        user_data = load_previous_session()
        previous_responses = None
        session_id = None
        personal_info = {}
        
        # Demander les URLs à chaque fois, même avec une session chargée
        print("\nPour générer une lettre de motivation, veuillez fournir les informations suivantes:")
        
        # Si l'URL est vide (appelé depuis launcher avec session), demander l'URL
        if not parcoursup_url:
            parcoursup_url = input("URL Parcoursup du programme : ")
        
        if not etablissement_url:
            etablissement_url = input("URL du site web de l'établissement : ")
        
        # Scraper les nouvelles informations, même avec une session existante
        print("\nRecherche d'informations sur Parcoursup...")
        parcoursup_info = scrape_parcoursup(parcoursup_url)
        
        print("Recherche d'informations sur l'établissement...")
        etablissement_info = scrape_etablissement(etablissement_url)
        
        if user_data:
            # Utiliser les données précédentes pour les réponses uniquement
            session_id = user_data.get("metadata", {}).get("session_id")
            personal_info = user_data.get("personal_info", {})
            previous_responses = user_data.get("interview_responses", [])
            
            # Demander à l'utilisateur s'il souhaite mettre à jour ses réponses
            update_responses = input("\nSouhaitez-vous mettre à jour vos réponses précédentes ? (o/n): ").lower() in ['o', 'oui']
            
            if not update_responses:
                # Utiliser le profil précédent mais avec les nouvelles informations scrapées
                student_info_data = user_data.get("student_info", "")
                if not student_info_data:
                    print("Aucun profil étudiant trouvé dans la session précédente.")
                    print("Nous allons procéder à un nouvel entretien.")
                    student_info, interview_responses = interview_student(parcoursup_info, etablissement_info)
                else:
                    # Utiliser les réponses précédentes avec les nouvelles informations sur le programme
                    student_profile = []
                    for resp in previous_responses:
                        student_profile.append(f"Question: {resp['question']}\nRéponse: {resp['answer']}")
                    student_info = "\n\n".join(student_profile)
                    interview_responses = previous_responses
            else:
                # Faire un nouvel entretien avec les réponses précédentes
                student_info, interview_responses = interview_student(parcoursup_info, etablissement_info, previous_responses)
                
            # Pour les lettres, toujours générer de nouvelles versions avec les informations mises à jour
            regenerate = True
        else:
            # Demander les informations personnelles
            personal_info = ask_personal_info()
            
            # Étape 2: Entretien avec l'étudiant
            student_info, interview_responses = interview_student(parcoursup_info, etablissement_info)
            
            regenerate = True
        
        # Étape 3: Génération des lettres (toujours régénérer avec les nouvelles informations)
        if regenerate:
            print("\nGénération de la première version de lettre (formelle)...")
            letter1 = generate_formal_letter(parcoursup_info, etablissement_info, student_info)
            print(f"✓ Lettre formelle générée: {len(letter1)} caractères")
            
            print("Génération de la seconde version de lettre (créative)...")
            letter2 = generate_creative_letter(parcoursup_info, etablissement_info, student_info)
            print(f"✓ Lettre créative générée: {len(letter2)} caractères")
            
            # Étape 4: Fusion des lettres
            print("Optimisation et fusion des deux lettres...\n")
            final_letter = fusion_letters(letter1, letter2)
            print(f"✓ Lettre finale générée: {len(final_letter)} caractères")
        else:
            # Ce cas ne devrait plus se produire, mais le code est conservé par sécurité
            letter1 = user_data["letter1"]
            letter2 = user_data["letter2"]
            final_letter = user_data["final_letter"]
            print("\nUtilisation des lettres précédemment générées.")
        
        # Sauvegarder la session utilisateur
        session_data = {
            "personal_info": personal_info,
            "parcoursup_info": parcoursup_info,
            "etablissement_info": etablissement_info,
            "student_info": student_info,
            "interview_responses": interview_responses,
            "letter1": letter1,
            "letter2": letter2,
            "final_letter": final_letter,
            "program_info": {
                "url": parcoursup_url,
                "name": extract_program_name(parcoursup_info)
            },
            "institution_info": {
                "url": etablissement_url,
                "name": extract_institution_name(etablissement_info)
            }
        }
        
        session_id = save_user_profile(session_data, session_id)
        print(f"\nVos informations ont été sauvegardées dans la session: {session_id}")
        
        # Affichage du résultat
        print("\n\n########################")
        print("## Votre Lettre de Motivation:")
        print("########################\n")
        
        # Nettoyage du texte pour supprimer les éléments non désirés
        cleaned_letter = clean_letter_text(final_letter)
        print(cleaned_letter)
        
        # Option de sauvegarde avec gestion d'erreur
        save_letter_to_file(cleaned_letter)
        
        return cleaned_letter
    
    except Exception as e:
        print(f"Une erreur s'est produite pendant le processus: {e}")
        return "Le processus a rencontré une erreur et n'a pas pu être complété."

def extract_program_name(parcoursup_info):
    """Extrait le nom du programme depuis les informations Parcoursup"""
    try:
        lines = parcoursup_info.strip().split('\n')
        for line in lines:
            if "Program:" in line:
                return line.split("Program:")[1].strip()
    except:
        pass
    return "Programme inconnu"

def extract_institution_name(etablissement_info):
    """Extrait le nom de l'établissement depuis les informations"""
    try:
        lines = etablissement_info.strip().split('\n')
        for line in lines:
            if "Institution:" in line:
                return line.split("Institution:")[1].strip()
    except:
        pass
    return "Établissement inconnu"

def save_letter_to_file(letter):
    """Sauvegarde la lettre dans un fichier"""
    try:
        save_option = input("\nVoulez-vous sauvegarder cette lettre dans un fichier? (o/n): ").lower()
        if save_option in ['o', 'oui']:
            try:
                filename = input("Nom du fichier: ")
                if not filename.strip():
                    filename = "lettre_motivation"
            except Exception:
                filename = "lettre_motivation"
                print(f"Erreur lors de la saisie du nom de fichier. Utilisation de: {filename}")
            
            if not filename.endswith('.txt'):
                filename += '.txt'
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(letter)
            print(f"Lettre sauvegardée dans {filename}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")
        print("La lettre n'a pas pu être sauvegardée.")

def clean_letter_text(letter_text):
    """
    Nettoie le texte de la lettre pour ne garder que le contenu principal.
    Supprime les en-têtes, coordonnées et formules de politesse.
    """
    # Liste des patterns à rechercher et supprimer
    patterns_to_remove = [
        r"\[Votre Nom et Prénom\].*?\n",
        r"\[Votre Adresse\].*?\n",
        r"\[Votre Numéro de Téléphone\].*?\n",
        r"\[Votre Adresse E-mail\].*?\n",
        r"\[Date\].*?\n",
        r".*?Objet :.*?\n",
        r"Madame, Monsieur,\s*\n",
        r".*?À l'attention de.*?\n",
        r".*?Service des Admissions.*?\n",
        r".*?Cordialement,.*?\n",
        r".*?Veuillez agréer.*?distinguées\.",
        r".*?Dans l'attente de.*?distinguées\.",
        r"\[Votre Signature.*?\].*?\n"
    ]
    
    import re
    cleaned_text = letter_text
    
    # Suppression des patterns
    for pattern in patterns_to_remove:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.DOTALL)
    
    # Suppression des lignes vides multiples
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
    
    # Suppression des espaces en début et fin
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text

def scrape_parcoursup(url):
    """Scrape les informations de Parcoursup de manière plus approfondie"""
    from tools.scraping_tools import scrape_parcoursup as basic_scrape
    
    # Récupérer les informations de base
    basic_info = basic_scrape(url)
    
    # Enrichir avec des informations supplémentaires
    enrichment_prompt = dedent(f"""
    Voici des informations extraites d'une page Parcoursup:
    {basic_info}
    
    Analyse ces informations et enrichis-les en:
    1. Identifiant les mots-clés du domaine d'études
    2. Extrayant les compétences spécifiques recherchées
    3. Notant les éléments distinctifs du programme
    4. Repérant les aspects de la formation qui sont mis en avant
    5. Identifiant les valeurs et la philosophie du programme
    
    Assure-toi que l'information enrichie reste factuelle et basée uniquement sur ce qui est fourni.
    Organise les informations de manière structurée pour faciliter leur utilisation dans une lettre de motivation.
    """)
    
    try:
        enriched_info = generate_text(enrichment_prompt, temperature=0.3)
        return basic_info + "\n\nInformations enrichies:\n" + enriched_info
    except:
        return basic_info

def scrape_etablissement(url):
    """Scrape les informations de l'établissement de manière plus approfondie"""
    from tools.scraping_tools import scrape_etablissement as basic_scrape
    
    # Récupérer les informations de base
    basic_info = basic_scrape(url)
    
    # Enrichir avec des informations supplémentaires
    enrichment_prompt = dedent(f"""
    Voici des informations extraites du site d'un établissement d'enseignement:
    {basic_info}
    
    Analyse ces informations et enrichis-les en:
    1. Identifiant la réputation et les points forts de l'établissement
    2. Extrayant les valeurs et la culture de l'institution
    3. Notant les partenariats, projets ou réussites particulières
    4. Repérant les opportunités uniques offertes aux étudiants
    5. Identifiant les éléments de langage et formulations spécifiques utilisés
    
    Assure-toi que l'information enrichie reste factuelle et basée uniquement sur ce qui est fourni.
    Organise les informations de manière structurée pour faciliter leur utilisation dans une lettre de motivation.
    """)
    
    try:
        enriched_info = generate_text(enrichment_prompt, temperature=0.3)
        return basic_info + "\n\nInformations enrichies:\n" + enriched_info
    except:
        return basic_info

# Point d'entrée si exécuté directement
if __name__ == "__main__":
    print("## Bienvenue dans le Système de Génération de Lettres de Motivation")
    print("-------------------------------")
    parcoursup_url = input("Entrez l'URL Parcoursup du programme : ")
    etablissement_url = input("Entrez l'URL du site web de l'établissement : ")
    
    run_direct_approach(parcoursup_url, etablissement_url)
