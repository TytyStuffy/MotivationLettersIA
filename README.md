## agents.py
This file contains the definition of custom agents.
To create a Agent, you need to define the following:
1. Role: The role of the agent.
2. Backstory: The backstory of the agent.
3. Goal: The goal of the agent.
4. Tools: The tools that the agent has access to (optional).
5. Allow Delegation: Whether the agent can delegate tasks to other agents(optional).

    [More Details about Agent](https://docs.crewai.com/concepts/agents).

## task.py
This file contains the definition of custom tasks.
To Create a task, you need to define the following :
1. description: A string that describes the task.
2. agent: An agent object that will be assigned to the task.
3. expected_output: The expected output of the task.

    [More Details about Task](https://docs.crewai.com/concepts/tasks).

## crew (main.py)
This is the main file that you will use to run your custom crew.
To create a Crew , you need to define Agent ,Task and following Parameters:
1. Agent: List of agents that you want to include in the crew.
2. Task: List of tasks that you want to include in the crew.
3. verbose: If True, print the output of each task.(default is False).
4. debug: If True, print the debug logs.(default is False).

    [More Details about Crew](https://docs.crewai.com/concepts/crew).

## Project Setup with Poetry

This project uses Poetry for dependency management. To set up:

1. **Install Poetry**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**
   ```bash
   cd /path/to/project
   poetry install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the project**
   ```bash
   poetry run python main.py
   ```

## Project Structure

```
.
├── README.md
├── pyproject.toml  # Poetry configuration
├── .env            # Environment variables (not in git)
├── .gitignore
├── main.py         # Main application entry point
├── agents.py       # Agent definitions
├── tasks.py        # Task definitions
└── tools/          # Custom tools directory
    └── scraping_tools.py  # Web scraping tools

# Générateur de Lettres de Motivation pour Parcoursup

## Vue d'ensemble

Ce projet offre un système d'aide à la rédaction de lettres de motivation personnalisées pour Parcoursup, utilisant l'IA générative (Google Gemini API).

### Fonctionnalités
- Récupération automatique d'informations depuis Parcoursup
- Analyse des sites des établissements
- Entretien guidé pour recueillir votre profil
- Génération de deux versions de lettres de motivation (formelle et créative)
- Fusion intelligente des versions pour une lettre optimale

## Installation

Plusieurs options s'offrent à vous pour installer le projet :

### 1. Installation automatisée (recommandée)
```bash
# Rendre le script exécutable
chmod +x install.sh
# Lancer l'installation
./install.sh
```

### 2. Installation manuelle
```bash
# Installer les dépendances avec Poetry
poetry install

# OU installer les dépendances avec pip
pip install -r requirements.txt
```

## Utilisation

Pour lancer l'application, vous pouvez utiliser l'une des méthodes suivantes :

```bash
# Méthode 1 (recommandée si vous utilisez Poetry)
./run.sh

# Méthode 2
poetry run python launcher.py

# Méthode 3 (si vous n'utilisez pas Poetry)
python launcher.py
```

L'application vous demandera :
1. L'URL de la formation Parcoursup
2. L'URL du site de l'établissement
3. Des informations sur votre profil (ou vous proposera d'utiliser des réponses prédéfinies)

À la fin, une lettre de motivation personnalisée sera générée et pourra être sauvegardée.

## Configuration

Assurez-vous que votre fichier `.env` contient une clé API Google valide :