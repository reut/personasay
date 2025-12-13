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

---

## Configuration Files

### Product Configuration

**File**: `product_config.py` (gitignored - your customizations stay private)  
**Template**: `product_config.py.example` (tracked in git - generic template)

This is the **single source of truth** for your product information in PersonaSay.

#### Setup

```bash
# Copy the template
cp backend/config/product_config.py.example backend/config/product_config.py

# Edit with your product details
nano backend/config/product_config.py  # or use your preferred editor
```

#### What to Configure

| Section | Required | Description |
|---------|----------|-------------|
| **Basic Identity** | ✅ Yes | Product name, tagline, industry |
| **Product Context** | ✅ Yes | Description, features, pain points, value prop |
| **Target Users** | ✅ Yes | Who uses your product (3-6 types) |
| **Technical Context** | ⚠️ Recommended | Brief technical overview |
| **Mock Generation** | ⚠️ Recommended | Context for SVG mock generation |

#### How It's Used

1. **API Endpoint**: Frontend fetches config via `GET /product/config`
2. **AI Context**: Personas use this to understand your product domain
3. **Mock Generation**: SVG diagrams reflect your industry and terminology
4. **System Prompts**: AI behavior adapts to your product context

#### Example Configuration

See `product_config.py.example` for:
- Complete template with detailed comments
- Two industry examples (SaaS, Healthcare)
- Tips for great configuration

#### Environment Override

All values can be overridden via environment variables:

```bash
export PRODUCT_NAME="MyProduct"
export PRODUCT_SHORT_NAME="MyProduct"
export PRODUCT_INDUSTRY="SaaS"
```

See `product_config.py.example` for full list of environment variables.

---

### Environment Variables

**File**: `.env` or `config.env` (gitignored - contains secrets)  
**Template**: `config.env.example` (tracked in git)

Contains sensitive configuration like API keys and database URLs.

#### Setup

```bash
# Copy the template
cp backend/config/config.env.example backend/.env

# Edit with your actual values
nano backend/.env

# Add your OpenAI API key (required)
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

#### Required Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API key ([get one here](https://platform.openai.com/api-keys)) |
| `DATABASE_URL` | ⚠️ Default provided | SQLite for dev, PostgreSQL for production |
| `SECRET_KEY` | ⚠️ Default provided | Change in production! |
| `CORS_ORIGINS` | ⚠️ Default provided | Allowed frontend origins |

#### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Generate secure `SECRET_KEY` (see config.env.example)
- [ ] Use PostgreSQL `DATABASE_URL`
- [ ] Set `LOG_LEVEL=WARNING` or `ERROR`
- [ ] Configure production `CORS_ORIGINS`

---

### Dynamic Product Documentation

**Service**: `product_docs_service.py`  
**Configuration**: Optional - configure in `lsports_full_config_example.py`

Automatically scrapes your product documentation to keep AI personas updated.

#### Features

- **Static Fallback**: Hardcoded features as baseline
- **Dynamic Scraping**: Live updates from your docs
- **Auto-refresh**: Configurable intervals (default: 6 hours)
- **Graceful Degradation**: Falls back if scraping fails

#### Setup (Optional)

```python
# In your app startup (main.py or dependencies.py)
from services.product_docs_service import ProductDocsConfig, ProductDocsService, set_service

config = ProductDocsConfig(
    main_docs_url="https://docs.yourproduct.com/features",
    product_name="YourProduct",
    product_industry="Your Industry",
    cache_duration_hours=6
)

service = ProductDocsService(config)
set_service(service)
```

See `backend/services/README.md` for complete guide.

---

---

### Persona Configurations

**Location**: `backend/app/personas/` directory  
**Template**: `persona_template.json` (tracked in git)  
**Actual Personas**: `*_enhanced.json` files (gitignored - your customizations stay private)

PersonaSay comes with 7 default personas for sports betting. **You should customize these for your product/industry.**

#### Setup

```bash
# Copy the template for each persona you want to create
cp backend/app/personas/persona_template.json backend/app/personas/sarah_analyst.json

# Edit with your persona details
nano backend/app/personas/sarah_analyst.json
```

#### What to Configure

Each persona needs:
- **Basic Info**: id, name, role, company, description
- **Empathy Map**: think_and_feel, hear, see, say_and_do, pain, gain
- **Career History**: roles, achievements, defining experiences
- **Industry Awareness**: market trends, competitors, vendors, regulations
- **Organizational Context**: stakeholders, team, budget, decision authority
- **Communication Patterns**: tone, terminology, question patterns
- **Incentives**: KPIs, career risks/gains, decision drivers
- **Response Rules**: How the persona generates responses

#### Template Structure

The `persona_template.json` includes:
- Complete structure with all required fields
- Detailed explanations for each field (in brackets)
- Examples and tips
- 300+ lines of guidance

#### Best Practices

1. **Be Specific**: Use real numbers, metrics, and examples
2. **Show Experience**: Reference past roles and defining moments
3. **Include Constraints**: Budget limits, approval processes, stakeholder pressure
4. **Domain Terminology**: Use industry-specific terms and jargon
5. **Make Them Distinct**: Each persona should have unique voice and concerns

#### Default Personas (Sports Betting - Example Only)

The repo includes 7 example personas in sports betting:
- `alex_enhanced.json` - Trading Manager
- `ben_enhanced.json` - Performance Analyst  
- `clara_enhanced.json` - Risk & Trading Ops
- `john_enhanced.json` - Customer Support Lead
- `marco_enhanced.json` - VP Commercial Strategy
- `nina_enhanced.json` - Product Owner
- `rachel_enhanced.json` - In-Play Trader

**These are examples** showing the level of detail needed. Replace them with personas relevant to your product.

#### How Personas Are Used

1. **AI Context**: LangChain agents use persona details to generate authentic responses
2. **Empathy-Driven**: Responses reflect persona's pain points, gains, and motivations
3. **Experience-Based**: Career history and defining moments shape their perspective
4. **Constraint-Aware**: Organizational context (budget, stakeholders, KPIs) influences their thinking

See [CUSTOMIZATION_GUIDE](../../docs/CUSTOMIZATION_GUIDE.md) for detailed persona customization instructions.

---

## Quick Setup Checklist

For new installations:

- [ ] Copy `config.env.example` → `.env` and add `OPENAI_API_KEY`
- [ ] Copy `product_config.py.example` → `product_config.py`
- [ ] Edit `product_config.py` with your product details
- [ ] (Optional) Create custom personas using `persona_template.json`
- [ ] (Optional) Configure `product_docs_service` for dynamic content
- [ ] Install dependencies: `pip install -r requirements-dev.txt`
- [ ] Run backend: `python main.py`

---

## File Structure

```
backend/
├── config/
│   ├── config.env.example          # Environment variables template (tracked)
│   ├── product_config.py.example   # Product configuration template (tracked)
│   ├── lsports_full_config_example.py  # Product docs scraping example (tracked)
│   ├── requirements.txt            # Production dependencies (tracked)
│   ├── requirements-dev.txt        # Development dependencies (tracked)
│   ├── README.md                   # This file (tracked)
│   │
│   ├── .env                        # Your environment variables (gitignored)
│   └── product_config.py           # Your product configuration (gitignored)
│
└── app/
    └── personas/
        ├── persona_template.json       # Persona template (tracked)
        │
        ├── alex_enhanced.json          # Your persona files (gitignored)
        ├── nina_enhanced.json          # Your persona files (gitignored)
        └── *_enhanced.json             # All custom personas (gitignored)
```

**Tracked files** = In git, safe to share publicly  
**Gitignored files** = Your private customizations

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'config.product_config'"

**Solution**: You haven't created `product_config.py` yet.

```bash
cp backend/config/product_config.py.example backend/config/product_config.py
```

### "OpenAI API authentication failed"

**Solution**: Check your `.env` file has valid `OPENAI_API_KEY`.

### "Product config seems generic"

**Solution**: Edit `backend/config/product_config.py` with your actual product details.

---

## Related Documentation

- [Main README](../../README.md) - Project overview
- [CUSTOMIZATION_GUIDE](../../docs/CUSTOMIZATION_GUIDE.md) - Full customization guide
- [QUICKSTART](../../docs/QUICKSTART.md) - Fast setup guide
- [Product Docs Service](../services/README.md) - Dynamic content scraping

