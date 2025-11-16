# PersonaSay - Unified Development Makefile
# Comprehensive commands for development, testing, and deployment

.PHONY: help setup dev dev-backend dev-frontend test test-backend test-frontend \
        format lint check clean clean-all docker-build docker-up docker-down quickstart

# ============================================================================
# HELP - Default target
# ============================================================================

help:
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║              PersonaSay - Development Commands                 ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📦 SETUP & INSTALLATION"
	@echo "  make setup          - Initial project setup (run once)"
	@echo "  make quickstart     - Setup + start with Docker"
	@echo ""
	@echo "🚀 DEVELOPMENT"
	@echo "  make dev            - Instructions for starting both services"
	@echo "  make dev-backend    - Start backend server (port 8000)"
	@echo "  make dev-frontend   - Start frontend dev server (port 5173)"
	@echo ""
	@echo "🧪 TESTING"
	@echo "  make test           - Run all tests (backend + frontend)"
	@echo "  make test-backend   - Run backend tests only"
	@echo "  make test-frontend  - Run frontend type checks"
	@echo ""
	@echo "🎨 CODE QUALITY (Backend)"
	@echo "  make format         - Format code with black and isort"
	@echo "  make lint           - Run all linters (flake8, pylint, mypy)"
	@echo "  make check          - Check formatting without changes"
	@echo ""
	@echo "🧹 CLEANUP"
	@echo "  make clean          - Clean Python cache and build artifacts"
	@echo "  make clean-all      - Deep clean (cache + node_modules + venv)"
	@echo ""
	@echo "🐳 DOCKER"
	@echo "  make docker-build   - Build Docker images"
	@echo "  make docker-up      - Start with Docker Compose"
	@echo "  make docker-down    - Stop Docker Compose"
	@echo ""

# ============================================================================
# SETUP & INSTALLATION
# ============================================================================

setup:
	@echo "🔧 Setting up PersonaSay..."
	@chmod +x setup.sh
	@./setup.sh
	@echo ""
	@echo "✅ Setup complete!"
	@echo "📝 Next: Edit backend/.env and add your OPENAI_API_KEY"

quickstart: setup
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "🚀 Starting with Docker Compose..."
	@echo "   Make sure you've added OPENAI_API_KEY to your environment"
	@echo ""
	@echo "Now run: make docker-up"
	@echo ""
	@echo "Or start manually:"
	@echo "  Terminal 1: make dev-backend"
	@echo "  Terminal 2: make dev-frontend"

# ============================================================================
# DEVELOPMENT SERVERS
# ============================================================================

dev:
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║           Starting PersonaSay in Development Mode              ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🔧 Backend:  http://localhost:8000"
	@echo "🎨 Frontend: http://localhost:5173"
	@echo ""
	@echo "⚠️  This requires TWO separate terminals:"
	@echo ""
	@echo "   Terminal 1: make dev-backend"
	@echo "   Terminal 2: make dev-frontend"
	@echo ""
	@echo "💡 Or use Docker: make docker-up"
	@echo ""

dev-backend:
	@echo "🚀 Starting backend server..."
	@cd backend && source venv/bin/activate && python main.py

dev-frontend:
	@echo "🎨 Starting frontend dev server..."
	@cd frontend && npm run dev

# ============================================================================
# TESTING
# ============================================================================

test: test-backend test-frontend
	@echo ""
	@echo "✅ All tests complete!"

test-backend:
	@echo "🧪 Running backend tests..."
	@cd backend && source venv/bin/activate && pytest tests/ -v

test-frontend:
	@echo "🔍 Running frontend type checks..."
	@cd frontend && npm run type-check

# ============================================================================
# CODE QUALITY (Backend)
# ============================================================================

format:
	@echo "🎨 Formatting backend code..."
	@cd backend && source venv/bin/activate && black app/ tests/ services/
	@echo ""
	@echo "📦 Sorting imports..."
	@cd backend && source venv/bin/activate && isort app/ tests/ services/
	@echo ""
	@echo "✅ Code formatting complete!"

lint:
	@echo "🔍 Running linters on backend..."
	@echo ""
	@echo "→ flake8..."
	@cd backend && source venv/bin/activate && flake8 app/ tests/ services/ || true
	@echo ""
	@echo "→ pylint..."
	@cd backend && source venv/bin/activate && pylint app/ || true
	@echo ""
	@echo "→ mypy..."
	@cd backend && source venv/bin/activate && mypy app/ || true
	@echo ""
	@echo "✅ Linting complete!"

check:
	@echo "🔍 Checking code formatting (no changes)..."
	@cd backend && source venv/bin/activate && black --check app/ tests/ services/
	@echo ""
	@cd backend && source venv/bin/activate && isort --check-only app/ tests/ services/
	@echo ""
	@echo "✅ Code format check complete!"

# ============================================================================
# CLEANUP
# ============================================================================

clean:
	@echo "🧹 Cleaning build artifacts and cache..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf backend/htmlcov backend/.coverage
	@rm -rf frontend/dist frontend/.vite
	@echo "✅ Cleaned!"

clean-all: clean
	@echo "🧹 Deep cleaning (removing node_modules and venv)..."
	@rm -rf frontend/node_modules
	@rm -rf backend/venv
	@echo "⚠️  You'll need to run 'make setup' again after this"
	@echo "✅ Deep clean complete!"

# ============================================================================
# DOCKER COMMANDS
# ============================================================================

docker-build:
	@echo "🐳 Building Docker images..."
	@docker compose build
	@echo "✅ Docker images built!"

docker-up:
	@echo "🐳 Starting PersonaSay with Docker Compose..."
	@docker compose up -d
	@echo ""
	@echo "✅ Services started!"
	@echo "   Frontend: http://localhost"
	@echo "   Backend:  http://localhost/api"
	@echo ""
	@echo "📊 View logs:  docker compose logs -f"
	@echo "🛑 Stop:       make docker-down"

docker-down:
	@echo "🛑 Stopping Docker services..."
	@docker compose down
	@echo "✅ Services stopped!"

# ============================================================================
# UTILITY COMMANDS
# ============================================================================

.SILENT: help setup dev dev-backend dev-frontend test test-backend test-frontend \
         format lint check clean clean-all docker-build docker-up docker-down quickstart
