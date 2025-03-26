import requests
from bs4 import BeautifulSoup
import re
import time
import random
from typing import Optional
import sys
import os

# Ajouter le répertoire parent au chemin pour importer quota_manager
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from quota_manager import quota_manager

# User agents pour simuler différents navigateurs
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
]

def get_random_user_agent():
    """Retourne un User-Agent aléatoire"""
    return random.choice(USER_AGENTS)

def fetch_url_content(url: str) -> Optional[str]:
    """Récupère le contenu d'une URL avec gestion d'erreur et retry"""
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la tentative {attempt+1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                # Attente exponentielle entre les tentatives
                wait_time = 2 ** attempt
                print(f"Nouvelle tentative dans {wait_time} secondes...")
                time.sleep(wait_time)
            else:
                print("Échec après plusieurs tentatives.")
                return None

def clean_text(text: str) -> str:
    """Nettoie le texte extrait"""
    # Supprimer les espaces et sauts de ligne multiples
    text = re.sub(r'\s+', ' ', text)
    # Supprimer les caractères de contrôle
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    return text.strip()

def extract_title(soup: BeautifulSoup) -> str:
    """Extrait le titre de la page"""
    title = soup.find('title')
    return title.get_text().strip() if title else "Titre non trouvé"

def extract_meta_description(soup: BeautifulSoup) -> str:
    """Extrait la méta description"""
    meta = soup.find('meta', attrs={'name': 'description'})
    if meta and meta.get('content'):
        return meta['content'].strip()
    return "Description non trouvée"

def extract_main_content(soup: BeautifulSoup) -> str:
    """Extrait le contenu principal de la page"""
    # Recherche des éléments qui contiennent généralement le contenu principal
    main_content = ""
    
    # Chercher les conteneurs principaux
    main_containers = soup.find_all(['main', 'article', 'div', 'section'], 
                                    class_=re.compile(r'(content|main|article)'))
    
    if main_containers:
        for container in main_containers[:3]:  # Prendre les 3 premiers conteneurs les plus pertinents
            paragraphs = container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li'])
            for p in paragraphs:
                text = clean_text(p.get_text())
                if len(text) > 20:  # Ignorer les textes trop courts
                    main_content += text + "\n"
    else:
        # Fallback: prendre tous les paragraphes de la page
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4'])
        for p in paragraphs:
            text = clean_text(p.get_text())
            if len(text) > 20:
                main_content += text + "\n"
    
    return main_content

def extract_parcoursup_specific(soup: BeautifulSoup) -> str:
    """Extrait des informations spécifiques à Parcoursup"""
    parcoursup_info = ""
    
    # Extraire les informations sur le programme
    program_name = ""
    program_elements = soup.find_all(['h1', 'h2'], class_=re.compile(r'(title|heading)'))
    if program_elements:
        program_name = clean_text(program_elements[0].get_text())
    
    # Extraire les conditions d'admission
    admission_info = ""
    admission_elements = soup.find_all(['div', 'section'], 
                                      class_=re.compile(r'(admission|requirements|condition)'))
    if admission_elements:
        for element in admission_elements:
            admission_info += clean_text(element.get_text()) + "\n"
    
    # Extraire les compétences et connaissances attendues
    skills_info = ""
    skills_elements = soup.find_all(['div', 'section', 'ul'], 
                                   class_=re.compile(r'(skills|competences|attendues)'))
    if skills_elements:
        for element in skills_elements:
            skills_info += clean_text(element.get_text()) + "\n"
    
    # Compiler les informations
    if program_name:
        parcoursup_info += f"Program: {program_name}\n\n"
    if admission_info:
        parcoursup_info += f"Admission Requirements:\n{admission_info}\n"
    if skills_info:
        parcoursup_info += f"Expected Skills:\n{skills_info}\n"
    
    return parcoursup_info

def extract_establishment_specific(soup: BeautifulSoup) -> str:
    """Extrait des informations spécifiques à l'établissement"""
    establishment_info = ""
    
    # Extraire le nom de l'établissement
    institution_name = ""
    name_elements = soup.find_all(['h1', 'h2', 'div'], 
                                 class_=re.compile(r'(title|name|logo)'))
    if name_elements:
        institution_name = clean_text(name_elements[0].get_text())
    
    # Extraire la présentation/mission de l'établissement
    mission_info = ""
    mission_elements = soup.find_all(['div', 'section', 'article'], 
                                    class_=re.compile(r'(about|mission|presentation)'))
    if mission_elements:
        for element in mission_elements:
            mission_info += clean_text(element.get_text()) + "\n"
    
    # Extraire les valeurs ou la philosophie
    values_info = ""
    values_elements = soup.find_all(['div', 'section'], 
                                   class_=re.compile(r'(values|philosophy|approach)'))
    if values_elements:
        for element in values_elements:
            values_info += clean_text(element.get_text()) + "\n"
    
    # Compiler les informations
    if institution_name:
        establishment_info += f"Institution: {institution_name}\n\n"
    if mission_info:
        establishment_info += f"Mission:\n{mission_info}\n"
    if values_info:
        establishment_info += f"Values and Approach:\n{values_info}\n"
    
    return establishment_info

def scrape_parcoursup(url: str) -> str:
    """
    Fonction principale pour scraper les informations de Parcoursup
    """
    if not url or "parcoursup" not in url.lower():
        # Si l'URL n'est pas valide ou ne contient pas parcoursup, simuler des données
        return """Program: (URL invalide ou non-Parcoursup - Données simulées)
        
Les informations spécifiques sur le programme n'ont pas pu être extraites.
Pour une lettre de motivation plus précise, veuillez fournir une URL Parcoursup valide.
        
La lettre de motivation sera générée avec des informations génériques."""
    
    html_content = fetch_url_content(url)
    if not html_content:
        return "Impossible d'accéder à l'URL Parcoursup. Veuillez vérifier l'URL et réessayer."
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extraire les informations de base
    title = extract_title(soup)
    description = extract_meta_description(soup)
    
    # Extraire les informations spécifiques à Parcoursup
    parcoursup_specific = extract_parcoursup_specific(soup)
    
    # Extraire le contenu principal
    main_content = extract_main_content(soup)
    
    # Compiler toutes les informations
    result = f"Title: {title}\n\n"
    if parcoursup_specific:
        result += parcoursup_specific
    else:
        result += f"Description: {description}\n\n"
    
    # Ajouter le contenu principal si les informations spécifiques sont limitées
    if len(parcoursup_specific) < 200 and main_content:
        result += f"Additional Information:\n{main_content[:1000]}...\n"
    
    return result

def scrape_etablissement(url: str) -> str:
    """
    Fonction principale pour scraper les informations de l'établissement
    """
    if not url:
        # Si l'URL n'est pas valide, simuler des données
        return """Institution: (URL invalide - Données simulées)
        
Les informations spécifiques sur l'établissement n'ont pas pu être extraites.
Pour une lettre de motivation plus précise, veuillez fournir une URL valide.
        
La lettre de motivation sera générée avec des informations génériques."""
    
    html_content = fetch_url_content(url)
    if not html_content:
        return "Impossible d'accéder à l'URL de l'établissement. Veuillez vérifier l'URL et réessayer."
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extraire les informations de base
    title = extract_title(soup)
    description = extract_meta_description(soup)
    
    # Extraire les informations spécifiques à l'établissement
    establishment_specific = extract_establishment_specific(soup)
    
    # Extraire le contenu principal
    main_content = extract_main_content(soup)
    
    # Compiler toutes les informations
    result = f"Title: {title}\n\n"
    if establishment_specific:
        result += establishment_specific
    else:
        result += f"Description: {description}\n\n"
    
    # Ajouter le contenu principal si les informations spécifiques sont limitées
    if len(establishment_specific) < 200 and main_content:
        result += f"Additional Information:\n{main_content[:1000]}...\n"
    
    return result
