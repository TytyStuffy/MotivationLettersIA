#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}============================================${NC}"
echo -e "${YELLOW}Générateur de Lettres de Motivation Launcher${NC}"
echo -e "${YELLOW}============================================${NC}"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Poetry is not installed. Please install it first:${NC}"
    echo "curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    read -p "Please enter your Google API Key: " api_key
    echo "GOOGLE_API_KEY=$api_key" > .env
    echo -e "${GREEN}.env file created!${NC}"
fi

# Install dependencies if not already installed
echo -e "${YELLOW}Checking and installing dependencies...${NC}"
poetry install

# Run the dependency checker
echo -e "${YELLOW}Running dependency check...${NC}"
poetry run python check_dependencies.py

# Check the result of dependency check
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Would you like to continue anyway? (y/n)${NC}"
    read answer
    if [[ $answer != "y" && $answer != "Y" ]]; then
        echo -e "${RED}Exiting...${NC}"
        exit 1
    fi
fi

# Run the application
echo -e "${GREEN}Starting the application...${NC}"
poetry run python launcher.py
