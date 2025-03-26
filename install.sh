#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}============================================${NC}"
echo -e "${YELLOW}Motivation Letter Generator Setup${NC}"
echo -e "${YELLOW}============================================${NC}"

# Check if Python 3.11+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [[ -z "$python_version" ]]; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.11 or higher.${NC}"
    exit 1
fi

major=$(echo $python_version | cut -d. -f1)
minor=$(echo $python_version | cut -d. -f2)

if [[ $major -lt 3 || ($major -eq 3 && $minor -lt 11) ]]; then
    echo -e "${RED}Python 3.11 or higher is required. You have $python_version.${NC}"
    exit 1
fi

echo -e "${GREEN}Python $python_version detected.${NC}"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}Poetry is not installed. Would you like to install it? (y/n)${NC}"
    read answer
    if [[ $answer == "y" || $answer == "Y" ]]; then
        echo -e "${YELLOW}Installing Poetry...${NC}"
        curl -sSL https://install.python-poetry.org | python3 -
        echo -e "${GREEN}Poetry installed successfully!${NC}"
    else
        echo -e "${RED}Poetry is required to run this application.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Poetry is already installed.${NC}"
fi

# Create .env file
echo -e "${YELLOW}Creating .env file...${NC}"
if [ -f .env ]; then
    echo -e "${YELLOW}.env file already exists. Would you like to overwrite it? (y/n)${NC}"
    read answer
    if [[ $answer != "y" && $answer != "Y" ]]; then
        echo -e "${GREEN}Keeping existing .env file.${NC}"
    else
        read -p "Please enter your Google API Key: " api_key
        echo "GOOGLE_API_KEY=$api_key" > .env
        echo -e "${GREEN}.env file created!${NC}"
    fi
else
    read -p "Please enter your Google API Key: " api_key
    echo "GOOGLE_API_KEY=$api_key" > .env
    echo -e "${GREEN}.env file created!${NC}"
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
poetry install

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${YELLOW}To run the application, use: ./run.sh or 'poetry run python launcher.py'${NC}"

# Make the run script executable
chmod +x run.sh
echo -e "${GREEN}Setup completed successfully!${NC}"
