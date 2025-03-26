try:
    from crewai import Agent
    from textwrap import dedent
    from langchain.llms.base import LLM
    from langchain_community.tools import DuckDuckGoSearchRun
    from decouple import config
    import json
    import google.generativeai as genai
    from typing import Any, List, Optional, Dict, Mapping
    from pydantic import Field, BaseModel
    import os
    
    # Import des fonctions simples pour le scraping
    from tools.scraping_tools import scrape_parcoursup, scrape_etablissement
except ImportError as e:
    module_name = str(e).split("'")[-2]
    import sys
    print(f"\n❌ ERROR: The '{module_name}' module is not installed.")
    print("Please install all dependencies using one of the following commands:")
    print("    pip install -r requirements.txt")
    print("    or")
    print("    poetry install\n")
    sys.exit(1)

# Forcer l'utilisation de l'API directe et non Vertex AI
os.environ["GOOGLE_AUTH_NO_IMPLICIT"] = "true"
API_KEY = config("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# Définition d'une classe LLM personnalisée pour Gemini qui n'utilise pas LiteLLM
class GeminiLLM(LLM, BaseModel):
    model_name: str = Field("gemini-2.0-pro-exp-02-05")  # Utiliser gemini-2.0-pro-exp-02-05 qui est plus stable
    temperature: float = Field(0.7)
    api_key: Optional[str] = None
    
    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = self.api_key or API_KEY
        
    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        try:
            # Créer directement un modèle Gemini
            model = genai.GenerativeModel(self.model_name)
            
            # Générer du contenu avec la configuration spécifiée
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature
                )
            )
            
            # Retourner le texte généré
            return response.text
        except Exception as e:
            # Afficher une erreur détaillée pour faciliter le débogage
            print(f"Error with Gemini API: {str(e)}")
            # Retourner un message d'erreur au lieu de lever une exception
            return f"Une erreur s'est produite lors de la génération de texte: {str(e)}"
    
    @property
    def _llm_type(self) -> str:
        return "gemini"
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model_name": self.model_name, "temperature": self.temperature}


class CustomAgents:
    def __init__(self):
        # Initialiser les modèles Gemini avec la classe personnalisée
        self.GeminiPro = GeminiLLM(
            model_name="gemini-2.0-pro-exp-02-05",  # Utiliser gemini-2.0-pro-exp-02-05 standard
            temperature=0.7
        )
        
        self.GeminiProFactual = GeminiLLM(
            model_name="gemini-2.0-pro-exp-02-05",
            temperature=0.1
        )
        
        self.GeminiProCreative = GeminiLLM(
            model_name="gemini-2.0-pro-exp-02-05",
            temperature=0.9
        )
        
        # Initialiser le tool de recherche web
        self.search_tool = DuckDuckGoSearchRun()

    def agent_scraping_parcoursup(self):
        # Définition des outils en format de dictionnaire pour compatibilité
        parcoursup_tool = {
            "name": "parcoursup_scraper",
            "description": "Scrapes information from a Parcoursup page about an educational program. Input should be a URL.",
            "func": scrape_parcoursup
        }
        
        return Agent(
            role="Parcoursup Information Specialist",
            backstory=dedent(f"""You are an expert in extracting relevant information from Parcoursup,
            the French higher education application platform. You have deep knowledge of educational programs,
            admission requirements, and can identify key information that would be valuable for a motivation letter."""),
            goal=dedent(f"""Extract all relevant information about the educational program from the Parcoursup link,
            including program description, requirements, expected skills and qualities."""),
            tools=[parcoursup_tool],
            verbose=True,
            llm=self.GeminiProFactual,
        )

    def agent_scraping_etablissement(self):
        # Créer un agent sans outils pour commencer
        return Agent(
            role="Educational Institution Research Specialist",
            backstory=dedent(f"""You are a research specialist who excels at finding detailed information
            about educational institutions. You know how to navigate institution websites to extract program details,
            values, unique selling points and other relevant information."""),
            goal=dedent(f"""Find detailed and specific information about the educational program from the institution's
            website that would make a motivation letter more targeted and personalized."""),
            verbose=True,
            llm=self.GeminiProFactual,
        )
        
    def agent_interaction_utilisateur(self):
        return Agent(
            role="Student Profile Interviewer",
            backstory=dedent(f"""You are an empathetic interviewer specialized in helping students
            identify and articulate their strengths, motivations, and experiences. You know exactly what
            questions to ask to get information that would strengthen a motivation letter."""),
            goal=dedent(f"""Conduct a thorough Q&A session with the student to gather all personal information
            needed for a compelling motivation letter, including academic background, achievements, 
            motivations, career goals, and reasons for choosing this specific program."""),
            verbose=True,
            llm=self.GeminiPro,
        )
        
    def agent_generation_lettre1(self):
        return Agent(
            role="Academic Motivation Letter Specialist",
            backstory=dedent(f"""You are an academic writing expert who specializes in formal, 
            structured motivation letters. You excel at showcasing a student's qualifications
            and creating clear connections between their background and the program they're applying to."""),
            goal=dedent(f"""Create a professional, formal motivation letter that effectively highlights
            the student's academic achievements and demonstrates their fit with the program's requirements.
            The letter must be concise and not exceed 1500 characters."""),
            verbose=True,
            llm=self.GeminiPro,  # Using Gemini Pro for the first letter generation
        )
        
    def agent_generation_lettre2(self):
        return Agent(
            role="Creative Motivation Letter Writer",
            backstory=dedent(f"""You are a creative writer specialized in personal statements that stand out.
            You excel at storytelling, creating emotional connections, and showcasing personality while
            maintaining professionalism."""),
            goal=dedent(f"""Craft an engaging, memorable motivation letter that tells a compelling story
            about the student's journey, passion, and unique attributes that make them perfect for the program.
            The letter must be concise and not exceed 1500 characters."""),
            verbose=True,
            llm=self.GeminiProCreative,  # Using Gemini Pro with higher temperature for creativity
        )
        
    def agent_fusion_lettre(self):
        return Agent(
            role="Expert Letter Editor and Optimizer",
            backstory=dedent(f"""You are a senior admissions consultant who has helped thousands of students
            get accepted to their dream programs. You have an exceptional eye for effective motivation letters
            and can identify and combine the strongest elements from different drafts."""),
            goal=dedent(f"""Analyze both motivation letter versions, identify the strengths of each,
            and combine them into a single optimized letter that maximizes the student's chances of admission.
            The final letter must be concise and not exceed 1500 characters."""),
            verbose=True,
            llm=self.GeminiPro,
        )
