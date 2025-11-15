# PersonaSay - Development Makefile
# Quick commands for common tasks

.PHONY: help setup dev dev-backend dev-frontend clean test docker-build docker-up docker-down

# Default target
help:
	@echo "PersonaSay - Available Commands:"
	@echo ""
	@echo "  make setup          - Initial project setup (run once)"
	@echo "  make dev            - Start both backend and frontend"
	@echo "  make dev-backend    - Start backend only"
	@echo "  make dev-frontend   - Start frontend only"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make docker-build   - Build Docker images"
	@echo "  make docker-up      - Start with Docker Compose"
	@echo "  make docker-down    - Stop Docker Compose"
	@echo ""

# Setup project (run once)
setup:
	@chmod +x setup.sh
	@./setup.sh

# Start both services (requires two terminals or tmux)
dev:
	@echo "Starting PersonaSay in development mode..."
	@echo "Backend: http://localhost:8001"
	@echo "Frontend: http://localhost:5173"
	@echo ""
	@echo "⚠️  This requires two terminals:"
	@echo "Terminal 1: make dev-backend"
	@echo "Terminal 2: make dev-frontend"
	@echo ""
	@echo "Or use Docker: make docker-up"

# Start backend
dev-backend:
	@echo "Starting backend server..."
	@cd backend && source venv/bin/activate && python main.py

# Start frontend
dev-frontend:
	@echo "Starting frontend dev server..."
	@cd frontend && npm run dev

# Run tests
test:
	@echo "Running backend tests..."
	@cd backend && source venv/bin/activate && pytest tests/ -v
	@echo ""
	@echo "Running frontend type checks..."
	@cd frontend && npm run type-check

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf backend/htmlcov backend/.pytest_cache
	@rm -rf frontend/dist frontend/.vite
	@echo "✓ Cleaned"

# Docker commands
docker-build:
	@echo "Building Docker images..."
	@docker compose build

docker-up:
	@echo "Starting with Docker Compose..."
	@docker compose up -d
	@echo ""
	@echo "✓ Services started!"
	@echo "Frontend: http://localhost"
	@echo "Backend: http://localhost/api"
	@echo ""
	@echo "View logs: docker compose logs -f"

docker-down:
	@echo "Stopping Docker services..."
	@docker compose down

# Quick start (setup + run)
quickstart: setup
	@echo ""
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Now run: make docker-up"
	@echo "Or start manually:"
	@echo "  Terminal 1: make dev-backend"
	@echo "  Terminal 2: make dev-frontend"
