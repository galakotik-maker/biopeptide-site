#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Banner ---
echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}🛡️  Starting Setup for Legal Guard RegTech 🛡️ ${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo

# --- Step 1: Dependency Check ---
echo -e "${YELLOW}Step 1: Checking for required dependencies...${NC}"

# Function to check for a command
check_command() {
  if command -v $1 &> /dev/null; then
    echo -e "  [${GREEN}✅${NC}] $1 is installed."
  else
    echo -e "  [${RED}❌${NC}] $1 is not installed. Please install it before running this script."
    exit 1
  fi
}

check_command python3
check_command pip
check_command node
check_command npm
echo -e "${GREEN}All dependencies are satisfied.${NC}"
echo

# --- Step 2: Backend Setup ---
echo -e "${YELLOW}Step 2: Setting up Backend (Python/FastAPI)...${NC}"
cd backend

# Create a Python virtual environment
echo "  -> Creating Python virtual environment in 'venv'..."
python3 -m venv venv

# Activate virtual environment and install dependencies
echo "  -> Activating virtual environment and installing requirements..."
source venv/bin/activate
pip install --upgrade pip > /dev/null
pip install -r requirements.txt

# Deactivate after installation
deactivate

cd ..
echo -e "${GREEN}Backend setup complete.${NC}"
echo

# --- Step 3: Frontend Setup ---
echo -e "${YELLOW}Step 3: Setting up Frontend (React/TypeScript)...${NC}"
cd frontend

# Install npm packages
echo "  -> Installing npm dependencies with 'npm install'..."
npm install

cd ..
echo -e "${GREEN}Frontend setup complete.${NC}"
echo

# --- Final Instructions ---
echo -e "${BLUE}=====================================================${NC}"
echo -e "🎉  ${GREEN}Setup is Complete! You are ready to go!${NC} 🎉"
echo -e "${BLUE}=====================================================${NC}"
echo
echo -e "To run the application, you need to open ${YELLOW}TWO separate terminal windows${NC}."
echo
echo -e "In ${YELLOW}Terminal 1${NC}, run the Backend by typing these commands:"
echo -e "  1. ${GREEN}cd backend${NC}"
echo -e "  2. ${GREEN}source venv/bin/activate${NC}"
echo -e "  3. ${GREEN}uvicorn main:app --reload --port 8000${NC}"
echo
echo -e "In ${YELLOW}Terminal 2${NC}, run the Frontend by typing these commands:"
echo -e "  1. ${GREEN}cd frontend${NC}"
echo -e "  2. ${GREEN}npm run dev${NC}"
echo
echo -e "Once both servers are running:"
echo -e "  - Access the Web Application at: ${YELLOW}http://localhost:5173${NC}"
echo -e "  - Access the API Docs at:        ${YELLOW}http://localhost:8000/docs${NC}"
echo