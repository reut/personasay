# Secrets & API Keys Management Guide

This guide explains where to add secrets and API keys for different deployment scenarios.

## Required Secrets

| Secret | Required? | Purpose |
|--------|-----------|---------|
| `OPENAI_API_KEY` | Yes | OpenAI API access for LangChain |
| `SECRET_KEY` | Production | Session encryption (auto-generated for dev) |
| `DATABASE_URL` | Optional | PostgreSQL connection (SQLite default) |
| `REDIS_URL` | Optional | Session storage and caching |

---

## Local Development (Easiest)

### Setup Steps:

```bash
# 1. Run automated setup
./setup.sh

# 2. Add your OpenAI API key
nano backend/.env

# Or use echo
echo "OPENAI_API_KEY=sk-your-actual-key-here" >> backend/.env

# 3. (Optional) Add other secrets
nano backend/.env
```

### File Location: `backend/.env`

**Minimum configuration:**
```bash
# Required
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Optional (has safe defaults)
ENVIRONMENT=development
DEBUG=false
DATABASE_URL=sqlite:///./data/personasay.db
SECRET_KEY=dev-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Full configuration example:**
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///./data/personasay.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/personasay

# Redis (optional - for session storage)
REDIS_URL=redis://localhost:6379

# Application Configuration
ENVIRONMENT=development
DEBUG=false
HOST=0.0.0.0
PORT=8001

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true

# Security (auto-generated for dev)
SECRET_KEY=dev-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Start Development:

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate # Activate virtual environment
python main.py
# Or use make command:
make dev-backend

# Terminal 2: Frontend
cd frontend
npm run dev
# Or use make command:
make dev-frontend

# Open http://localhost:5173
```

---

## Docker Compose (Recommended for Testing)

### Setup Steps:

```bash
# 1. Create .env file in project root
nano .env

# Or copy from example
cp backend/config/config.env.example .env

# 2. Edit with your values
nano .env

# 3. Start services
docker compose up -d
```

### File Location: `.env` (project root)

**Example:**
```bash
# Required
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Environment
ENVIRONMENT=production
DEBUG=false

# Database (included in docker compose)
DATABASE_URL=sqlite:///./data/personasay.db

# Security
SECRET_KEY=your-random-secret-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Logging
LOG_LEVEL=WARNING
LOG_TO_FILE=true
```

### Generate Secure Secret Key:

```bash
# Option 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: OpenSSL
openssl rand -base64 32
```

---

## Kubernetes/Helm (Production)

### NEVER commit secrets to Git!

### Option A: Kubernetes Secrets (Recommended)

```bash
# 1. Create namespace
kubectl create namespace personasay

# 2. Create secret
kubectl create secret generic personasay-secrets \
 --from-literal=openai-api-key='sk-your-actual-key-here' \
 --from-literal=secret-key='your-random-secret-key' \
 -n personasay

# 3. Deploy with Helm (references the secret)
helm install personasay ./helm/personasay \
 --namespace personasay \
 --values helm/personasay/values-production.yaml
```

**Update `values-production.yaml`:**
```yaml
global:
 env:
 # Reference secrets from Kubernetes Secret
 OPENAI_API_KEY: "" # Leave empty, will be injected
 SECRET_KEY: "" # Leave empty, will be injected
 
 # Non-secret config
 ENVIRONMENT: "production"
 DEBUG: "false"
 DATABASE_URL: "postgresql://personasay:password@postgresql:5432/personasay"
```

### Option B: Helm Values Override (Less Secure)

```bash
# Pass secrets via command line (not stored in files)
helm install personasay ./helm/personasay \
 --namespace personasay \
 --values helm/personasay/values-production.yaml \
 --set global.env.OPENAI_API_KEY='sk-your-key' \
 --set global.env.SECRET_KEY='your-secret'
```

### Option C: External Secrets Operator (Best for Production)

Use tools like:
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager
- HashiCorp Vault

---

## GitHub Actions CI/CD

### Setup Steps:

1. **Go to GitHub Repository**
2. **Settings → Secrets and variables → Actions**
3. **Click "New repository secret"**
4. **Add secrets:**

| Secret Name | Value | Required |
|-------------|-------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | No (tests work without it) |
| `SECRET_KEY` | Random secret for production | No (CI uses test values) |
| `CODECOV_TOKEN` | For coverage reports | No (optional) |

**Note:** Current CI workflows use test/mock values, so secrets are optional for CI. Add them only if you want to test with real API calls.

---

## Security Best Practices

### DO:
- Use `.env` files for local development
- Add `.env` to `.gitignore` (already done)
- Use Kubernetes Secrets for production
- Rotate API keys regularly
- Use different keys for dev/staging/prod
- Generate strong random SECRET_KEY for production
- Use environment-specific CORS_ORIGINS

### DON'T:
- Commit `.env` files to Git
- Share API keys in chat/email
- Use production keys in development
- Hardcode secrets in source code
- Use default SECRET_KEY in production
- Allow `CORS_ORIGINS=*` in production

---

## Verify Your Setup

### Check Backend Configuration:

```bash
# Local development
cd backend
source venv/bin/activate
python -c "from app.models import AppSettings; s = AppSettings(); print(f'Environment: {s.environment}'); print(f'Debug: {s.debug}')"
```

### Check Environment Variables:

```bash
# Show loaded config (without revealing secrets)
curl http://localhost:8001/health
```

### Test API Connection:

```bash
# Test backend is running
curl http://localhost:8001/health

# Test with actual API call (requires OPENAI_API_KEY)
curl -X POST http://localhost:8001/langchain/initialize \
 -H "Content-Type: application/json" \
 -d '{"personas": [{"id": "test", "name": "Test"}]}'
```

---

## Troubleshooting

### "OpenAI API key not found"
```bash
# Check if key is set
cat backend/.env | grep OPENAI_API_KEY
# Should show: OPENAI_API_KEY=sk-...

# Verify backend is reading it
cd backend
source venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Key loaded:', bool(os.getenv('OPENAI_API_KEY')))"
```

### "Permission denied" on setup.sh
```bash
chmod +x setup.sh
./setup.sh
```

### "Module not found" errors
```bash
# Reinstall dependencies
cd backend
source venv/bin/activate
pip install -r config/requirements.txt -r config/requirements-dev.txt
```

### Environment not loading in Docker
```bash
# Check .env file exists in project root
ls -la .env

# Check docker compose is reading it
docker compose config | grep OPENAI_API_KEY
```

---

## Additional Resources

- [Python-dotenv Documentation](https://github.com/thecdp/python-dotenv)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [Generating Secure Keys](https://docs.python.org/3/library/secrets.html)

---

## Quick Reference

| Scenario | File Location | Command |
|----------|---------------|---------|
| **Local Dev** | `backend/.env` | `nano backend/.env` |
| **Docker Compose** | `.env` (root) | `nano .env` |
| **Kubernetes** | Kubernetes Secret | `kubectl create secret` |
| **CI/CD** | GitHub Secrets | Settings → Secrets → Actions |

---

**Remember:** Never commit secrets to Git! Always use `.env` files (which are gitignored) or secret management systems.

