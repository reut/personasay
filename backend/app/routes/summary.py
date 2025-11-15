"""
Summary generation endpoint for PersonaSay API
"""

import json

from fastapi import APIRouter, HTTPException
from langchain_openai import ChatOpenAI

from app.logging_config import get_logger
from app.models import SummaryRequest
from app.svg_generator import ensure_kpis_in_summary, extract_kpis_as_structured_data

router = APIRouter(tags=["summary"])
logger = get_logger(__name__)


@router.post("/summary")
async def generate_langchain_summary(request: SummaryRequest):
    """Generate conversation summary using LangChain"""
    try:
        logger.info("Generating LangChain-powered summary...")

        if not request.history:
            return {"summary": "No conversation history to summarize.", "status": "success"}

        # Create summary prompt - use ENTIRE conversation history with structure detection
        # Detect discussion rounds (user questions start new rounds)
        rounds = []
        current_round = []
        round_number = 0

        for msg in request.history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # User messages start new rounds
            if role == "user" and current_round:
                round_number += 1
                rounds.append({"round": round_number, "messages": current_round})
                current_round = []

            current_round.append(f"{role}: {content}")

        # Add the last round
        if current_round:
            round_number += 1
            rounds.append({"round": round_number, "messages": current_round})

        # Format conversation with clear round markers
        conversation_text = ""
        for round_data in rounds:
            conversation_text += f"\n{'='*80}\n"
            conversation_text += f"DISCUSSION ROUND {round_data['round']} of {len(rounds)}\n"
            conversation_text += f"{'='*80}\n"
            conversation_text += "\n".join(round_data["messages"])
            conversation_text += "\n"

        logger.info(
            f"Generating summary for {len(request.history)} messages across {len(rounds)} discussion rounds"
        )

        # Get current date for timeline context
        from datetime import datetime

        current_date = datetime.now()
        current_year = current_date.year
        current_quarter = (current_date.month - 1) // 3 + 1

        # Build list of participating personas
        participating_personas = []
        if request.personas:
            participating_personas = [p.get("name", "Unknown") for p in request.personas]
            personas_list = ", ".join(participating_personas)
        else:
            personas_list = "Various personas"

        summary_prompt = f"""Analyze this COMPLETE product conversation and provide a comprehensive business summary.

Product Context: {json.dumps(request.context, indent=2)}

CONVERSATION STRUCTURE:
- Total Messages: {len(request.history)}
- Discussion Rounds: {len(rounds)}
- Participating Personas: {personas_list}

The conversation below is organized into {len(rounds)} DISTINCT DISCUSSION ROUNDS.
Each round is clearly marked with "DISCUSSION ROUND X of {len(rounds)}".

FULL CONVERSATION HISTORY:
{conversation_text}

🚨 CRITICAL INSTRUCTIONS - READ CAREFULLY:
⚠️ The conversation has {len(rounds)} SEPARATE DISCUSSION ROUNDS - you MUST analyze ALL {len(rounds)} rounds equally.
⚠️ DO NOT ignore ROUND 1 - it contains critical initial analysis from all personas.
⚠️ DO NOT focus disproportionately on ROUND {len(rounds)} (the last round) - give equal weight to ALL rounds.
⚠️ Your summary must explicitly mention insights from ROUND 1, ROUND 2{"" if len(rounds) <= 2 else ", ROUND 3"}{", and all subsequent rounds" if len(rounds) > 3 else ""}.

EXAMPLE OF WHAT YOU MUST DO:
- "In Round 1, personas discussed [topic]..."
- "In Round 2, Clara addressed [topic]..."
- "In Round {len(rounds)}, Marco and John [topic]..."

IMPORTANT CONTEXT:
- Current Date: {current_date.strftime('%B %Y')}
- Current Year: {current_year}
- Current Quarter: Q{current_quarter} {current_year}
- Participating Personas: {personas_list}

When creating timelines and dates, use the current date as reference. For example:
- "By end of Q{current_quarter} {current_year}" for near-term goals
- "By end of Q{(current_quarter % 4) + 1} {current_year if current_quarter < 4 else current_year + 1}" for next quarter

Please structure your summary with these sections:

## 1. Key Insights
⚠️ MANDATORY: Organize insights by discussion round. Start with Round 1 and proceed chronologically through all {len(rounds)} rounds.
For EACH round, summarize the main topic and ALL personas who contributed.

Structure like this:
- Round 1: [What was discussed] - Insights from [list all personas who spoke]
- Round 2: [What was discussed] - Insights from [list all personas who spoke]
- Round {len(rounds)}: [What was discussed] - Insights from [list all personas who spoke]

Include perspectives from ALL participating personas ({personas_list}) across ALL {len(rounds)} rounds of discussion.

## 2. Concerns & Opportunities
List ALL key concerns raised and opportunities identified THROUGHOUT THE ENTIRE CONVERSATION, not just from recent messages.

## 3. Consensus & Disagreements
Note where personas agreed and where they had different views ACROSS THE COMPLETE CONVERSATION. Consider perspectives from all {len(participating_personas) if participating_personas else 'participating'} personas throughout all discussion rounds.

## 4. Actionable Recommendations
Provide 3-5 specific, actionable recommendations.

## 5. Next Steps
List 3-5 prioritized next actions with clear owners or timelines.

## 6. Success Metrics & KPIs
Provide 4-5 specific, measurable KPIs directly tied to the recommendations above. For EACH KPI, use this exact format:

**KPI [Number]: [KPI Name]**
- **What to Measure**: [Specific metric with clear definition]
- **Target**: [Specific number, percentage, or measurable goal]
- **Timeline**: [When to achieve this - be specific with dates/duration]
- **How to Measure**: [Specific tool, method, or process to track this]
- **Type**: [Leading/Lagging/Diagnostic indicator]
- **Owner**: [Who is responsible for tracking this KPI]

Make the KPIs practical, measurable, and directly tied to the conversation topics and recommendations. Include both leading indicators (predictive) and lagging indicators (outcome-based)."""

        # Get API key from backend settings
        from app.models import AppSettings

        app_settings = AppSettings()
        if not app_settings.openai_api_key:
            raise HTTPException(
                status_code=500, detail="OpenAI API key not configured in backend .env file"
            )

        llm = ChatOpenAI(
            api_key=app_settings.openai_api_key,
            model="gpt-4o",
            temperature=0.3,
            max_tokens=2500,  # Ensure enough space for all sections including KPIs
        )

        messages = [
            {
                "role": "system",
                "content": f"You are a senior business analyst specializing in KPI development and strategic planning. Today is {current_date.strftime('%B %d, %Y')}. You will receive a conversation organized into {len(rounds)} DISTINCT DISCUSSION ROUNDS with clear round markers. CRITICAL INSTRUCTIONS: You MUST analyze ALL {len(rounds)} rounds with equal importance. DO NOT skip Round 1 or focus only on Round {len(rounds)}. Each round discusses different topics and involves different personas. Your summary must explicitly reference insights from EACH round, starting with Round 1. Organize your Key Insights section by round number. Include ALL personas who participated: {personas_list}. Pay special attention to creating meaningful, measurable KPIs that tie to ALL topics discussed across ALL rounds. Use realistic future dates based on the current date provided. Always include the Success Metrics & KPIs section with at least 4 well-defined KPIs.",
            },
            {"role": "user", "content": summary_prompt},
        ]

        summary_response = await llm.ainvoke(messages)

        # ALWAYS ensure KPIs are included
        final_summary = ensure_kpis_in_summary(summary_response.content)

        # Log KPI presence
        has_kpis = "## 6." in final_summary or "Success Metrics & KPIs" in final_summary
        kpi_count = final_summary.count("**KPI")
        logger.info(
            f"Summary generated ({len(final_summary)} chars, KPIs included: {has_kpis}, KPI count: {kpi_count})"
        )

        # Extract KPIs as structured data for potential programmatic use
        structured_kpis = extract_kpis_as_structured_data(final_summary)
        logger.info(f"Extracted {len(structured_kpis)} structured KPIs")

        return {
            "summary": final_summary,
            "kpis": structured_kpis,  # Structured KPI data for potential frontend use
            "kpi_count": len(structured_kpis),
            "framework": "langchain",
            "analysis_type": "ai_powered",
            "message_count": len(request.history),
            "status": "success",
        }

    except Exception as e:
        logger.error(f"Summary generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")
