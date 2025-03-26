import os
import google.generativeai as genai
from decouple import config

def test_gemini_api():
    """Test simple pour vérifier que l'API Gemini fonctionne correctement"""
    print("Test de connexion à l'API Gemini...")
    
    try:
        # Récupérer la clé API depuis .env
        api_key = config("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Clé API Google non trouvée dans le fichier .env")
            
        print(f"Clé API trouvée (premiers caractères: {api_key[:5]}...)")
        
        # Configurer Gemini avec la clé API
        genai.configure(api_key=api_key)
        
        # Tester la génération de texte avec une simple requête
        model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')
        response = model.generate_content("Dis-moi bonjour en français.")
        
        print("\nRéponse du modèle:")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
        
        print("\n✅ Test réussi! La connexion à l'API Gemini fonctionne correctement.\n")
        
        # Test avec le modèle spécifié dans agents.py
        try:
            print("Test avec le modèle utilisé dans agents.py (gemini-2.0-pro-exp-02-05)...")
            advanced_model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')
            advanced_response = advanced_model.generate_content("Comment vas-tu aujourd'hui?")
            print("\nRéponse du modèle avancé:")
            print("-" * 40)
            print(advanced_response.text)
            print("-" * 40)
            print("\n✅ Test du modèle avancé réussi!\n")
        except Exception as e:
            print(f"\n❌ Erreur avec le modèle avancé: {str(e)}")
            print("Ce modèle spécifique peut ne pas être disponible pour votre compte.")
            print("Veuillez mettre à jour 'model_name' dans agents.py vers 'gemini-pro'.")
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {str(e)}")
        print("\nConseils de dépannage:")
        print("1. Vérifiez que votre clé API dans le fichier .env est correcte")
        print("2. Vérifiez votre connexion internet")
        print("3. Visitez https://ai.google.dev pour vérifier l'état du service")

if __name__ == "__main__":
    test_gemini_api()
