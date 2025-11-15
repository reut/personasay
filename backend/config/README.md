# Backend Configuration

This directory contains configuration files for the PersonaSay backend.

## Requirements Files

### `requirements.txt` - Production Dependencies 
**What it includes:**
- FastAPI, Uvicorn (web server)
- LangChain stack (AI agents)
- OpenAI client
- Database (SQLAlchemy, PostgreSQL)
- Redis, ChromaDB (optional storage)
- Utilities (dotenv, pydantic)

**Used in:**
- Production Docker images
- Kubernetes deployments
- Minimal production installs

**Install:**
```bash
pip install -r requirements.txt
```

### `requirements-dev.txt` - Development & Testing 
**What it includes:**
- All production dependencies (via `-r requirements.txt`)
- Testing: pytest, pytest-asyncio, pytest-cov, pytest-mock
- HTTP client: httpx (for TestClient)
- Code quality: flake8, black, mypy
- Development tools: ipython

**Used in:**
- Local development
- CI/CD testing
- Contributors

**Install:**
```bash
pip install -r requirements.txt -r requirements-dev.txt
# Or just:
pip install -r requirements-dev.txt # (includes requirements.txt)
```

### `config.env.example` - Environment Template
Template for environment variables. Copy to `.env` and customize.

## Installation Examples

### For Development (Local)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt -r config/requirements-dev.txt
```

### For Production (Docker)
```bash
# Dockerfile only installs requirements.txt
docker build -t personasay-backend .
```

### For Production (Manual)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt # Production only
```

## Why Split Requirements?

### Benefits

| Benefit | Description |
|---------|-------------|
| **Smaller production images** | No test packages = smaller Docker images |
| **Faster deployments** | Less to install = faster builds |
| **Better security** | Fewer packages = smaller attack surface |
| **Clearer intent** | Explicit separation of concerns |

### Size Comparison

- **requirements.txt only**: ~450MB
- **requirements.txt + requirements-dev.txt**: ~520MB
- **Savings in production**: ~70MB + faster installs

## File Structure

```
backend/config/
 requirements.txt # Production dependencies (32 packages)
 requirements-dev.txt # Dev/test dependencies (9 extra packages)
 config.env.example # Environment template
 README.md # This file
```

## Quick Reference

| Scenario | Command |
|----------|---------|
| **Development setup** | `pip install -r requirements-dev.txt` |
| **Production deploy** | `pip install -r requirements.txt` |
| **Run tests** | `pytest tests/` (needs requirements-dev.txt) |
| **Check code** | `flake8 app/` (needs requirements-dev.txt) |

---

**Note**: The `setup.sh` script automatically installs both files for development convenience.

