"""
Chat endpoints for PersonaSay API
"""

import base64
import json
import re
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from langchain_openai import ChatOpenAI

from app.dependencies import get_or_none_langchain_manager, set_langchain_manager
from app.langchain_personas import LangChainPersonaAgent, LangChainPersonaManager
from app.logging_config import get_logger
from app.models import ChatRequest
from app.svg_generator import generate_svg_dashboard
from app.svg_templates import get_dashboard_template_for_role
from config.product_config import get_product_context

router = APIRouter(tags=["chat"])
logger = get_logger(__name__)


def get_role_specific_metrics(role: str) -> Dict[str, List[str]]:
    """Return role-specific metrics and concerns for personalized dashboards"""
    role_lower = role.lower()

    # Trading/Performance roles
    if any(keyword in role_lower for keyword in ["trading", "trader", "risk", "quant"]):
        return {
            "primary": ["Odds Accuracy", "Profit Margin", "Market Share", "Arbitrage Risk"],
            "secondary": ["Latency", "Trading Volume", "Risk Exposure", "Win Rate"],
            "chart_focus": "real-time performance and risk metrics",
        }

    # Product/Management roles
    elif any(keyword in role_lower for keyword in ["product", "pm", "owner", "manager"]):
        return {
            "primary": ["Feature Adoption", "User Engagement", "NPS Score", "Active Users"],
            "secondary": [
                "Development Velocity",
                "Time to Market",
                "User Retention",
                "Feature Usage",
            ],
            "chart_focus": "user adoption and product metrics",
        }

    # Operations/Support roles
    elif any(keyword in role_lower for keyword in ["operations", "ops", "support", "engineer"]):
        return {
            "primary": ["System Uptime", "Response Time", "Incident Rate", "SLA Compliance"],
            "secondary": ["Team Capacity", "Ticket Volume", "Resolution Time", "Error Rate"],
            "chart_focus": "operational health and team capacity",
        }

    # Data/Analytics roles
    elif any(keyword in role_lower for keyword in ["data", "analytics", "analyst", "scientist"]):
        return {
            "primary": ["Data Quality", "Pipeline Accuracy", "Query Performance", "Model Accuracy"],
            "secondary": [
                "Processing Time",
                "Data Freshness",
                "Coverage Rate",
                "Anomaly Detection",
            ],
            "chart_focus": "data quality and analytical insights",
        }

    # Executive roles
    elif any(
        keyword in role_lower for keyword in ["vp", "director", "executive", "ceo", "cto", "head"]
    ):
        return {
            "primary": ["Revenue Impact", "ROI", "Strategic Alignment", "Team Performance"],
            "secondary": [
                "Cost Efficiency",
                "Market Position",
                "Innovation Index",
                "Customer Satisfaction",
            ],
            "chart_focus": "strategic business outcomes",
        }

    # Default
    else:
        return {
            "primary": ["Performance", "Quality", "Efficiency", "Satisfaction"],
            "secondary": ["Growth", "Stability", "Innovation", "Impact"],
            "chart_focus": "key performance indicators",
        }


@router.post("/chat")
async def langchain_chat(request: ChatRequest):
    """
    Main chat endpoint using LangChain agents with auto-initialization
    Each persona thinks independently with persistent memory
    """
    langchain_manager = get_or_none_langchain_manager()

    try:
        logger.info(f"Chat request received: {request.prompt[:50]}...")
        logger.debug(f"Active personas: {[p['name'] for p in request.personas]}")

        # Auto-initialize if not already done
        if langchain_manager is None:
            logger.info("Auto-initializing LangChain personas...")
            # Get API key from backend settings
            from app.models import AppSettings

            app_settings = AppSettings()
            if not app_settings.openai_api_key:
                raise HTTPException(
                    status_code=500, detail="OpenAI API key not configured in backend .env file"
                )
            langchain_manager = LangChainPersonaManager(api_key=app_settings.openai_api_key)
            langchain_manager.initialize_personas(request.personas)
            set_langchain_manager(langchain_manager)
            logger.info(f"Initialized {len(request.personas)} LangChain persona agents")
            logger.debug(f"Initialized persona IDs: {list(langchain_manager.personas.keys())}")

        # Extract persona IDs
        persona_ids = [p["id"] for p in request.personas]
        logger.debug(f"Requested persona IDs: {persona_ids}")
        logger.debug(f"Available persona IDs: {list(langchain_manager.personas.keys())}")

        # Initialize any missing personas on-the-fly (for @mentions)
        missing_personas = [
            p for p in request.personas if p["id"] not in langchain_manager.personas
        ]
        if missing_personas:
            logger.info(f"Initializing {len(missing_personas)} missing personas...")
            for persona_data in missing_personas:
                try:
                    langchain_manager.personas[persona_data["id"]] = LangChainPersonaAgent(
                        persona_data=persona_data,
                        settings=langchain_manager.settings,
                        db_session=langchain_manager.db_session,
                    )
                    logger.info(f"Initialized: {persona_data['name']}")
                except Exception as e:
                    logger.error(f"Failed to initialize {persona_data['name']}: {e}")

        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Use backend's product config if not provided in request
        product_context = request.context if request.context else get_product_context()

        # Get responses from all active personas using LangChain
        responses = await langchain_manager.get_all_responses(
            active_persona_ids=persona_ids,
            user_message=request.prompt,
            product_context=product_context,
            session_id=session_id,
        )

        logger.info(f"Generated {len(responses)} LangChain responses")
        logger.debug(f"Mock generation requested: {request.generate_mock}")

        # If mock is requested, generate SVG for each persona response
        if request.generate_mock and responses:
            logger.info(f"Generating SVG mocks for {len(responses)} personas...")

            # Get API key from backend settings
            from app.models import AppSettings

            app_settings_mock = AppSettings()

            mock_llm = ChatOpenAI(
                api_key=app_settings_mock.openai_api_key,
                model="gpt-4o",
                temperature=0.6,
                max_tokens=2500,
            )

            for i, resp in enumerate(responses):
                persona = next((p for p in request.personas if p["id"] == resp["persona_id"]), None)
                if not persona:
                    continue

                try:
                    # Extract persona-specific context
                    empathy_map = persona.get("empathy_map", {})
                    pain_points = empathy_map.get("pain", "operational challenges")
                    goals = empathy_map.get("gain", "efficiency improvements")
                    daily_focus = empathy_map.get("see", "day-to-day operations")

                    # Get role-specific metric suggestions
                    persona_role = persona.get("role", persona.get("title", "Expert"))
                    role_metrics = get_role_specific_metrics(persona_role)
                    role_lower = persona_role.lower()

                    # Determine dashboard type and required fields based on role
                    if any(
                        keyword in role_lower for keyword in ["trading", "trader", "risk", "quant"]
                    ):
                        dashboard_type = "Gauge Meters + Line Trend + Risk Indicator"
                        required_format = """{
  "gauge1_label": "<Your primary metric>", "gauge1_value": <85-99>,
  "gauge2_label": "<Your secondary metric>", "gauge2_value": <80-99>,
  "trend1": <value1>, "trend2": <value2>, "trend3": <value3>, "trend4": <value4>,
  "line_title": "<Your trend name>",
  "risk_level": <0.5-5.0>, "risk_label": "<Your risk metric>"
}"""
                    elif any(
                        keyword in role_lower for keyword in ["product", "pm", "owner", "manager"]
                    ):
                        dashboard_type = "User Funnel + Segment Comparison + Satisfaction"
                        required_format = """{
  "funnel1_name": "<Stage 1>", "funnel1_value": <10000>,
  "funnel2_name": "<Stage 2>", "funnel2_value": <5000>,
  "funnel3_name": "<Stage 3>", "funnel3_value": <2500>,
  "funnel4_name": "<Stage 4>", "funnel4_value": <1500>,
  "bar_title": "<Segment comparison title>",
  "bar1_name": "<Segment A>", "bar1_value": <70-90>,
  "bar2_name": "<Segment B>", "bar2_value": <60-85>,
  "satisfaction": <3.5-5.0>
}"""
                    elif any(
                        keyword in role_lower
                        for keyword in ["operations", "ops", "support", "engineer"]
                    ):
                        dashboard_type = (
                            "Status Indicators + System Load Area Chart + Capacity Meters"
                        )
                        required_format = """{
  "uptime": <99.0-100.0>, "incidents": <0-10>, "response_time": <100-500>,
  "load1": <30-80>, "load2": <35-85>, "load3": <40-90>, "load4": <35-80>, "load5": <30-75>,
  "capacity1_name": "<Resource 1>", "capacity1_value": <50-90>,
  "capacity2_name": "<Resource 2>", "capacity2_value": <60-95>,
  "capacity3_name": "<Resource 3>", "capacity3_value": <40-80>
}"""
                    elif any(
                        keyword in role_lower
                        for keyword in ["data", "analytics", "analyst", "scientist"]
                    ):
                        dashboard_type = "Scatter Plot + Heat Map + Distribution Chart"
                        required_format = """{
  "scatter_x0": <val>, "scatter_y0": <val>, ... "scatter_x7": <val>, "scatter_y7": <val>,
  "heatmap_title": "<Your data quality metric>",
  "dist1_range": "<0-20>", "dist1_count": <30-50>,
  "dist2_range": "<20-40>", "dist2_count": <60-90>,
  "dist3_range": "<40-60>", "dist3_count": <80-100>,
  "dist4_range": "<60-80>", "dist4_count": <50-80>,
  "dist5_range": "<80-100>", "dist5_count": <30-60>
}"""
                    else:
                        dashboard_type = "Standard: Bar + Line + Donut"
                        required_format = """{
  "bar_title": "<title>", "bar1_name": "<name>", "bar1_value": <val>, ...
  "line_title": "<title>", "line1_label": "<label>", "line1_value": <val>, ...
  "donut_title": "<title>", "donut1_name": "<name>", "donut1_value": <val>, ...
}"""

                    # Ask AI for dashboard data with strong persona context
                    prompt_text = f"""You are {persona['name']}, {persona_role} at {persona['company']}.

YOUR UNIQUE PERSPECTIVE:
- Your Pain Points: {pain_points}
- Your Goals: {goals}
- What You See Daily: {daily_focus}

YOUR TYPICAL METRICS AS {persona_role}:
- Primary Concerns: {', '.join(role_metrics['primary'])}
- Secondary Metrics: {', '.join(role_metrics['secondary'])}
- Dashboard Focus: {role_metrics['chart_focus']}

YOUR ANALYSIS OF THE FEATURE:
{resp.get('response', '')[:500]}

YOUR UNIQUE DASHBOARD TYPE: {dashboard_type}

As a {persona_role}, you get a UNIQUE dashboard layout that other roles DON'T have.
Create dashboard data showing {role_metrics['chart_focus']} using YOUR specialized visualization.

CRITICAL REQUIREMENTS:
1. Use metrics from YOUR typical concerns list (e.g., {role_metrics['primary'][0]}, {role_metrics['primary'][1]})
2. Use YOUR industry terminology (not generic terms)
3. Values should reflect what YOU see in {daily_focus}
4. This is YOUR unique dashboard type - make it authentic to your role

REQUIRED FORMAT:
{required_format}

Return ONLY valid JSON, no markdown, no explanations.
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
                        # Generate role-specific SVG using specialized templates
                        svg = get_dashboard_template_for_role(persona_role, data)
                        responses[i]["mock_svg"] = svg
                        logger.info(
                            f"Mock generated for {persona['name']} ({persona_role}) - Dashboard type: {dashboard_type}"
                        )
                    else:
                        logger.warning(f"No valid JSON found for {persona['name']}")
                        responses[i]["mock_svg"] = None
                except Exception as e:
                    logger.warning(
                        f"Mock generation failed for {persona.get('name', 'unknown')}: {e}"
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
        logger.error(f"LangChain chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.post("/chat-attachments")
async def langchain_chat_with_attachments(
    prompt: str = Form(...),
    personas: str = Form(...),
    history: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    generate_mock: Optional[bool] = Form(False),
):
    """
    Chat endpoint with file attachments (images, documents) using LangChain
    Supports multimodal inputs for visual feedback and document analysis
    Note: API key is read from backend .env, not from request
    """
    langchain_manager = get_or_none_langchain_manager()

    # Get API key from backend settings
    from app.models import AppSettings

    app_settings_attach = AppSettings()
    if not app_settings_attach.openai_api_key:
        raise HTTPException(
            status_code=500, detail="OpenAI API key not configured in backend .env file"
        )

    try:
        # Parse JSON strings
        parsed_personas: List[Dict[str, Any]] = (
            json.loads(personas) if isinstance(personas, str) else personas
        )
        # Always use backend's product config (never from client)
        parsed_context = get_product_context()
        
        parsed_history: List[Dict[str, Any]] = []
        if history:
            try:
                parsed_history = json.loads(history)
            except Exception:
                parsed_history = []

        # Convert generate_mock to boolean if it's a string
        if isinstance(generate_mock, str):
            generate_mock = generate_mock.lower() in ("true", "1", "yes")

        logger.info(f"Chat with attachments: {prompt[:50]}...")
        logger.debug(f"Files attached: {len(files)}")
        logger.debug(f"Active personas: {[p['name'] for p in parsed_personas]}")
        logger.debug(
            f"Mock generation requested: {generate_mock} (type: {type(generate_mock).__name__})"
        )

        # Auto-initialize if needed
        if langchain_manager is None:
            logger.info("Auto-initializing LangChain personas...")
            langchain_manager = LangChainPersonaManager(api_key=app_settings_attach.openai_api_key)
            langchain_manager.initialize_personas(parsed_personas)
            set_langchain_manager(langchain_manager)
            logger.info(f"Initialized {len(parsed_personas)} LangChain persona agents")

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
            logger.info(f"Processing {len(image_files)} images with gpt-4o vision...")

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
                            logger.warning(f"Failed to process image {img_file.filename}: {e}")
                        finally:
                            try:
                                img_file.file.seek(0)
                            except Exception:
                                pass

                    # Use vision model
                    vision_llm = ChatOpenAI(
                        api_key=app_settings_attach.openai_api_key,
                        model="gpt-4o",
                        temperature=0.85,
                        max_tokens=1500,
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

                    logger.info(f"{persona_data['name']} processed vision request")

                except Exception as e:
                    logger.error(f"Error from {persona_data.get('name', 'unknown')}: {e}")
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
                logger.info(f"Generating SVG mocks for {len(responses)} personas (with images)...")

                mock_llm = ChatOpenAI(
                    api_key=app_settings_attach.openai_api_key,
                    model="gpt-4o",
                    temperature=0.6,
                    max_tokens=2500,
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
                            logger.info(f"Mock generated for {persona['name']}")
                        else:
                            logger.warning(f"No valid JSON found for {persona['name']}")
                            responses[i]["mock_svg"] = None

                    except Exception as e:
                        logger.warning(f"Mock generation failed for {persona['name']}: {e}")
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
        logger.error(f"Chat with attachments error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Attachment processing failed: {str(e)}")
