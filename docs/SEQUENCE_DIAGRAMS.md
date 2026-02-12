# PersonaSay Sequence Diagrams

This document provides complete sequence diagrams for all major flows in the PersonaSay application.

---

## Table of Contents

1. [Initialization Flow](#1-initialization-flow)
2. [Chat Flow](#2-chat-flow)
3. [Chat with Attachments Flow](#3-chat-with-attachments-flow)
4. [Debate Flow](#4-debate-flow)
5. [Summary Flow](#5-summary-flow)

---

## 1. Initialization Flow

**Lazy initialization triggered by first chat request**

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Frontend (React)
    participant Backend as Backend (FastAPI)
    participant Manager as LangChainPersonaManager
    participant Agent as LangChainPersonaAgent
    participant Loader as EnhancedProfileLoader
    participant DB as SQLite
    participant OpenAI as OpenAI API

    User->>Frontend: Opens app
    Frontend->>Frontend: Load personas.config.ts
    Frontend->>Frontend: Set default selection (alex, ben, nina, rachel)
    Note over Frontend: No API call on mount. Initialization is lazy.

    User->>Frontend: Sends first message
    Frontend->>Backend: POST /chat {prompt, personas, history}
    Backend->>Backend: get_or_none_langchain_manager() → None

    rect rgb(240, 248, 255)
        Note over Backend,DB: Auto-Initialization first request only
        Backend->>Manager: new LangChainPersonaManager(api_key)
        Manager->>DB: create_engine(sqlite:///data/personasay.db)
        Manager->>DB: Base.metadata.create_all()

        loop For each persona in request
            Manager->>Agent: new LangChainPersonaAgent(persona_data)
            Agent->>Loader: get_persona_data(persona_id, baseline)
            Loader->>Loader: load {id}_enhanced.json
            Loader->>Loader: merge_with_baseline_persona()
            Loader-->>Agent: merged persona data
            Agent->>Agent: _initialize_llm() → ChatOpenAI(gpt-4o)
            Agent->>DB: _initialize_memory() → load from DB
            Agent->>Agent: _initialize_tools()
            Agent->>Agent: _initialize_agent() → AgentExecutor
        end
        Manager-->>Backend: Manager ready with all agents
        Backend->>Backend: set_langchain_manager(manager)
    end

    Note over Backend: Continues to chat flow...
```

**Key Points:**
- No initialization on server startup - fully lazy
- First `/chat` request triggers auto-initialization
- Each persona loads from `{id}_enhanced.json` and merges with baseline
- LangChain agents created with memory, tools, and AgentExecutor
- Memory is loaded from database (if exists from previous sessions)

---

## 2. Chat Flow

**Standard conversation with personas**

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Frontend (ChatWindow)
    participant Backend as Backend (chat.py)
    participant Manager as PersonaManager
    participant Alex as Agent Alex
    participant Nina as Agent Nina
    participant Ben as Agent Ben
    participant OpenAI as OpenAI API
    participant DB as SQLite

    User->>Frontend: Type message, click Send
    Frontend->>Frontend: Parse @mentions
    Frontend->>Frontend: Build history array
    Frontend->>Backend: POST /chat {prompt, personas, generate_mock, history}

    Backend->>Backend: get_or_none_langchain_manager()
    Backend->>Backend: get_product_context()
    Backend->>Manager: get_all_responses(persona_ids, message, product_ctx, session_id)

    par Persona responses (sequential await, concurrent creation)
        Manager->>Alex: think_and_respond(message, product_ctx)
        Alex->>Alex: Load memory from buffer
        Alex->>Alex: _create_system_prompt()
        Alex->>OpenAI: llm.ainvoke(messages)
        OpenAI-->>Alex: Response text
        Alex->>Alex: ResponseValidator.validate()
        Alex->>DB: _save_memory_to_db()
        Alex-->>Manager: "As Head of Trading..."

        Manager->>Nina: think_and_respond(message, product_ctx)
        Nina->>OpenAI: llm.ainvoke(messages)
        OpenAI-->>Nina: Response text
        Nina->>DB: _save_memory_to_db()
        Nina-->>Manager: "From a product perspective..."

        Manager->>Ben: think_and_respond(message, product_ctx)
        Ben->>OpenAI: llm.ainvoke(messages)
        OpenAI-->>Ben: Response text
        Ben->>DB: _save_memory_to_db()
        Ben-->>Manager: "Looking at the data..."
    end

    Manager-->>Backend: [reply_alex, reply_nina, reply_ben]

    opt generate_mock = true
        loop For each reply
            Backend->>OpenAI: ChatOpenAI.ainvoke(mock prompt)
            OpenAI-->>Backend: JSON with SVG params
            Backend->>Backend: Generate SVG from template
        end
    end

    Backend-->>Frontend: {replies: [...], session_id, status: "success"}
    Frontend->>Frontend: Map replies to chat messages
    Frontend->>User: Render persona responses (with SVG if mock)
```

**Key Points:**
- @Mentions are parsed by frontend to filter active personas
- Personas respond in parallel (concurrent async tasks)
- Each response is validated and saved to database
- Optional mock generation creates SVG visualizations
- All conversation history persists in SQLite

---

## 3. Chat with Attachments Flow

**Chat with image or document attachments**

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Frontend (ChatWindow)
    participant Backend as Backend (chat.py)
    participant Manager as PersonaManager
    participant Agent as PersonaAgent
    participant OpenAI as OpenAI Vision
    participant DB as SQLite

    User->>Frontend: Attach files + type message
    Frontend->>Backend: POST /chat-attachments (FormData: prompt, personas, files)

    Backend->>Backend: Parse JSON (personas, history)
    Backend->>Backend: Separate images vs documents
    Backend->>Backend: Extract text from documents (first 64KB)

    alt Has image files
        loop For each persona
            Backend->>Backend: Build vision content (text + base64 images)
            Backend->>OpenAI: ChatOpenAI(model=gpt-4o).ainvoke([image_content])
            OpenAI-->>Backend: Vision-aware response
        end
    else Text/docs only
        Backend->>Backend: Build enhanced prompt with doc text
        Backend->>Manager: get_all_responses(personas, enhanced_prompt)
        loop For each persona
            Manager->>Agent: think_and_respond()
            Agent->>OpenAI: llm.ainvoke(messages)
            OpenAI-->>Agent: Response
            Agent->>DB: Save to memory
        end
        Manager-->>Backend: All responses
    end

    Backend-->>Frontend: {replies: [...], status: "success"}
    Frontend->>User: Render responses with file context
```

**Key Points:**
- Supports images (PNG, JPG, WEBP) and documents (PDF, DOCX, TXT)
- Images use GPT-4o Vision for multimodal understanding
- Documents have text extracted and appended to prompt
- File attachments are processed per request (not persisted)

---

## 4. Debate Flow

**Multi-round structured debate between personas**

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Frontend (DebatePanel)
    participant Backend as Backend (debate.py)
    participant Manager as PersonaManager
    participant Agents as PersonaAgents (debate mode)
    participant OpenAI as OpenAI API
    participant DB as SQLite

    User->>Frontend: Set topic, select personas, click Start
    Frontend->>Frontend: Create debate_id

    loop Round 1..N
        Frontend->>Backend: POST /debate/round {debate_id, topic, personas, round_number, conversation_history}

        Backend->>Backend: Get/init LangChainPersonaManager

        rect rgb(255, 248, 240)
            Note over Backend,Agents: Switch to debate mode
            Backend->>Agents: Ensure context_mode = "debate"
            Backend->>Agents: Reinitialize agent if needed
        end

        Backend->>Backend: Extract last 14 messages as history
        Backend->>Backend: Build history_context (other participants' arguments)

        alt Round 1
            Backend->>Backend: round_instruction = "Present initial position"
        else Round 2+
            Backend->>Backend: round_instruction = "React to others, evolve thinking"
        end

        Backend->>Backend: Combine into debate_prompt
        Backend->>Manager: get_all_responses(persona_ids, debate_prompt)

        par All personas respond
            Manager->>Agents: think_and_respond() per persona
            Agents->>OpenAI: llm.ainvoke() per persona
            OpenAI-->>Agents: Responses
            Agents->>DB: Save memory per persona
        end

        Manager-->>Backend: [responses]
        Backend-->>Frontend: {round, responses, debate_id, status}
        Frontend->>Frontend: Add responses to conversation_history
        Frontend->>User: Render round responses
    end

    opt User requests summary
        User->>Frontend: Click "Generate Summary"
        Frontend->>Backend: POST /summary {history, personas, context}
        Backend->>OpenAI: Single LLM call with full conversation
        OpenAI-->>Backend: Structured summary + KPIs
        Backend-->>Frontend: {summary, kpis, status}
        Frontend->>User: Display summary
    end
```

**Key Points:**
- Debate mode changes persona system prompts for argumentative responses
- Each round includes context from previous rounds (last 14 messages)
- Round 1: Initial positions, Round 2+: React and evolve
- Personas engage with each other's arguments
- Optional summary generation at end

---

## 5. Summary Flow

**AI-powered conversation summary with KPI extraction**

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Frontend (SummaryPanel)
    participant Backend as Backend (summary.py)
    participant OpenAI as OpenAI API

    User->>Frontend: Click "Generate Summary"
    Frontend->>Frontend: Build history from chat/debate messages
    Frontend->>Backend: POST /summary {history, personas}

    Backend->>Backend: Detect discussion rounds (user msgs = round boundaries)
    Backend->>Backend: Format conversation with round markers
    Backend->>Backend: Get product context + date context
    Backend->>Backend: Build summary prompt (6-section structure)

    Backend->>OpenAI: ChatOpenAI(gpt-4o, temp=0.3).ainvoke()
    OpenAI-->>Backend: Summary markdown

    Backend->>Backend: ensure_kpis_in_summary()
    Backend->>Backend: extract_kpis_as_structured_data()

    Backend-->>Frontend: {summary, kpis, kpi_count, status}
    Frontend->>User: Render formatted summary
    
    opt Export
        User->>Frontend: Click "Export Summary"
        Frontend->>Frontend: Generate .docx file
        Frontend->>User: Download file
    end
```

**Key Points:**
- Automatically detects discussion rounds from conversation history
- Generates 6-section structured summary:
  1. Executive Summary
  2. Key Discussion Themes
  3. Consensus Points
  4. Areas of Disagreement
  5. Action Items & Recommendations
  6. KPIs Identified
- Extracts KPIs as structured data (JSON)
- Supports .docx export for sharing

---

## Architecture Overview

### System Components

```mermaid
graph TB
    subgraph Frontend
        UI[React UI]
        ChatWindow[ChatWindow.tsx]
        DebatePanel[DebatePanel.tsx]
        SummaryPanel[SummaryPanel.tsx]
    end

    subgraph Backend
        API[FastAPI Routes]
        Manager[LangChainPersonaManager]
        Agents[LangChainPersonaAgents]
    end

    subgraph External
        OpenAI[OpenAI GPT-4o]
        DB[SQLite Database]
    end

    UI --> ChatWindow
    UI --> DebatePanel
    UI --> SummaryPanel

    ChatWindow --> API
    DebatePanel --> API
    SummaryPanel --> API

    API --> Manager
    Manager --> Agents
    Agents --> OpenAI
    Agents --> DB
```

### Data Flow Patterns

**Request-Response Pattern:**
- All frontend-backend communication is synchronous HTTP (REST)
- No WebSockets, SSE, or webhooks currently implemented
- Each request waits for full response before proceeding

**Persona Processing:**
- Personas process requests in parallel (concurrent async tasks)
- Each persona has independent memory and state
- All personas share the same database but have separate memory buffers

**Memory Persistence:**
- Every chat exchange saved to SQLite (`persona_memories` table)
- Memory loaded on agent initialization
- ConversationBufferWindowMemory keeps last 50 exchanges in memory

---

## API Endpoints Reference

### Chat Endpoints
- `POST /chat` - Standard chat with personas
- `POST /chat-attachments` - Chat with file attachments

### Debate Endpoints
- `POST /debate/round` - Execute single debate round
- `POST /debate/round-with-attachments` - Debate with attachments
- `POST /langchain/debate` - Legacy multi-round debate (not used)

### Summary Endpoints
- `POST /summary` - Generate conversation summary

### System Endpoints
- `GET /health` - Health check
- `POST /langchain/initialize` - Initialize personas (optional)
- `GET /langchain/stats` - System statistics
- `GET /product/config` - Get product configuration

### Memory Endpoints
- `GET /langchain/memory/{persona_id}` - Get persona memory
- `GET /langchain/conversation/{session_id}` - Get conversation history

---

## Implementation Notes

### Lazy Initialization
The system uses lazy initialization - no personas are loaded until the first chat request. This reduces startup time and resource usage.

### Parallel Processing
Personas respond concurrently using Python's `asyncio`. Tasks are created together but awaited sequentially in the current implementation. For true parallel execution, use `asyncio.gather()`.

### Database Schema
```sql
CREATE TABLE persona_memories (
    id INTEGER PRIMARY KEY,
    persona_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    message_type TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Response Format
All API responses follow this structure:
```json
{
    "replies": [...],
    "session_id": "uuid",
    "framework": "langchain",
    "status": "success"
}
```

---

## Future Enhancement Opportunities

Based on these flows, potential improvements include:

1. **True Parallel Execution**: Use `asyncio.gather()` for concurrent persona responses
2. **WebSocket Support**: Real-time streaming responses instead of waiting for all personas
3. **Webhook Events**: Fire events for external integrations (e.g., n8n, Zapier)
4. **Caching**: Redis cache for product context and persona profiles
5. **Batch Processing**: Process multiple prompts in a single request
6. **Agent-to-Agent Communication**: Direct persona interactions without user mediation

---

*Generated: 2026-02-06*
*PersonaSay Version: LangChain 0.3+*
