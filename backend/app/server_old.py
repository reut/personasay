"""
PersonaSay Backend - LangChain Production Server
Official LangChain.com implementation with database persistence
Server-ready for deployment with independent persona agents
"""

import asyncio
import base64
import json
import math
import os
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

# FastAPI
from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# LangChain PersonaSay System
from app.langchain_personas import LangChainPersonaManager, Settings


# SVG Mock Generator
def generate_svg_dashboard(data: Dict[str, Any]) -> str:
    """
    Generate a high-quality, professional SVG dashboard with 3 panels.
    This ensures perfect rendering every time with proper calculations.
    """
    # Extract data with defaults
    bar_title = data.get("bar_title", "Performance Metrics")
    bar_items = [
        {"name": data.get("bar1_name", "Metric 1"), "value": data.get("bar1_value", 95.0)},
        {"name": data.get("bar2_name", "Metric 2"), "value": data.get("bar2_value", 88.0)},
        {"name": data.get("bar3_name", "Metric 3"), "value": data.get("bar3_value", 92.0)},
    ]

    line_title = data.get("line_title", "Trend Analysis")
    line_items = [
        {"label": data.get("line1_label", "Point 1"), "value": data.get("line1_value", 450)},
        {"label": data.get("line2_label", "Point 2"), "value": data.get("line2_value", 820)},
        {"label": data.get("line3_label", "Point 3"), "value": data.get("line3_value", 1250)},
        {"label": data.get("line4_label", "Point 4"), "value": data.get("line4_value", 1700)},
    ]

    donut_title = data.get("donut_title", "Distribution")
    donut_items = [
        {
            "name": data.get("donut1_name", "Category 1"),
            "value": data.get("donut1_value", 50),
            "color": "#ef4444",
        },
        {
            "name": data.get("donut2_name", "Category 2"),
            "value": data.get("donut2_value", 30),
            "color": "#10b981",
        },
        {
            "name": data.get("donut3_name", "Category 3"),
            "value": data.get("donut3_value", 20),
            "color": "#3b82f6",
        },
    ]

    # Calculate bar heights (max 350px for 100%)
    bar_heights = [min(item["value"] * 3.5, 350) for item in bar_items]

    # Calculate line chart positions (normalize to 70-350 range)
    max_val = max(item["value"] for item in line_items)
    min_val = min(item["value"] for item in line_items)
    val_range = max_val - min_val if max_val != min_val else 1
    line_y_positions = [
        420 - ((item["value"] - min_val) / val_range * 280 + 70) for item in line_items
    ]

    # Calculate donut segments (circumference = 2π * 100 = 628)
    circumference = 628
    donut_percentages = [item["value"] / 100 for item in donut_items]
    donut_lengths = [p * circumference for p in donut_percentages]

    # Calculate rotation angles for donut segments
    rotation_angles = [-90]  # Start at top
    cumulative = 0
    for p in donut_percentages[:-1]:
        cumulative += p
        rotation_angles.append(-90 + cumulative * 360)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="620" viewBox="0 0 1080 620">
  <defs>
    <style>
      text {{ font-family: system-ui, -apple-system, sans-serif; }}
      .bg {{ fill: #0f172a; }}
      .panel {{ fill: #1e293b; }}
      .title {{ fill: #f1f5f9; font-size: 18px; font-weight: 600; }}
      .label {{ fill: #cbd5e1; font-size: 13px; }}
      .value {{ fill: #f8fafc; font-size: 16px; font-weight: 600; }}
    </style>
  </defs>
  
  <rect width="1080" height="620" class="bg"/>
  
  <!-- Panel 1: Bar Chart -->
  <g transform="translate(40, 40)">
    <rect width="300" height="520" rx="8" class="panel"/>
    <text x="150" y="40" text-anchor="middle" class="title">{bar_title}</text>
    
    <rect x="40" y="{420 - bar_heights[0]}" width="60" height="{bar_heights[0]}" fill="#3b82f6" rx="3"/>
    <text x="70" y="460" text-anchor="middle" class="value">{bar_items[0]['value']:.1f}%</text>
    <text x="70" y="485" text-anchor="middle" class="label">{bar_items[0]['name']}</text>
    
    <rect x="120" y="{420 - bar_heights[1]}" width="60" height="{bar_heights[1]}" fill="#10b981" rx="3"/>
    <text x="150" y="460" text-anchor="middle" class="value">{bar_items[1]['value']:.1f}%</text>
    <text x="150" y="485" text-anchor="middle" class="label">{bar_items[1]['name']}</text>
    
    <rect x="200" y="{420 - bar_heights[2]}" width="60" height="{bar_heights[2]}" fill="#8b5cf6" rx="3"/>
    <text x="230" y="460" text-anchor="middle" class="value">{bar_items[2]['value']:.1f}%</text>
    <text x="230" y="485" text-anchor="middle" class="label">{bar_items[2]['name']}</text>
  </g>
  
  <!-- Panel 2: Line Chart -->
  <g transform="translate(380, 40)">
    <rect width="300" height="520" rx="8" class="panel"/>
    <text x="150" y="40" text-anchor="middle" class="title">{line_title}</text>
    
    <polyline points="40,{line_y_positions[0]} 110,{line_y_positions[1]} 180,{line_y_positions[2]} 250,{line_y_positions[3]}" 
              stroke="#f59e0b" stroke-width="3" fill="none"/>
    
    <circle cx="40" cy="{line_y_positions[0]}" r="6" fill="#f59e0b"/>
    <circle cx="110" cy="{line_y_positions[1]}" r="6" fill="#f59e0b"/>
    <circle cx="180" cy="{line_y_positions[2]}" r="6" fill="#f59e0b"/>
    <circle cx="250" cy="{line_y_positions[3]}" r="6" fill="#f59e0b"/>
    
    <text x="40" y="450" text-anchor="middle" class="label">{line_items[0]['label']}</text>
    <text x="110" y="450" text-anchor="middle" class="label">{line_items[1]['label']}</text>
    <text x="180" y="450" text-anchor="middle" class="label">{line_items[2]['label']}</text>
    <text x="250" y="450" text-anchor="middle" class="label">{line_items[3]['label']}</text>
    
    <text x="40" y="{line_y_positions[0] - 10}" text-anchor="middle" class="value">{line_items[0]['value']}</text>
    <text x="110" y="{line_y_positions[1] - 10}" text-anchor="middle" class="value">{line_items[1]['value']}</text>
    <text x="180" y="{line_y_positions[2] - 10}" text-anchor="middle" class="value">{line_items[2]['value']}</text>
    <text x="250" y="{line_y_positions[3] - 10}" text-anchor="middle" class="value">{line_items[3]['value']}</text>
  </g>
  
  <!-- Panel 3: Donut Chart -->
  <g transform="translate(720, 40)">
    <rect width="300" height="520" rx="8" class="panel"/>
    <text x="150" y="40" text-anchor="middle" class="title">{donut_title}</text>
    
    <g transform="translate(150, 250)">
      <circle r="100" fill="transparent" stroke="{donut_items[0]['color']}" stroke-width="60" 
              stroke-dasharray="{donut_lengths[0]} {circumference}" transform="rotate({rotation_angles[0]})"/>
      <circle r="100" fill="transparent" stroke="{donut_items[1]['color']}" stroke-width="60" 
              stroke-dasharray="{donut_lengths[1]} {circumference}" transform="rotate({rotation_angles[1]})"/>
      <circle r="100" fill="transparent" stroke="{donut_items[2]['color']}" stroke-width="60" 
              stroke-dasharray="{donut_lengths[2]} {circumference}" transform="rotate({rotation_angles[2]})"/>
      <text y="5" text-anchor="middle" class="title">100%</text>
    </g>
    
    <g transform="translate(40, 400)">
      <rect x="0" y="0" width="20" height="20" fill="{donut_items[0]['color']}" rx="3"/>
      <text x="30" y="15" class="label">{donut_items[0]['name']}: {donut_items[0]['value']}%</text>
      
      <rect x="0" y="30" width="20" height="20" fill="{donut_items[1]['color']}" rx="3"/>
      <text x="30" y="45" class="label">{donut_items[1]['name']}: {donut_items[1]['value']}%</text>
      
      <rect x="0" y="60" width="20" height="20" fill="{donut_items[2]['color']}" rx="3"/>
      <text x="30" y="75" class="label">{donut_items[2]['name']}: {donut_items[2]['value']}%</text>
    </g>
  </g>
</svg>"""

    return svg


# Fixer Agent - Completely removed Nov 4, 2025

# Configuration
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Application settings"""

    app_name: str = "PersonaSay LangChain API"
    version: str = "2.0.0"
    description: str = "LangChain-based multi-agent persona system with persistent memory"
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")

    class Config:
        env_file = ".env"


# Initialize FastAPI app
app_settings = AppSettings()
app = FastAPI(
    title=app_settings.app_name,
    version=app_settings.version,
    description=app_settings.description,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global LangChain persona manager
langchain_manager: Optional[LangChainPersonaManager] = None

# Fixer agent - Removed


# Pydantic models for API
class ChatRequest(BaseModel):
    """Chat request with LangChain agents"""

    prompt: str = Field(..., description="User message to send to personas")
    personas: List[Dict[str, Any]] = Field(..., description="List of active personas")
    context: Dict[str, Any] = Field(..., description="Product context for the conversation")
    api_key: str = Field(..., description="OpenAI API key")
    session_id: Optional[str] = Field(None, description="Conversation session ID")
    history: Optional[List[Dict[str, Any]]] = Field([], description="Previous conversation history")
    generate_mock: Optional[bool] = Field(
        False, description="Whether to generate SVG mock visualizations"
    )


class SummaryRequest(BaseModel):
    """Summary generation request"""

    context: Dict[str, Any] = Field(..., description="Product context")
    history: List[Dict[str, Any]] = Field(..., description="Conversation history to summarize")
    api_key: str = Field(..., description="OpenAI API key")
    session_id: Optional[str] = Field(None, description="Session ID for context")


class InitializeRequest(BaseModel):
    """Initialize personas request"""

    personas: List[Dict[str, Any]] = Field(..., description="Persona data to initialize")
    api_key: str = Field(..., description="OpenAI API key")


class MemoryRequest(BaseModel):
    """Memory retrieval request"""

    persona_id: str = Field(..., description="Persona ID to get memory for")
    session_id: Optional[str] = Field(None, description="Specific session ID")


class DebateRequest(BaseModel):
    """Multi-agent debate request"""

    topic: str = Field(..., description="Debate topic")
    persona_ids: List[str] = Field(..., description="Personas to participate in debate")
    api_key: str = Field(..., description="OpenAI API key")
    rounds: int = Field(3, description="Number of debate rounds")


# Fixer - Removed


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "PersonaSay LangChain API",
        "version": app_settings.version,
        "description": app_settings.description,
        "framework": "LangChain (langchain.com)",
        "features": [
            "Independent persona agents",
            "Persistent memory with database",
            "Tool-equipped agents",
            "Concurrent processing",
            "Intelligent debugging agent",
            "Automated error fixing",
            "Production-ready deployment",
        ],
        "status": "running",
        "initialized": langchain_manager is not None,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "langchain_initialized": langchain_manager is not None,
        "environment": app_settings.environment,
    }


# Dependency to get LangChain manager
async def get_langchain_manager() -> LangChainPersonaManager:
    """Dependency to ensure LangChain manager is available"""
    global langchain_manager
    if langchain_manager is None:
        raise HTTPException(
            status_code=503,
            detail="LangChain manager not initialized. Call /langchain/initialize first",
        )
    return langchain_manager


# LangChain Persona endpoints
@app.post("/langchain/initialize")
async def initialize_langchain_personas(request: InitializeRequest):
    """Initialize LangChain persona agents with database persistence"""
    global langchain_manager

    try:
        print(f"Initializing LangChain PersonaSay with {len(request.personas)} agents...")

        # Create new LangChain manager
        langchain_manager = LangChainPersonaManager(api_key=request.api_key)

        # Initialize all personas
        langchain_manager.initialize_personas(request.personas)

        return {
            "message": f"Successfully initialized {len(request.personas)} LangChain persona agents",
            "personas": [p["name"] for p in request.personas],
            "framework": "LangChain",
            "features": [
                "persistent_memory",
                "agent_tools",
                "independent_thinking",
                "intelligent_debugging",
            ],
            "database": "enabled",
            "status": "ready",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize LangChain system: {str(e)}"
        )


@app.post("/chat")
async def langchain_chat(request: ChatRequest):
    """
    Main chat endpoint using LangChain agents with auto-initialization
    Each persona thinks independently with persistent memory
    """
    global langchain_manager

    try:
        print(f"LangChain chat request: {request.prompt[:50]}...")
        print(f"👥 Active personas: {[p['name'] for p in request.personas]}")

        # Auto-initialize if not already done
        if langchain_manager is None:
            print("Auto-initializing LangChain personas...")
            langchain_manager = LangChainPersonaManager(api_key=request.api_key)
            langchain_manager.initialize_personas(request.personas)
            print(f"Initialized {len(request.personas)} LangChain persona agents")
            print(f"📋 Initialized persona IDs: {list(langchain_manager.personas.keys())}")

        # Extract persona IDs
        persona_ids = [p["id"] for p in request.personas]
        print(f"Requested persona IDs: {persona_ids}")
        print(f"Available persona IDs: {list(langchain_manager.personas.keys())}")

        # Initialize any missing personas on-the-fly (for @mentions)
        missing_personas = [
            p for p in request.personas if p["id"] not in langchain_manager.personas
        ]
        if missing_personas:
            print(f"Initializing {len(missing_personas)} missing personas...")
            from app.langchain_personas import LangChainPersonaAgent

            for persona_data in missing_personas:
                try:
                    langchain_manager.personas[persona_data["id"]] = LangChainPersonaAgent(
                        persona_data=persona_data,
                        settings=langchain_manager.settings,
                        db_session=langchain_manager.db_session,
                    )
                    print(f"Initialized: {persona_data['name']}")
                except Exception as e:
                    print(f"Failed to initialize {persona_data['name']}: {e}")

        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Get responses from all active personas using LangChain
        responses = await langchain_manager.get_all_responses(
            active_persona_ids=persona_ids,
            user_message=request.prompt,
            product_context=request.context,
            session_id=session_id,
        )

        print(f"Generated {len(responses)} LangChain responses")
        print(f"Mock generation requested: {request.generate_mock}")

        # If mock is requested, generate SVG for each persona response
        if request.generate_mock and responses:
            print(f"Generating SVG mocks for {len(responses)} personas...")
            from langchain_openai import ChatOpenAI

            mock_llm = ChatOpenAI(
                api_key=request.api_key, model="gpt-4o", temperature=0.6, max_tokens=2500
            )

            for i, resp in enumerate(responses):
                persona = next((p for p in request.personas if p["id"] == resp["persona_id"]), None)
                if not persona:
                    continue

                try:
                    # Ask AI for dashboard data (not SVG code) based on persona's analysis
                    prompt_text = f"""Based on this feature analysis, provide dashboard data for visualization:

ANALYSIS:
{resp.get('response', '')[:500]}

Return a JSON object with relevant dashboard data. Make it SPECIFIC to what's being analyzed.

REQUIRED FORMAT:
{{
  "bar_title": "<Chart 1 title relevant to feature>",
  "bar1_name": "<Metric/Category 1>", "bar1_value": <85-99>,
  "bar2_name": "<Metric/Category 2>", "bar2_value": <85-99>,
  "bar3_name": "<Metric/Category 3>", "bar3_value": <85-99>,
  
  "line_title": "<Chart 2 title>",
  "line1_label": "<Point 1>", "line1_value": <number>,
  "line2_label": "<Point 2>", "line2_value": <number>,
  "line3_label": "<Point 3>", "line3_value": <number>,
  "line4_label": "<Point 4>", "line4_value": <number>,
  
  "donut_title": "<Chart 3 title>",
  "donut1_name": "<Segment 1>", "donut1_value": <percent>,
  "donut2_name": "<Segment 2>", "donut2_value": <percent>,
  "donut3_name": "<Segment 3>", "donut3_value": <percent>
}}

EXAMPLE for "Leading & Trailing Odds" feature:
{{
  "bar_title": "Odds Performance",
  "bar1_name": "Leading", "bar1_value": 94.2,
  "bar2_name": "Trailing", "bar2_value": 88.5,
  "bar3_name": "Average", "bar3_value": 91.3,
  
  "line_title": "Event Coverage",
  "line1_label": "Pre-match", "line1_value": 450,
  "line2_label": "Live", "line2_value": 820,
  "line3_label": "In-play", "line3_value": 1250,
  "line4_label": "Total", "line4_value": 1700,
  
  "donut_title": "Accuracy Metrics",
  "donut1_name": "Precision", "donut1_value": 55,
  "donut2_name": "Speed", "donut2_value": 30,
  "donut3_name": "Depth", "donut3_value": 15
}}

Return ONLY valid JSON, no markdown, no explanations."""

                    mock_resp = await mock_llm.ainvoke([{"role": "user", "content": prompt_text}])

                    # Extract and parse JSON
                    json_match = re.search(
                        r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", mock_resp.content, re.DOTALL
                    )
                    if json_match:
                        data = json.loads(json_match.group(0))
                        # Generate SVG using our Python function (perfect quality guaranteed)
                        svg = generate_svg_dashboard(data)
                        responses[i]["mock_svg"] = svg
                        print(f"Mock generated for {persona['name']}")
                    else:
                        print(f"WARNING: No valid JSON found for {persona['name']}")
                        responses[i]["mock_svg"] = None
                except Exception as e:
                    print(
                        f"WARNING: Mock generation failed for {persona.get('name', 'unknown')}: {e}"
                    )
                    responses[i]["mock_svg"] = None

        return {
            "replies": responses,
            "session_id": session_id,
            "framework": "langchain",
            "features_used": ["agent_thinking", "persistent_memory", "tool_usage"]
            + (["svg_mocks"] if request.generate_mock else []),
            "total_personas": len(responses),
            "status": "success",
        }

    except Exception as e:
        print(f"ERROR: LangChain chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.post("/chat-attachments")
async def langchain_chat_with_attachments(
    prompt: str = Form(...),
    personas: str = Form(...),
    context: str = Form(...),
    api_key: str = Form(...),
    history: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    generate_mock: Optional[bool] = Form(False),
):
    """
    Chat endpoint with file attachments (images, documents) using LangChain
    Supports multimodal inputs for visual feedback and document analysis
    """
    global langchain_manager

    try:
        # Parse JSON strings
        parsed_personas: List[Dict[str, Any]] = (
            json.loads(personas) if isinstance(personas, str) else personas
        )
        parsed_context: Dict[str, Any] = (
            json.loads(context) if isinstance(context, str) else context
        )
        parsed_history: List[Dict[str, Any]] = []
        if history:
            try:
                parsed_history = json.loads(history)
            except Exception:
                parsed_history = []

        # Convert generate_mock to boolean if it's a string
        if isinstance(generate_mock, str):
            generate_mock = generate_mock.lower() in ("true", "1", "yes")

        print(f"📎 Chat with attachments: {prompt[:50]}...")
        print(f"📁 Files attached: {len(files)}")
        print(f"👥 Active personas: {[p['name'] for p in parsed_personas]}")
        print(f"Mock generation requested: {generate_mock} (type: {type(generate_mock).__name__})")

        # Auto-initialize if needed
        if langchain_manager is None:
            print("Auto-initializing LangChain personas...")
            langchain_manager = LangChainPersonaManager(api_key=api_key)
            langchain_manager.initialize_personas(parsed_personas)
            print(f"✅ Initialized {len(parsed_personas)} LangChain persona agents")

        # Process attachments - separate images from documents
        image_files = [f for f in files if (f.content_type or "").startswith("image/")]
        doc_snippets: List[str] = []

        for f in files:
            if f in image_files:
                continue
            try:
                raw = f.file.read(64 * 1024)  # read up to 64KB
                snippet = raw.decode("utf-8", errors="ignore")
                if snippet:
                    doc_snippets.append(f"[File: {f.filename}]\n" + snippet[:2000])
            except Exception:
                continue
            finally:
                try:
                    f.file.seek(0)
                except Exception:
                    pass

        # Build conversation history
        formatted_history = ""
        if parsed_history:
            recent = parsed_history[-20:]
            lines = []
            for msg in recent:
                sender_label = msg.get("sender") or (
                    "User" if msg.get("role") == "user" else "Assistant"
                )
                content_text = msg.get("content", "")
                lines.append(f"- {sender_label}: {content_text}")
            formatted_history = "\n".join(lines)

        # Build multimodal message with images
        enhanced_prompt = f"""{prompt}

Conversation history (last 20 messages):
{formatted_history}

Attached document content:
{chr(10).join(doc_snippets) if doc_snippets else "(none)"}
"""

        # For images, we need to use OpenAI directly with vision model
        # since LangChain doesn't yet fully support multimodal in all agent types
        if image_files:
            print(f"Processing {len(image_files)} images with gpt-4o vision...")

            from langchain_openai import ChatOpenAI

            responses = []
            persona_ids = [p["id"] for p in parsed_personas]
            session_id = str(uuid.uuid4())

            for persona_data in parsed_personas:
                try:
                    # Build multimodal content
                    content_parts = [{"type": "text", "text": enhanced_prompt}]

                    for img_file in image_files:
                        try:
                            data = img_file.file.read()
                            if data:
                                b64 = base64.b64encode(data).decode("utf-8")
                                url = f"data:{img_file.content_type};base64,{b64}"
                                content_parts.append(
                                    {"type": "image_url", "image_url": {"url": url}}
                                )
                        except Exception as e:
                            print(f"WARNING: Failed to process image {img_file.filename}: {e}")
                        finally:
                            try:
                                img_file.file.seek(0)
                            except Exception:
                                pass

                    # Use vision model
                    vision_llm = ChatOpenAI(
                        api_key=api_key, model="gpt-4o", temperature=0.85, max_tokens=1500
                    )

                    # System message for persona
                    system_msg = f"""You are {persona_data['name']}, {persona_data.get('title', 'Expert')} at {persona_data.get('company', 'Company')}.

Analyze the attached image(s) and provide your professional feedback from your role's perspective.
Be specific, detailed, and authentic to your role and experience."""

                    messages = [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": content_parts},
                    ]

                    response = await vision_llm.ainvoke(messages)

                    responses.append(
                        {
                            "persona_id": persona_data["id"],
                            "name": persona_data["name"],
                            "response": response.content,
                            "role": persona_data.get("title", "Expert"),
                            "company": persona_data.get("company", "Company"),
                            "avatar": persona_data.get("avatar", ""),
                            "system": "langchain_vision",
                        }
                    )

                    print(f"{persona_data['name']} processed vision request")

                except Exception as e:
                    print(f"ERROR: Error from {persona_data.get('name', 'unknown')}: {e}")
                    responses.append(
                        {
                            "persona_id": persona_data["id"],
                            "name": persona_data["name"],
                            "response": f"I apologize, but I'm having trouble analyzing the image: {str(e)}",
                            "error": True,
                        }
                    )

            # Generate SVG mocks if requested (for image attachments)
            if generate_mock and responses:
                print(f"Generating SVG mocks for {len(responses)} personas (with images)...")
                from langchain_openai import ChatOpenAI

                mock_llm = ChatOpenAI(
                    api_key=api_key, model="gpt-4o", temperature=0.6, max_tokens=2500
                )

                for i, resp in enumerate(responses):
                    persona = next(
                        (p for p in parsed_personas if p["id"] == resp["persona_id"]), None
                    )
                    if not persona:
                        continue

                    try:
                        # Ask AI for dashboard data (not SVG code) based on persona's analysis
                        prompt_text = f"""Based on this feature analysis, provide dashboard data for visualization:

ANALYSIS:
{resp.get('response', '')[:500]}

Return a JSON object with relevant dashboard data. Make it SPECIFIC to what's being analyzed.

REQUIRED FORMAT:
{{
  "bar_title": "<Chart 1 title relevant to feature>",
  "bar1_name": "<Metric/Category 1>", "bar1_value": <85-99>,
  "bar2_name": "<Metric/Category 2>", "bar2_value": <85-99>,
  "bar3_name": "<Metric/Category 3>", "bar3_value": <85-99>,
  
  "line_title": "<Chart 2 title>",
  "line1_label": "<Point 1>", "line1_value": <number>,
  "line2_label": "<Point 2>", "line2_value": <number>,
  "line3_label": "<Point 3>", "line3_value": <number>,
  "line4_label": "<Point 4>", "line4_value": <number>,
  
  "donut_title": "<Chart 3 title>",
  "donut1_name": "<Segment 1>", "donut1_value": <percent>,
  "donut2_name": "<Segment 2>", "donut2_value": <percent>,
  "donut3_name": "<Segment 3>", "donut3_value": <percent>
}}

EXAMPLE for "Leading & Trailing Odds" feature:
{{
  "bar_title": "Odds Performance",
  "bar1_name": "Leading", "bar1_value": 94.2,
  "bar2_name": "Trailing", "bar2_value": 88.5,
  "bar3_name": "Average", "bar3_value": 91.3,
  
  "line_title": "Event Coverage",
  "line1_label": "Pre-match", "line1_value": 450,
  "line2_label": "Live", "line2_value": 820,
  "line3_label": "In-play", "line3_value": 1250,
  "line4_label": "Total", "line4_value": 1700,
  
  "donut_title": "Accuracy Metrics",
  "donut1_name": "Precision", "donut1_value": 55,
  "donut2_name": "Speed", "donut2_value": 30,
  "donut3_name": "Depth", "donut3_value": 15
}}

Return ONLY valid JSON, no markdown, no explanations."""

                        mock_resp = await mock_llm.ainvoke(
                            [{"role": "user", "content": prompt_text}]
                        )

                        # Extract and parse JSON
                        json_match = re.search(
                            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", mock_resp.content, re.DOTALL
                        )
                        if json_match:
                            data = json.loads(json_match.group(0))
                            # Generate SVG using our Python function (perfect quality guaranteed)
                            svg = generate_svg_dashboard(data)
                            responses[i]["mock_svg"] = svg
                            print(f"Mock generated for {persona['name']}")
                        else:
                            print(f"WARNING: No valid JSON found for {persona['name']}")
                            responses[i]["mock_svg"] = None

                    except Exception as e:
                        print(f"⚠️ Mock generation failed for {persona['name']}: {e}")
                        responses[i]["mock_svg"] = None

            return {
                "replies": responses,
                "session_id": session_id,
                "framework": "langchain",
                "features_used": ["multimodal_vision", "image_analysis"]
                + (["svg_mocks"] if generate_mock else []),
                "total_personas": len(responses),
                "status": "success",
            }
        else:
            # No images - use regular LangChain agents
            persona_ids = [p["id"] for p in parsed_personas]
            session_id = str(uuid.uuid4())

            responses = await langchain_manager.get_all_responses(
                active_persona_ids=persona_ids,
                user_message=enhanced_prompt,
                product_context=parsed_context,
                session_id=session_id,
            )

            return {
                "replies": responses,
                "session_id": session_id,
                "framework": "langchain",
                "features_used": ["agent_thinking", "document_analysis"],
                "total_personas": len(responses),
                "status": "success",
            }

    except Exception as e:
        print(f"ERROR: Chat with attachments error: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Attachment processing failed: {str(e)}")


def populate_svg_template(template: str, data: dict) -> str:
    """Populates an SVG template string with data from a dictionary."""

    # Bar Chart Calculations
    max_height = 350
    for i in range(1, 4):
        perf = data.get(f"provider_{i}_perf", 0)
        height = (perf / 100) * max_height
        data[f"provider_{i}_height"] = height
        data[f"provider_{i}_y"] = 450 - height
        data[f"provider_{i}_label_y"] = 440 - height

    # Line Chart Calculations
    latencies = [
        data.get("league_1_latency", 0),
        data.get("league_2_latency", 0),
        data.get("league_3_latency", 0),
    ]
    max_latency = max(latencies) if latencies else 1
    points = []
    for i in range(1, 4):
        cx = 50 + (i - 1) * 120
        latency = data.get(f"league_{i}_latency", 0)
        cy = 350 - ((latency / max_latency) * 200) if max_latency > 0 else 350
        data[f"league_{i}_cx"] = cx
        data[f"league_{i}_cy"] = cy
        data[f"league_{i}_label_y"] = cy + 30
        data[f"league_{i}_data_y"] = cy - 15
        points.append(f"{cx},{cy}")
    data["league_polyline_points"] = " ".join(points)

    # Donut Chart Calculations
    total_percent = sum(data.get(f"metric_{i}_percent", 0) for i in range(1, 4))
    circumference = 628.32
    offset = 0
    for i in range(1, 4):
        percent = data.get(f"metric_{i}_percent", 0)
        normalized_percent = (percent / total_percent) * 100 if total_percent > 0 else 0
        arc = (normalized_percent / 100) * circumference
        data[f"metric_{i}_arc"] = f"{arc}"
        data[f"metric_{i}_rotate"] = (offset / 100) * 360
        offset += normalized_percent

    # Simple string replacement
    for key, value in data.items():
        template = template.replace(f"__{key.upper()}__", str(value))

    return template


def ensure_kpis_in_summary(summary_text: str) -> str:
    """Ensure summary always has KPIs section"""
    has_section_6 = "## 6." in summary_text or "## 6:" in summary_text
    has_kpi_section = "Success Metrics & KPIs" in summary_text

    if has_section_6 or has_kpi_section:
        return summary_text

    # Add KPIs
    kpi_section = "\n\n## 6. Success Metrics & KPIs\n\n**KPI 1: User Engagement Rate**\n- **What to Measure**: Percentage of active users engaging with new features\n- **Target**: Increase from current baseline to 75%\n- **Timeline**: Within 3 months\n- **How to Measure**: Analytics platform tracking feature usage\n- **Type**: Leading indicator\n\n**KPI 2: Implementation Success**\n- **What to Measure**: Percentage of recommendations completed\n- **Target**: 80% completion rate\n- **Timeline**: Within 6 months\n- **How to Measure**: Project management tracking\n- **Type**: Lagging indicator\n\n**KPI 3: User Satisfaction Score**\n- **What to Measure**: Net Promoter Score (NPS) improvement\n- **Target**: Increase NPS by 15 points\n- **Timeline**: Within 4 months\n- **How to Measure**: Quarterly user surveys\n- **Type**: Lagging indicator"

    return summary_text + kpi_section


@app.post("/summary")
async def generate_langchain_summary(
    request: SummaryRequest, manager: LangChainPersonaManager = Depends(get_langchain_manager)
):
    """Generate conversation summary using LangChain"""
    try:
        print("Generating LangChain-powered summary...")

        if not request.history:
            return {"summary": "No conversation history to summarize.", "status": "success"}

        # Create summary prompt
        conversation_text = "\n".join(
            [
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in request.history[-20:]
            ]
        )

        summary_prompt = f"""Analyze this product conversation and provide a comprehensive business summary.

Product Context: {json.dumps(request.context, indent=2)}
Conversation: {conversation_text}

Please structure your summary with these sections:

## Key Insights
Summarize the main feedback and perspectives from different personas.

## Concerns & Opportunities  
List the key concerns raised and opportunities identified.

## Consensus & Disagreements
Note where personas agreed and where they had different views.

## Actionable Recommendations
Provide 3-5 specific, actionable recommendations.

## Next Steps
List 3-5 prioritized next actions with clear owners or timelines.

## Success Metrics & KPIs
Provide 3-4 specific KPIs to measure success of the recommendations and next steps. For each KPI include:
- What to measure (clear metric name)
- Target (specific number or percentage)
- Timeline (when to achieve it)
- How to measure it (tool/method)

Make the KPIs practical and directly tied to the recommendations above."""

        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            api_key=request.api_key,
            model="gpt-4o",
            temperature=0.3,
            max_tokens=2500,  # Ensure enough space for all sections including KPIs
        )

        messages = [
            {
                "role": "system",
                "content": "You are a business analyst. Provide a complete summary with all requested sections, including Success Metrics & KPIs.",
            },
            {"role": "user", "content": summary_prompt},
        ]

        summary_response = await llm.ainvoke(messages)

        # ALWAYS ensure KPIs are included
        final_summary = ensure_kpis_in_summary(summary_response.content)

        print(f"Summary generated ({len(final_summary)} chars, KPIs: {'## 6.' in final_summary})")

        return {
            "summary": final_summary,
            "framework": "langchain",
            "analysis_type": "ai_powered",
            "message_count": len(request.history),
            "status": "success",
        }

    except Exception as e:
        print(f"ERROR: Summary generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


@app.post("/langchain/debate")
async def langchain_debate(
    request: DebateRequest, manager: LangChainPersonaManager = Depends(get_langchain_manager)
):
    """Facilitate multi-round debate between personas using LangChain agents"""
    try:
        print(f"Starting LangChain debate: {request.topic}")
        print(f"👥 Participants: {request.persona_ids}")

        debate_history = []
        session_id = str(uuid.uuid4())

        for round_num in range(request.rounds):
            print(f"Debate round {round_num + 1}")

            round_responses = await manager.get_all_responses(
                active_persona_ids=request.persona_ids,
                user_message=f"Debate topic (Round {round_num + 1}): {request.topic}\n\nPrevious arguments:\n"
                + "\n".join(
                    [
                        f"{msg['name']}: {msg['response']}"
                        for msg in debate_history[-len(request.persona_ids) :]
                    ]
                ),
                product_context={"debate_topic": request.topic, "round": round_num + 1},
                session_id=session_id,
            )

            debate_history.extend(round_responses)

        return {
            "debate_topic": request.topic,
            "rounds": request.rounds,
            "participants": request.persona_ids,
            "debate_history": debate_history,
            "session_id": session_id,
            "framework": "langchain",
            "status": "completed",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debate failed: {str(e)}")


@app.get("/langchain/memory/{persona_id}")
async def get_persona_memory(
    persona_id: str, manager: LangChainPersonaManager = Depends(get_langchain_manager)
):
    """Get persistent memory for a specific persona"""
    try:
        memory_data = manager.get_persona_memory(persona_id)
        return {
            "persona_id": persona_id,
            "memory": memory_data,
            "framework": "langchain",
            "persistence": "database",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory retrieval failed: {str(e)}")


@app.get("/langchain/conversation/{session_id}")
async def get_conversation_history(
    session_id: str, manager: LangChainPersonaManager = Depends(get_langchain_manager)
):
    """Get full conversation history for a session"""
    try:
        history = manager.get_conversation_history(session_id)
        return {
            "session_id": session_id,
            "history": history,
            "framework": "langchain",
            "total_messages": len(history),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")


# Fixer endpoints removed - Nov 3, 2025


@app.post("/langchain/reset")
async def reset_langchain_system():
    """Reset the LangChain persona system"""
    global langchain_manager

    try:
        if langchain_manager:
            langchain_manager.cleanup()
        langchain_manager = None

        return {"message": "LangChain system (personas) reset successfully", "status": "reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System reset failed: {str(e)}")


@app.get("/langchain/stats")
async def get_system_stats(manager: LangChainPersonaManager = Depends(get_langchain_manager)):
    """Get system statistics and status"""
    try:
        stats = {
            "framework": "LangChain (langchain.com)",
            "active_personas": len(manager.personas),
            "persona_names": [persona.name for persona in manager.personas.values()],
            "database_url": manager.settings.database_url,
            "features": [
                "Persistent memory",
                "Independent agent thinking",
                "Tool-equipped personas",
                "Concurrent processing",
                "Database persistence",
                "Intelligent debugging agent",
            ],
            "status": "operational",
        }

        # Fixer agent removed

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when shutting down"""
    global langchain_manager

    if langchain_manager:
        langchain_manager.cleanup()
        print("LangChain persona system cleaned up")

    # Fixer removed


# Development/Testing endpoints
if app_settings.environment == "development":

    @app.get("/dev/test-personas")
    async def create_test_personas():
        """Create test personas for development"""
        test_personas = [
            {
                "id": "alex_trading",
                "name": "Alex",
                "role": "Head of Trading",
                "company": "Tier 1 Sportsbook",
                "avatar": "alex.png",
                "empathy_map": {
                    "think_and_feel": "Focused on risk management and maximizing profitability",
                    "hear": "Market intelligence and competitor analysis",
                    "see": "Real-time odds movements and market patterns",
                    "say_and_do": "Makes strategic trading decisions and manages risk exposure",
                    "pain": "Market inefficiencies and poor data quality affecting decisions",
                    "gain": "Better odds accuracy, reduced risk, increased profitability",
                },
            },
            {
                "id": "ben_analyst",
                "name": "Ben",
                "role": "Performance Analyst",
                "company": "Regional Operator",
                "avatar": "ben.png",
                "empathy_map": {
                    "think_and_feel": "Data-driven and analytical approach to optimization",
                    "hear": "Performance metrics and KPI discussions",
                    "see": "Dashboard data and performance trends",
                    "say_and_do": "Analyzes performance data and recommends improvements",
                    "pain": "Incomplete data and difficulty proving ROI of initiatives",
                    "gain": "Clear performance insights and actionable recommendations",
                },
            },
        ]

        return {
            "test_personas": test_personas,
            "message": "Test personas available for development",
            "count": len(test_personas),
        }


if __name__ == "__main__":
    import uvicorn

    print("Starting PersonaSay LangChain Production Server")
    print("=" * 60)
    print("Framework: LangChain (https://langchain.com/)")
    print("Architecture: Independent persona agents with persistent memory")
    print("Database: SQLAlchemy with persistent conversation storage")
    print("Features: Agent tools, memory persistence, concurrent processing")
    print("=" * 60)

    uvicorn.run(
        "app.server:app",
        host="0.0.0.0",
        port=8000,
        reload=app_settings.debug,
        log_level="info" if not app_settings.debug else "debug",
    )
