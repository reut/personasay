#!/bin/bash
# PersonaSay Quick Setup Script
# Makes local development setup effortless

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   PersonaSay - Quick Setup Script     ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo ""

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found. Please install npm${NC}"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓${NC} npm $NPM_VERSION"

echo ""

# Setup Backend
echo -e "${BLUE}🔧 Setting up Backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r config/requirements.txt -r config/requirements-dev.txt
echo -e "${GREEN}✓${NC} Python dependencies installed (production + dev)"

# Setup environment file
if [ ! -f ".env" ]; then
    cp config/config.env.example .env
    echo -e "${GREEN}✓${NC} Created .env file from template"
    echo -e "${YELLOW}⚠️  Please edit backend/.env and add your OPENAI_API_KEY${NC}"
else
    echo -e "${GREEN}✓${NC} .env file already exists"
fi

# Create data directory
mkdir -p data
echo -e "${GREEN}✓${NC} Data directory ready"

# Create logs directory
mkdir -p logs
echo -e "${GREEN}✓${NC} Logs directory ready"

cd ..
echo ""

# Setup Frontend
echo -e "${BLUE}🎨 Setting up Frontend...${NC}"
cd frontend

# Install npm dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
    echo -e "${GREEN}✓${NC} npm dependencies installed"
else
    echo -e "${GREEN}✓${NC} npm dependencies already installed"
fi

cd ..
echo ""

# Final instructions
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        Setup Complete! 🎉              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo -e "1. ${YELLOW}Add your OpenAI API key:${NC}"
echo "   nano backend/.env"
echo "   (Set OPENAI_API_KEY=sk-your-key-here)"
echo ""
echo -e "2. ${YELLOW}Start the backend:${NC}"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo -e "3. ${YELLOW}Start the frontend (in a new terminal):${NC}"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo -e "4. ${YELLOW}Open your browser:${NC}"
echo "   http://localhost:5173"
echo ""
echo -e "${BLUE}💡 Tip: Use 'make dev' for a single command to start both services!${NC}"
echo ""

