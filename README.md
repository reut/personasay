# PersonaSay

**LangChain-Powered Multi-Persona AI Framework**

> **Fully Customizable Open-Source Template**  
> Default configuration showcases Sports Betting Analytics product, but **easily adaptable to ANY industry or product**!  
> See [CUSTOMIZATION_GUIDE.md](docs/CUSTOMIZATION_GUIDE.md) to make PersonaSay your own.

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-blue.svg)](https://python.langchain.com/)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue.svg)](https://www.typescriptlang.org/)

---

## About PersonaSay

PersonaSay is an innovative AI-powered framework that simulates expert personas from your target user base, providing diverse perspectives on product features, requirements, and decisions. Built with **LangChain agents**, each persona is an independent AI agent with persistent memory, reasoning capabilities, and specialized tools.

### What is PersonaSay?

PersonaSay transforms how product teams gather feedback by creating virtual expert personas that think, react, and provide insights just like real users. Instead of waiting for user research sessions or limited feedback cycles, teams can instantly engage with multiple expert perspectives simultaneously.

**Key Concept:**
> Each persona is an autonomous **LangChain agent** with:
> - Independent reasoning and decision-making
> - Persistent memory across conversations
> - Specialized tools and capabilities
> - Unique personality, pain points, and motivations

### Why PersonaSay?

**Problem:**
- Traditional user research is slow, expensive, and difficult to scale
- Product decisions often lack diverse stakeholder perspectives
- Teams struggle to anticipate how different users will react to features
- Getting feedback from multiple expert roles requires extensive coordination

**Solution:**
PersonaSay provides instant, multi-perspective feedback from AI personas representing your key user segments. Whether you're designing a new feature, evaluating requirements, or making product decisions, get immediate insights from Trading Managers, Product Owners, Risk Analysts, and more—all powered by LangChain + OpenAI GPT-4o.

### Use Cases

- **Feature Design Reviews**: Get instant feedback on mockups and wireframes from multiple stakeholder perspectives
- **Requirements Analysis**: Validate user stories and requirements with personas representing different roles
- **Product Decisions**: Debate features and priorities with virtual representatives of your user base
- **UX Research**: Test design concepts and identify potential pain points before development
- **Stakeholder Alignment**: Simulate discussions between different roles to uncover conflicts early
- **Onboarding & Training**: Help new team members understand different user perspectives quickly

### Who Should Use PersonaSay?

- **Product Managers**: Validate ideas and gather diverse feedback rapidly
- **UX Designers**: Test concepts with personas before expensive user testing
- **Development Teams**: Understand user needs and priorities from multiple angles
- **Startup Founders**: Make informed product decisions without extensive user research budgets
- **Enterprise Teams**: Scale user research across complex products with many stakeholders

---

## Features

### Multi-Persona Conversations
- **Customizable Personas**: Default includes 7 example personas (various roles and seniorities)
- **Empathy Map Structure**: Each persona has detailed think/feel, see, hear, say/do, pain, and gain profiles
- **@Mention System**: Target specific personas with `@name` syntax
- **Parallel Processing**: Get responses from multiple personas simultaneously
- **Easy Customization**: Replace default personas with your own industry experts ([guide](docs/CUSTOMIZATION_GUIDE.md))

### File Attachments
- **Image Support**: Upload screenshots and mockups (PNG, JPG, JPEG, WEBP)
- **Document Support**: Attach PDFs, Word docs, PowerPoint presentations, and text files
- **Multimodal AI**: GPT-4o Vision analyzes images and provides contextual feedback
- **File Validation**: Client-side and server-side validation with clear error messages

### Visual Mock Generation
- **SVG Mockups**: Request personas to generate visual mockups and wireframes
- **Toggle Control**: Enable/disable mock generation per message
- **Expand View**: Full-screen SVG preview for better visibility
- **Context-Aware**: Mockups reflect your product conventions and user needs

### AI-Powered Summaries
- **Conversation Analysis**: Distill lengthy discussions into key insights
- **Structured Output**: Consensus points, conflicts, action items, and recommendations
- **Export to Word**: Download summaries as `.docx` files for sharing

### Product Context Integration
- **Configurable Context**: Pre-configured with sports betting analytics product as an example
- **Easy Replacement**: Edit `frontend/src/config/product.config.ts` to define your own product
- **Domain-Specific**: Personas automatically adapt to your industry and product context
- **Mock Generation**: Visual mockups (SVG) are generated based on your domain keywords

---

## Quick Start

**New to PersonaSay?** Check out [QUICKSTART.md](docs/QUICKSTART.md) for the fastest path to getting started!

**Want to customize for your industry?** See [CUSTOMIZATION_GUIDE.md](docs/CUSTOMIZATION_GUIDE.md) to replace personas and product context!

### Prerequisites

- **Node.js** 18+ (for local development)
- **Python** 3.11+ (for local development)
- **Docker** (for containerized deployment)
- **Kubernetes + Helm** (for production deployment)
- **OpenAI API Key** ([get one here](https://platform.openai.com/api-keys))

### Three Ways to Run PersonaSay

#### 1. Local Development (2-3 minutes)

**Quick Setup with Script** (Recommended):
```bash
./setup.sh
# Edit backend/.env and add your OPENAI_API_KEY
cd backend && source venv/bin/activate && python main.py
# In new terminal: cd frontend && npm run dev
```

**Manual Setup**:
```bash
# Backend
cd backend && python3 -m venv venv && source venv/bin/activate
pip install -r config/requirements.txt && cp config/config.env.example config.env
# Add your OPENAI_API_KEY to config.env, then:
python main.py

# Frontend (in new terminal)
cd frontend && npm install && npm run dev
```
Access at: `http://localhost:5173`

#### 2. Docker Compose (2 minutes)
```bash
export OPENAI_API_KEY="sk-your-api-key"
docker compose up -d
```
Access at: `http://localhost`

> **Note**: Use `docker-compose` (with hyphen) if you have an older Docker version.

#### 3. Kubernetes with Helm (5 minutes)
```bash
helm install personasay ./helm/personasay \
  --namespace personasay \
  --create-namespace \
  --set global.env.OPENAI_API_KEY="sk-your-api-key" \
  --set backend.image.repository="your-registry/personasay/backend" \
  --set frontend.image.repository="your-registry/personasay/frontend"
```

**Detailed Instructions**: See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete deployment guide.

---

## Technical Architecture

### System Overview

PersonaSay is a **LangChain-based multi-agent system** that orchestrates specialized personas to provide diverse product feedback. Each persona is an independent **LangChain agent** with persistent memory, reasoning capabilities, and specialized tools.

**Core Principle:**
> *"Each persona is an autonomous LangChain agent with persistent database memory, independent reasoning, and tool-use capabilities"*

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Frontend Client   │    │   FastAPI Gateway   │    │  LangChain Agents   │
│   (React/TypeScript)│◄──►│   (LangChain API)   │◄──►│  (7 Personas)       │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                      │                          │
                                      ▼                          ▼
                            ┌─────────────────────┐    ┌─────────────────────┐
                            │  Database Layer     │    │  OpenAI GPT-4o      │
                            │  (SQLite/PostgreSQL)│    │  (LLM Provider)     │
                            └─────────────────────┘    └─────────────────────┘
```

### Frontend Layer (React + TypeScript)

**Technology Stack:**
- **React 18** with TypeScript for type-safe components
- **Vite** for fast development and building
- **TailwindCSS** for modern, responsive UI
- **Marked** for markdown rendering

**Component Hierarchy:**
```
App.tsx                          # Root application component
├── PersonaSelector.tsx         # Multi-select persona interface
├── ChatWindow.tsx             # Real-time conversation with file attachments
├── SummaryPanel.tsx           # AI-generated insights and export
└── TheFixer.tsx              # Debug/monitoring interface (optional)
```

**Key Features:**
- Dark theme with custom "Aboreto" font for headings
- Real-time message streaming and updates
- Mobile-responsive design
- @Mention system with regex pattern matching
- Multi-file upload with drag-and-drop support
- Dynamic SVG rendering with expand/collapse
- Export to Word documents via backend API

### Backend Layer (LangChain + FastAPI)

**Technology Stack:**
- **LangChain** (v0.3+) - Agent framework and orchestration
- **LangChain OpenAI** - OpenAI integration for LangChain
- **FastAPI** - High-performance async REST API
- **SQLAlchemy** - ORM for persistent memory storage
- **OpenAI GPT-4o** - LLM provider for agent reasoning
- **Pydantic** - Data validation and settings management

**LangChain Components:**
```python
# Multi-Agent Architecture
LangChainPersonaManager
├── LangChainPersonaAgent[]     # Independent agents (7 personas)
│   ├── AgentExecutor          # LangChain agent runner
│   ├── ConversationMemory     # Persistent chat history
│   ├── PersonaTools[]         # Agent capabilities
│   └── Database Session       # SQLAlchemy persistence
└── SessionManager            # Multi-conversation support
```

**API Endpoints:**
```
# LangChain Endpoints
POST /langchain/initialize      # Initialize persona agents (REQUIRED FIRST)
POST /langchain/chat           # Chat with LangChain agents
POST /langchain/debate         # Agent-to-agent debate
POST /langchain/summary        # Generate AI summary
GET  /langchain/stats          # System statistics
GET  /langchain/memory/{id}    # Get persona memory
GET  /langchain/conversation/{id} # Get conversation history
POST /langchain/reset          # Reset system

# Legacy Endpoints (backward compatible)
GET  /health                   # Health check
POST /chat                     # Standard chat (routes to LangChain)
POST /summary                  # Summary generation
```

**Architecture Patterns:**
- **LangChain Agents**: Each persona is an independent agent with reasoning
- **Persistent Memory**: SQLAlchemy database for conversation history
- **Async/Await**: Non-blocking I/O for concurrent agent processing
- **Agent Tools**: Personas can use tools and make decisions
- **Session Management**: Track conversations across requests

### Data Flow

#### LangChain Agent Message Flow
```
User Input → Frontend → FastAPI → LangChainPersonaManager → [Agent1, Agent2, ...AgentN]
                                                                  ↓
                                                    Each Agent:
                                                    1. Load Memory (Database)
                                                    2. Apply Persona Context
                                                    3. Reason with LangChain
                                                    4. Generate Response
                                                    5. Update Memory
                                                                  ↓
Frontend ← FastAPI ← LangChainPersonaManager ← [Response1, Response2, ...ResponseN]
```

#### File Attachment Flow
```
User Uploads File → Frontend (FormData) → Backend (/chat-attachments)
                                             ↓
                              ┌──────────────┴─────────────────┐
                              ▼                                ▼
                    Image Files (.png, .jpg)         Document Files (.pdf, .docx)
                              ↓                                ↓
                    Base64 Encode for Vision         Extract Text (first 64KB)
                              ↓                                ↓
                    ┌─────────┴────────────────────────────────┘
                    ▼
          OpenAI GPT-4o Vision API (multimodal prompt)
                    ↓
          Persona Responses (with image context)
```

#### Mock Generation Flow
```
User Enables Mock Toggle → Backend receives generate_mock=true
                              ↓
               System Prompt Augmented with SVG Instructions
                              ↓
               OpenAI Generates Response with Inline SVG
                              ↓
               Backend Extracts SVG from Response
                              ↓
               Frontend Renders SVG with Expand Option
```

### Persona Intelligence System

Each of the 7 personas has:
- **Empathy Map**: Think/Feel, Hear, See, Say/Do, Pain, Gain
- **Role-Specific Context**: Job title, company type, responsibilities
- **Domain Expertise**: Product features, domain knowledge, industry expertise
- **Personality Traits**: Communication style, priorities, decision-making approach

| Persona | Role | Focus Area | Key Pain Points |
|---------|------|-----------|-----------------|
| **Alex** | Head of Trading | Uptime, SLAs, provider performance | Reactive responses, coverage gaps |
| **Ben** | Performance Analyst | Data analysis, ROI proof | Manual processes, limited exports |
| **Nina** | Product Owner | User experience, simplicity | Complex UI, poor incident visibility |
| **Clara** | Risk & Trading Ops | Risk management, margin analysis | Real-time monitoring gaps, liability |
| **Marco** | VP Commercial Strategy | ROI, competitive advantage | Cost vs value, strategic insights |
| **John** | Customer Support Lead | Incident response, reliability | Reactive support, unclear status |
| **Rachel** | In-Play Trader | Real-time trading, latency | Mid-game alerts, manual provider switching |


### Product Documentation Service

**Hybrid Content Architecture:**
- **Static Content**: Hardcoded fallback features for reliable baseline knowledge
- **Dynamic Content**: Live-scraped from your product documentation
- **Automatic Discovery**: Recursive crawling finds all related documentation pages
- **Refresh Mechanism**: Configurable automatic content updates (default: every 6 hours)
- **Fallback Strategy**: Graceful degradation to static content if scraping fails

**How It Works:**
1. Configure with your documentation URL
2. Service automatically discovers and scrapes all subpages
3. Extracted features are cached and formatted for AI context
4. Personas receive comprehensive, up-to-date product knowledge

**Default Example**:
- Static baseline: 8 core features
- Dynamic scraped: 20+ features from product user guides url
- Automatic crawl depth: 2 levels
- Updates every 6 hours

**Customization:** See `backend/services/README.md` for configuration guide

---

## Technology Stack

### Frontend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | React | 18.2 | UI component library |
| Language | TypeScript | 5.2 | Type-safe development |
| Build Tool | Vite | 4.5 | Fast dev server and building |
| Styling | TailwindCSS | 3.4 | Utility-first CSS |
| Markdown | Marked | 16.2 | Message content rendering |
| UUID | uuid | 11.1 | Unique identifiers |

### Backend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Agent Framework** | **LangChain** | **0.3+** | **Multi-agent orchestration** |
| **LangChain OpenAI** | **langchain-openai** | **0.2+** | **OpenAI integration** |
| API Framework | FastAPI | 0.104 | Async REST API |
| LLM Provider | OpenAI GPT-4o | 1.6+ | Agent reasoning and vision |
| Database ORM | SQLAlchemy | 2.0+ | Persistent memory |
| Database | SQLite/PostgreSQL | - | Conversation storage |
| Data Models | Pydantic | 2.0+ | Request/response validation |
| Server | Uvicorn | 0.24 | ASGI server |

---

## Usage Examples

### Basic Conversation
```
Select personas: Alex, Nina, Ben
Message: "What do you think about adding real-time provider alerts?"

Alex: "As Head of Trading, real-time alerts are critical..."
Nina: "From a product perspective, alerts need to be simple..."
Ben: "I'd want to see historical alert data for analysis..."
```

### Using @Mentions
```
Message: "@alex what are your thoughts on this feature?"

Result: Only Alex responds, regardless of other selected personas
```

### File Attachments
```
1. Click paperclip icon
2. Select image/document (e.g., screenshot.png)
3. Type message: "What do you think about this design?"
4. Send

Personas receive the image and provide visual feedback
```

### Mock Generation
```
1. Click magic-wand toggle (turns ON with green glow)
2. Message: "Create a quick mock for the provider dashboard"
3. Send

Personas may include inline SVG mockups in their responses
Click "expand" icon to view full-screen
```

### Generating Summaries
```
1. Have a conversation with multiple messages
2. Click "Generate Summary" button
3. Wait for AI analysis (5-10 seconds)
4. Review structured summary with key insights
5. Click "Export Summary" to download as .docx
```

---

## Security & Privacy

### API Key Management
- Environment variables for server-side keys
- No API keys in client-side code (config.ts for reference only)
- Secure transmission over HTTPS (production)

### File Upload Security
- File type validation (client + server)
- File size limits (implicitly handled by memory constraints)
- Allowed extensions: `.png, .jpg, .jpeg, .webp, .pdf, .doc, .docx, .ppt, .pptx, .txt`
- Temporary file handling (files processed in-memory, not persisted)

### Data Privacy
- No conversation data stored on server (stateless API)
- OpenAI data processing follows their [privacy policy](https://openai.com/policies/privacy-policy)
- Be mindful when uploading sensitive documents/images

---

## Configuration

### Environment Variables (`backend/config.env`)

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-api-key-here

# Server Configuration
PORT=8001
HOST=127.0.0.1
DEBUG=false

# Database (Optional - for future LangChain version)
DATABASE_URL=sqlite:///./personasay.db
# DATABASE_URL=postgresql://user:password@localhost:5432/personasay
```

### Frontend Configuration (`frontend/src/config.ts`)

```typescript
export const config = {
  api: {
    baseUrl: 'http://127.0.0.1:8001',
  },
  openai: {
    apiKey: 'YOUR_OPENAI_API_KEY', // For reference only, not used
    model: 'gpt-4o',
  },
};
```

---

## Deployment

PersonaSay can be deployed **locally** for development or in **production** using Docker or Kubernetes (K8s).

**Full deployment guide**: See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

### Quick Deployment Options

#### Option 1: Local Development
```bash
# Backend
cd backend && python working_server.py

# Frontend
cd frontend && npm run dev
```
Access at: `http://localhost:5173`

#### Option 2: Docker Compose (Recommended for Quick Testing)
```bash
export OPENAI_API_KEY="sk-your-api-key"
docker compose up -d
```
Access at: `http://localhost`

#### Option 3: Kubernetes with Helm (Production)
```bash
# Install with Helm
helm install personasay ./helm/personasay \
  --namespace personasay \
  --create-namespace \
  --set global.env.OPENAI_API_KEY="sk-your-api-key" \
  --set backend.image.repository="your-registry/personasay/backend" \
  --set frontend.image.repository="your-registry/personasay/frontend"
```

### Deployment Features

- **Docker Support**: Multi-stage builds, health checks, security best practices  
- **Kubernetes Ready**: Full Helm chart with ConfigMaps, Secrets, and Services  
- **Environment Variables**: All configurable via Helm `global.env` values  
- **Auto-scaling**: HPA support for both frontend and backend  
- **Production Hardened**: Security contexts, resource limits, liveness/readiness probes  
- **Ingress Support**: Built-in ingress configuration with TLS support

---

## Performance & Scaling

### Current Limits
- **Concurrent Personas**: 7 (all personas processed in parallel)
- **API Calls**: Rate limited by OpenAI (see [OpenAI rate limits](https://platform.openai.com/docs/guides/rate-limits))
- **File Size**: Recommended <10MB per file
- **Conversation History**: Client-side only (no server persistence in current version)

### Optimization Tips
- Use `gpt-4o-mini` for faster/cheaper responses (modify in `working_server.py`)
- Limit active personas to reduce API costs
- Implement Redis caching for frequently requested content
- Use CDN for static frontend assets in production

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test thoroughly
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Code Style
- **Frontend**: ESLint + Prettier (React/TypeScript conventions)
- **Backend**: PEP 8 (Python style guide)
- **Commits**: Conventional Commits format

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **OpenAI** for GPT-4o API
- **FastAPI** and **React** communities for excellent frameworks
- All contributors and testers

---

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/personasay/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/personasay/discussions)
- **Email**: your-email@example.com

---

*PersonaSay simulates expert feedback, but remember: real user research is irreplaceable!*
