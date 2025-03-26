#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}============================================${NC}"
echo -e "${YELLOW}Motivation Letter Generator - Cleanup Tool${NC}"
echo -e "${YELLOW}============================================${NC}"

# Create backup directory
BACKUP_DIR="./backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo -e "${GREEN}Created backup directory: $BACKUP_DIR${NC}"

# Function to safely move files to backup
backup_file() {
    if [ -f "$1" ]; then
        echo -e "Moving $1 to backup..."
        mv "$1" "$BACKUP_DIR/"
    fi
}

# Function to safely remove files (with confirmation)
remove_file() {
    if [ -f "$1" ]; then
        echo -e "${YELLOW}Removing $1...${NC}"
        rm "$1"
        echo -e "${GREEN}✓ Removed $1${NC}"
    fi
}

echo -e "\n${YELLOW}Files identified for backup/removal:${NC}"
echo "1. test_gemini.py - Test file, not needed for operation"
echo "2. lettre.txt, testprout.txt - Generated output files"
echo "3. agents.py - Part of CrewAI approach, not used in direct mode"
echo "4. tasks.py - Part of CrewAI approach, not used in direct mode"

echo -e "\n${YELLOW}Would you like to back up these files before removal? (y/n)${NC}"
read backup_choice

if [[ $backup_choice == "y" || $backup_choice == "Y" ]]; then
    # Backup files
    backup_file "test_gemini.py"
    backup_file "lettre.txt"
    backup_file "testprout.txt"
    backup_file "agents.py"
    backup_file "tasks.py"
    echo -e "${GREEN}✓ Files backed up to $BACKUP_DIR${NC}"
else
    # Remove files directly
    remove_file "test_gemini.py"
    remove_file "lettre.txt"
    remove_file "testprout.txt"
    remove_file "agents.py"
    remove_file "tasks.py"
fi

# Update main.py to use only direct approach
echo -e "\n${YELLOW}Simplifying main.py to use only direct approach...${NC}"

cat > main.py << 'EOF'
#!/usr/bin/env python3
"""
Motivation Letter Generator - Main entry point
This script redirects to the launcher for backward compatibility.
"""
import sys
import os
from textwrap import dedent

try:
    from launcher import main as launcher_main
    
    if __name__ == "__main__":
        sys.exit(launcher_main())
except ImportError as e:
    print(f"\n❌ ERROR: {e}")
    print("Please install all dependencies using one of the following commands:")
    print("    pip install -r requirements.txt")
    print("    or")
    print("    poetry install\n")
    sys.exit(1)
EOF

# Update launcher.py to ensure it has a main function for import
echo -e "${YELLOW}Updating launcher.py to ensure it can be imported...${NC}"

# Create a temporary file
cat > launcher.py.new << 'EOF'
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
except ImportError:
    print("\n❌ ERROR: The 'decouple' module is not installed.")
    print("Please install it using one of the following commands:")
    print("    pip install python-decouple")
    print("    poetry add python-decouple\n")
    sys.exit(1)

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

    print("Pour commencer, nous avons besoin d'informations sur votre candidature.")
    print("-------------------------------")
    parcoursup_url = input(dedent("""URL Parcoursup du programme: """))
    etablissement_url = input(dedent("""URL du site web de l'établissement: """))

    # Exécuter directement l'approche qui fonctionne
    try:
        from direct_approach import run_direct_approach
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
EOF

# Replace the old file with the new one
mv launcher.py.new launcher.py
chmod +x launcher.py
chmod +x main.py

echo -e "\n${GREEN}✓ Updated main.py and launcher.py${NC}"

# Make scripts executable
chmod +x cleanup.sh
chmod +x run.sh
chmod +x install.sh

echo -e "\n${GREEN}✓ Made all scripts executable${NC}"
echo -e "\n${GREEN}Cleanup completed successfully!${NC}"
echo -e "${YELLOW}To run the application, use: ./run.sh or python launcher.py${NC}"
