"""
Debate endpoints for PersonaSay API
"""

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.dependencies import (
    get_langchain_manager,
    get_or_none_langchain_manager,
    set_langchain_manager,
)
from app.langchain_personas import LangChainPersonaAgent, LangChainPersonaManager
from app.logging_config import get_logger
from app.models import DebateRequest
from config.product_config import PRODUCT_SHORT_NAME, COMPANY_INDUSTRY

router = APIRouter(tags=["debate"])
logger = get_logger(__name__)


class DebateRoundRequest(BaseModel):
    """Request for a single debate round"""

    debate_id: str = Field(..., description="Unique debate session ID")
    topic: str = Field(..., description="Debate topic")
    personas: List[Dict[str, Any]] = Field(..., description="Participating personas")
    round_number: int = Field(..., description="Current round number")
    conversation_history: List[Dict[str, Any]] = Field(default=[], description="Previous messages")
    user_message: Optional[str] = Field(None, description="Optional user interjection")


@router.post("/debate/round")
async def debate_round(request: DebateRoundRequest):
    """Execute a single round of debate between personas"""
    try:
        logger.info(f"Debate round {request.round_number} for: {request.topic}")
        logger.debug(f"Participants: {[p['name'] for p in request.personas]}")

        # Get or initialize manager
        langchain_manager = get_or_none_langchain_manager()

        if langchain_manager is None:
            logger.info("Auto-initializing LangChain personas for debate...")
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

        # Initialize any missing personas in debate mode
        missing_personas = [
            p for p in request.personas if p["id"] not in langchain_manager.personas
        ]
        if missing_personas:
            logger.info(f"Initializing {len(missing_personas)} missing personas for debate...")
            for persona_data in missing_personas:
                try:
                    agent = LangChainPersonaAgent(
                        persona_data=persona_data,
                        settings=langchain_manager.settings,
                        db_session=langchain_manager.db_session,
                    )
                    # Reinitialize agent in debate mode
                    agent._initialize_agent(context_mode="debate")
                    langchain_manager.personas[persona_data["id"]] = agent
                    logger.info(f"Initialized {persona_data['name']} in debate mode")
                except Exception as e:
                    logger.error(f"Failed to initialize {persona_data['name']}: {e}")

        # Ensure existing personas are in debate mode
        for persona_id in [p["id"] for p in request.personas]:
            if persona_id in langchain_manager.personas:
                agent = langchain_manager.personas[persona_id]
                if not hasattr(agent, "context_mode") or agent.context_mode != "debate":
                    logger.info(f"Switching {agent.name} to debate mode")
                    agent._initialize_agent(context_mode="debate")

        # Get persona IDs
        persona_ids = [p["id"] for p in request.personas]

        # Build context from conversation history
        history_context = ""
        if request.conversation_history:
            # Get all messages from the current round and previous round
            recent_history = request.conversation_history[-14:]  # More context for better debate
            history_context = "\n\nOTHER PARTICIPANTS' ARGUMENTS:\n" + "\n\n".join(
                [
                    f"**{msg.get('persona_name', 'Unknown')}** ({msg.get('persona_title', 'Participant')}):\n{msg.get('response', '')[:400]}..."
                    for msg in recent_history
                    if msg.get("type") != "user"  # Exclude user messages
                ]
            )

        # Build the debate prompt emphasizing engagement and reaction
        round_instruction = ""
        if request.round_number == 1:
            round_instruction = "This is Round 1. Present your initial position on this topic."
        else:
            round_instruction = f"""This is Round {request.round_number}. You've heard other perspectives above.

CRITICAL DEBATE RULES:
- DO NOT repeat your Round 1 position - you already said that
- REACT to what others said - agree, disagree, challenge, or build on their points
- If someone makes a good argument, acknowledge it and adjust your view
- If you disagree with someone, say so explicitly: "I disagree with [Name] because..."
- Reference specific points from other participants: "While [Name] prioritizes X, I think Y because..."
- Show how your position DIFFERS from or COMPLEMENTS what others said
- If multiple people agree on something, either join the consensus or explain why you're the outlier
- EVOLVE your thinking based on the debate - don't just restate Round 1

You are in a CONVERSATION, not giving isolated speeches. Engage with what others said!"""

        debate_prompt = f"""Debate Topic: {request.topic}
{history_context}

{round_instruction}

{'User interjection: ' + request.user_message if request.user_message else ''}

IDENTITY REMINDER: You are a CUSTOMER/USER from the {COMPANY_INDUSTRY}, NOT a {PRODUCT_SHORT_NAME} employee.
Speak from YOUR company's perspective as someone who uses or evaluates these services."""

        # Get responses from all participants
        responses = await langchain_manager.get_all_responses(
            active_persona_ids=persona_ids,
            user_message=debate_prompt,
            product_context={"debate_topic": request.topic, "round": request.round_number},
            session_id=request.debate_id,
            feature="debate",
            trace_metadata={"round_number": request.round_number, "debate_topic": request.topic}
        )

        logger.info(f"Round {request.round_number} complete with {len(responses)} responses")

        return {
            "round": request.round_number,
            "responses": responses,
            "debate_id": request.debate_id,
            "status": "success",
        }

    except Exception as e:
        logger.error(f"Debate round error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Debate round failed: {str(e)}")


@router.post("/debate/round-with-attachments")
async def debate_round_with_attachments(
    debate_id: str = Form(...),
    topic: str = Form(...),
    personas: str = Form(...),
    round_number: int = Form(...),
    conversation_history: str = Form(default="[]"),
    user_message: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
):
    """Execute a single round of debate with file attachments"""
    try:
        import json

        personas_data = json.loads(personas)
        history = json.loads(conversation_history)

        logger.info(f"Debate round {round_number} with {len(files)} attachments for: {topic}")
        logger.debug(f"Participants: {[p['name'] for p in personas_data]}")

        # Get or initialize manager
        langchain_manager = get_or_none_langchain_manager()

        if langchain_manager is None:
            logger.info("Auto-initializing LangChain personas for debate...")
            # Get API key from backend settings
            from app.models import AppSettings

            app_settings = AppSettings()
            if not app_settings.openai_api_key:
                raise HTTPException(
                    status_code=500, detail="OpenAI API key not configured in backend .env file"
                )
            langchain_manager = LangChainPersonaManager(api_key=app_settings.openai_api_key)
            langchain_manager.initialize_personas(personas_data)
            set_langchain_manager(langchain_manager)

        # Initialize any missing personas in debate mode
        missing_personas = [p for p in personas_data if p["id"] not in langchain_manager.personas]
        if missing_personas:
            logger.info(f"Initializing {len(missing_personas)} missing personas for debate...")
            for persona_data in missing_personas:
                try:
                    agent = LangChainPersonaAgent(
                        persona_data=persona_data,
                        settings=langchain_manager.settings,
                        db_session=langchain_manager.db_session,
                    )
                    # Reinitialize agent in debate mode
                    agent._initialize_agent(context_mode="debate")
                    langchain_manager.personas[persona_data["id"]] = agent
                    logger.info(f"Initialized {persona_data['name']} in debate mode")
                except Exception as e:
                    logger.error(f"Failed to initialize {persona_data['name']}: {e}")

        # Ensure existing personas are in debate mode
        for persona_id in [p["id"] for p in personas_data]:
            if persona_id in langchain_manager.personas:
                agent = langchain_manager.personas[persona_id]
                if not hasattr(agent, "context_mode") or agent.context_mode != "debate":
                    logger.info(f"Switching {agent.name} to debate mode")
                    agent._initialize_agent(context_mode="debate")

        # Get persona IDs
        persona_ids = [p["id"] for p in personas_data]

        # Process attached files
        file_descriptions = []
        if files:
            logger.info(f"Processing {len(files)} attached files...")
            for file in files:
                content = await file.read()
                file_type = file.content_type or "application/octet-stream"

                if file_type.startswith("image/"):
                    # For images, just note them (b64 encoding available if needed)
                    file_descriptions.append(f"[Attached image: {file.filename}]")
                    logger.debug(f"Attached image: {file.filename}")
                else:
                    # For text files, decode content
                    try:
                        text_content = content.decode("utf-8")
                        file_descriptions.append(
                            f"[Attached file: {file.filename}]\n{text_content[:1000]}"
                        )
                        logger.debug(f"Attached document: {file.filename}")
                    except Exception:
                        file_descriptions.append(f"[Attached file: {file.filename} (binary file)]")

        # Build context from conversation history
        history_context = ""
        if history:
            # Get all messages from the current round and previous round
            recent_history = history[-14:]  # More context for better debate
            history_context = "\n\nOTHER PARTICIPANTS' ARGUMENTS:\n" + "\n\n".join(
                [
                    f"**{msg.get('persona_name', 'Unknown')}** ({msg.get('persona_title', 'Participant')}):\n{msg.get('response', '')[:400]}..."
                    for msg in recent_history
                    if msg.get("type") != "user"  # Exclude user messages
                ]
            )

        # Build the debate prompt emphasizing engagement and reaction
        round_instruction = ""
        if round_number == 1:
            round_instruction = "This is Round 1. Present your initial position on this topic."
        else:
            round_instruction = f"""This is Round {round_number}. You've heard other perspectives above.

CRITICAL DEBATE RULES:
- DO NOT repeat your Round 1 position - you already said that
- REACT to what others said - agree, disagree, challenge, or build on their points
- If someone makes a good argument, acknowledge it and adjust your view
- If you disagree with someone, say so explicitly: "I disagree with [Name] because..."
- Reference specific points from other participants: "While [Name] prioritizes X, I think Y because..."
- Show how your position DIFFERS from or COMPLEMENTS what others said
- If multiple people agree on something, either join the consensus or explain why you're the outlier
- EVOLVE your thinking based on the debate - don't just restate Round 1

You are in a CONVERSATION, not giving isolated speeches. Engage with what others said!"""

        # Build the debate prompt with file context
        file_context = "\n\n".join(file_descriptions) if file_descriptions else ""
        debate_prompt = f"""Debate Topic: {topic}
{history_context}

{round_instruction}

{file_context}

{'User interjection: ' + user_message if user_message else ''}

IDENTITY REMINDER: You are a CUSTOMER/USER from the {COMPANY_INDUSTRY}, NOT a {PRODUCT_SHORT_NAME} employee.
Speak from YOUR company's perspective as someone who uses or evaluates these services."""

        # Get responses from all participants
        responses = await langchain_manager.get_all_responses(
            active_persona_ids=persona_ids,
            user_message=debate_prompt,
            product_context={
                "debate_topic": topic,
                "round": round_number,
                "has_attachments": len(files) > 0,
            },
            session_id=debate_id,
            feature="debate",
            trace_metadata={"round_number": round_number, "debate_topic": topic, "has_attachments": len(files) > 0}
        )

        logger.info(f"Round {round_number} complete with {len(responses)} responses")

        return {
            "round": round_number,
            "responses": responses,
            "debate_id": debate_id,
            "status": "success",
        }

    except Exception as e:
        logger.error(f"Debate round with attachments error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Debate round failed: {str(e)}")


@router.post("/langchain/debate")
async def langchain_debate(
    request: DebateRequest, manager: LangChainPersonaManager = Depends(get_langchain_manager)
):
    """Facilitate multi-round debate between personas using LangChain agents"""
    try:
        logger.info(f"Starting LangChain debate: {request.topic}")
        logger.debug(f"Participants: {request.persona_ids}")

        debate_history = []
        session_id = str(uuid.uuid4())

        for round_num in range(request.rounds):
            logger.debug(f"Debate round {round_num + 1}")

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
