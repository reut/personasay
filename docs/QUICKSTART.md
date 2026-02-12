# PersonaSay Quick Start Guide

Get PersonaSay running in under 5 minutes!

## Choose Your Deployment Method

### Local Development (Fastest for Testing)

#### Option A: Automated Setup (Recommended)

Use the provided setup script for automatic installation:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/personasay.git
cd personasay

# 2. Run the setup script
./setup.sh

# 3. Edit backend/.env and add your OpenAI API key
nano backend/.env
# Set: OPENAI_API_KEY=sk-your-key-here

# 4. Run (keep both terminals open)
# Terminal 1 - Backend:
cd backend && source venv/bin/activate && python main.py

# Terminal 2 - Frontend:
cd frontend && npm run dev

# 5. Open browser
# Visit: http://localhost:5173
```

**Time to run**: ~2 minutes (automated setup)

#### Option B: Manual Setup

If you prefer manual control or the script doesn't work on your system:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/personasay.git
cd personasay

# 2. Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r config/requirements.txt
cp config/config.env.example .env
# Edit .env and add your OPENAI_API_KEY

# Initialize database (optional - will auto-create if skipped)
python init_db.py

# 3. Setup frontend (in new terminal)
cd frontend
npm install

# 4. Run (keep both terminals open)
# Terminal 1 - Backend:
cd backend && source venv/bin/activate && python main.py

# Terminal 2 - Frontend:
cd frontend && npm run dev

# 5. Open browser
# Visit: http://localhost:5173
```

**Time to run**: ~3 minutes

---

### Docker Compose (Easiest for Quick Demo)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/personasay.git
cd personasay

# 2. Set your OpenAI API key
export OPENAI_API_KEY="sk-your-api-key-here"

# 3. Start everything
docker compose up -d

# 4. Open browser
# Visit: http://localhost

# View logs
docker compose logs -f

# Stop when done
docker compose down
```

> **Note**: If you have an older Docker version, use `docker-compose` (with hyphen) instead of `docker compose`.

**Time to run**: ~2 minutes (after initial build)

---

### Kubernetes (Production Ready)

```bash
# 1. Build and push Docker images
cd personasay

# Build
docker build -t your-registry.com/personasay/backend:1.0.0 ./backend
docker build -t your-registry.com/personasay/frontend:1.0.0 ./frontend

# Push to your registry
docker push your-registry.com/personasay/backend:1.0.0
docker push your-registry.com/personasay/frontend:1.0.0

# 2. Install with Helm
helm install personasay ./helm/personasay \
  --namespace personasay \
  --create-namespace \
  --set global.env.OPENAI_API_KEY="sk-your-api-key" \
  --set backend.image.repository="your-registry.com/personasay/backend" \
  --set frontend.image.repository="your-registry.com/personasay/frontend"

# 3. Check status
kubectl get pods -n personasay

# 4. Access application
kubectl port-forward -n personasay svc/personasay-frontend 8080:80
# Visit: http://localhost:8080

# Or configure ingress for public access
helm upgrade personasay ./helm/personasay \
  --namespace personasay \
  -f helm/personasay/values-production.yaml
```

**Time to deploy**: ~5 minutes

---

## Using PersonaSay

### Basic Usage

1. **Select Personas**: Click on persona cards to select them (they'll highlight)
2. **Ask a Question**: Type in the text box and click send
3. **View Responses**: Each selected persona responds based on their role
4. **Generate Summary**: Click "Generate Summary" for AI-powered insights

### Advanced Features

**@Mentions**: Target specific personas
```
@alex what do you think about real-time alerts?
```
Only Alex will respond, regardless of selection.

**File Attachments**: Upload images/documents
1. Click paperclip icon
2. Select file (PNG, JPG, PDF, DOCX, etc.)
3. Type your question
4. Send

**Visual Mocks**: Request SVG mockups
1. Click magic wand icon (toggle ON)
2. Ask for a design: "Create a mock for the provider dashboard"
3. Personas may include visual mockups
4. Click expand icon to view full-screen

**Export Summary**: Download insights as Word document
1. Generate a summary
2. Click "Export Summary"
3. Opens as .docx file

---

## Configuration Options

### Essential Configuration Files

PersonaSay requires two configuration files that are **gitignored** (not in version control):

#### 1. Environment Variables (`backend/.env`)

Contains API keys and secrets:

```bash
# Copy template
cp backend/config/config.env.example backend/.env

# Edit and add your OpenAI key
nano backend/.env
```

Required settings:
```bash
OPENAI_API_KEY=sk-your-key-here
PORT=8001
HOST=127.0.0.1
DEBUG=true
```

#### 2. Product Configuration (`backend/config/product_config.py`)

Defines your product context for AI personas:

```bash
# Copy template
cp backend/config/product_config.py.example backend/config/product_config.py

# Customize with your product details
nano backend/config/product_config.py
```

**What to customize:**
- Product name, tagline, industry
- Target users and key features
- Pain points and value proposition
- Mock generation context

See [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) for detailed instructions.

---

### Local Development

Edit `backend/.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
PORT=8001
HOST=127.0.0.1
DEBUG=true
```

### Docker Compose

Set environment variables:
```bash
export OPENAI_API_KEY="sk-your-key"
export DEBUG="false"
docker compose up -d
```

### Kubernetes/Helm

Override values with `--set` or values file:
```bash
# Individual overrides
helm install personasay ./helm/personasay \
  --set global.env.OPENAI_API_KEY="sk-key" \
  --set global.env.DEBUG="false" \
  --set backend.replicaCount=3

# Or use values file
helm install personasay ./helm/personasay \
  -f helm/personasay/values-production.yaml
```

All environment variables are configurable via `global.env` in Helm values:
- `OPENAI_API_KEY` (required)
- `PORT` (default: 8001)
- `HOST` (default: 0.0.0.0)
- `DEBUG` (default: false)
- `DATABASE_URL` (default: SQLite)
- `REDIS_URL` (optional)
- `ENVIRONMENT` (default: production)

---

## Troubleshooting

### "Cannot connect to backend"
- **Local**: Ensure backend is running on port 8001
- **Docker**: Check `docker compose logs backend`
- **K8s**: Check pods with `kubectl get pods -n personasay`

### "OpenAI API error"
- Verify your API key is correct
- Check OpenAI account has credits
- Ensure key has proper permissions

### "File upload failed"
- Check file type is supported (PNG, JPG, PDF, DOCX, etc.)
- Verify file size is reasonable (<10MB recommended)
- View backend logs for detailed error

### Docker build issues
```bash
# Clear cache and rebuild
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### Kubernetes issues
```bash
# Check pod status
kubectl describe pod -n personasay <pod-name>

# View logs
kubectl logs -n personasay -l app.kubernetes.io/component=backend -f

# Restart deployment
kubectl rollout restart deployment -n personasay personasay-backend
```

---

## Additional Resources

- [README.md](../README.md) - Full documentation and features
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) - Customize for your industry
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

---

## Quick Commands Reference

### Makefile Commands
```bash
make help              # Show all available commands
make install           # Install dependencies
make docker-build      # Build Docker images
make docker-up         # Start with Docker
make helm-install      # Deploy to Kubernetes
make k8s-logs-backend  # View backend logs
```

### Docker Commands
```bash
docker compose up -d           # Start in background
docker compose down            # Stop
docker compose logs -f         # View logs
docker compose ps              # List services
docker compose restart backend # Restart backend
```

### Kubernetes Commands
```bash
kubectl get pods -n personasay                    # List pods
kubectl logs -n personasay -l component=backend   # Backend logs
kubectl port-forward -n personasay svc/frontend   # Port forward
helm status personasay -n personasay              # Deployment status
helm upgrade personasay ./helm/personasay         # Upgrade
```

---

**Questions?** Open an issue on GitHub or check the [full documentation](../README.md).
