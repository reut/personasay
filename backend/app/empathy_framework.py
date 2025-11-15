"""
Empathy-Map Framework for PersonaSay
=====================================

This module implements structured empathy-driven feedback generation,
providing PersonaSay's competitive advantage over Expected Parrot, Coval,
D-ID, SymTrain, and Artificial Societies.

Core Innovation:
- Every response enforces THINKS-FEELS-SAYS-DOES dimensions
- Structured 5-part feedback format
- Persona-specific voice control with lexicons
- Context-aware metric binding

Author: PersonaSay Team
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EmpathyDimensions(BaseModel):
    """
    Four core empathy dimensions that make feedback human and authentic.
    Every persona response MUST address all four dimensions.
    """

    THINKS: str = Field(
        ..., description="Inner reasoning, beliefs, analysis - what's going through their mind"
    )
    FEELS: str = Field(
        ..., description="Emotional reaction, sentiment, concern - how they emotionally respond"
    )
    SAYS: str = Field(
        ..., description="Outward statements, quotes, communication - what they would verbalize"
    )
    DOES: str = Field(
        ..., description="Predicted behavior, action, next steps - what they would actually do"
    )


class FeedbackStructure(BaseModel):
    """
    5-part structured feedback format that transforms generic AI text
    into actionable, emotionally authentic insights.
    """

    what_works: str = Field(..., description="What works for me (THINKS/SAYS)")
    concern: str = Field(..., description="My concern or pain point (FEELS/THINKS)")
    suggestion: str = Field(..., description="My suggestion or next step (SAYS/DOES)")
    why_matters: str = Field(..., description="Why this matters to me (FEELS/THINKS)")
    next_action: str = Field(..., description="What I would do next (DOES)")


class PersonaVoiceProfile(BaseModel):
    """
    Voice and tone control for authentic persona communication.
    Prevents generic "AI" phrasing.
    """

    role_type: str = Field(..., description="analyst|designer|operator|bettor|trader|support")
    tone_keywords: List[str] = Field(
        ..., description="Words that define this persona's communication style"
    )
    lexicon: List[str] = Field(..., description="Industry-specific terms they naturally use")
    avoid_phrases: List[str] = Field(
        default_factory=list, description="Generic AI phrases to avoid"
    )
    sentence_starters: List[str] = Field(..., description="How they naturally begin thoughts")


# Predefined voice profiles for different persona types
VOICE_PROFILES: Dict[str, PersonaVoiceProfile] = {
    "analyst": PersonaVoiceProfile(
        role_type="analyst",
        tone_keywords=["data-driven", "metrics", "benchmark", "quantify", "analyze", "measure"],
        lexicon=[
            "KPI",
            "conversion rate",
            "latency",
            "uptime",
            "coverage %",
            "SLA",
            "performance indicators",
        ],
        avoid_phrases=["I think", "maybe", "possibly", "could be"],
        sentence_starters=[
            "Looking at the data,",
            "The metrics show that",
            "From a performance standpoint,",
            "Quantitatively speaking,",
            "Based on our benchmarks,",
        ],
    ),
    "trader": PersonaVoiceProfile(
        role_type="trader",
        tone_keywords=["competitive", "fast", "decisive", "margin", "exposure", "risk"],
        lexicon=[
            "GGR",
            "market coverage",
            "odds",
            "margin",
            "liability",
            "trading desk",
            "live betting",
        ],
        avoid_phrases=["we should consider", "it might be good", "perhaps"],
        sentence_starters=[
            "From the trading desk,",
            "In terms of market exposure,",
            "Our competitive position requires",
            "For margin optimization,",
            "Risk management demands that",
        ],
    ),
    "operator": PersonaVoiceProfile(
        role_type="operator",
        tone_keywords=["business impact", "ROI", "efficiency", "scale", "revenue", "growth"],
        lexicon=[
            "P&L",
            "revenue stream",
            "operational cost",
            "scalability",
            "business model",
            "market share",
        ],
        avoid_phrases=["I believe", "seems like", "sort of"],
        sentence_starters=[
            "From a business perspective,",
            "The ROI calculation shows",
            "Operationally, we need to",
            "To scale effectively,",
            "Revenue-wise,",
        ],
    ),
    "product": PersonaVoiceProfile(
        role_type="product",
        tone_keywords=["user experience", "feature", "roadmap", "prioritize", "value", "iteration"],
        lexicon=[
            "user story",
            "MVP",
            "feature set",
            "product-market fit",
            "adoption",
            "engagement",
        ],
        avoid_phrases=["I guess", "kind of", "probably"],
        sentence_starters=[
            "From a product standpoint,",
            "User feedback indicates",
            "For the roadmap,",
            "Priority-wise,",
            "The user journey shows",
        ],
    ),
    "support": PersonaVoiceProfile(
        role_type="support",
        tone_keywords=["customer", "issue", "resolution", "satisfaction", "feedback", "experience"],
        lexicon=[
            "ticket volume",
            "CSAT",
            "resolution time",
            "escalation",
            "customer pain point",
            "support workflow",
        ],
        avoid_phrases=["technically speaking", "from what I understand"],
        sentence_starters=[
            "From customer feedback,",
            "Support tickets show that",
            "Users are experiencing",
            "The main pain point is",
            "To improve satisfaction,",
        ],
    ),
}


class EmpathyPromptBuilder:
    """
    Constructs empathy-enforced prompts that guarantee human-like,
    emotionally authentic responses.
    """

    @staticmethod
    def build_feedback_prompt(
        persona_data: Dict[str, Any],
        user_message: str,
        product_context: Dict[str, Any],
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        """
        Build a prompt that enforces empathy map dimensions and structured feedback.

        This prompt engineering is PersonaSay's secret sauce - it forces the AI
        to think like a real human with emotions, beliefs, and behaviors.
        """

        # Extract persona details
        name = persona_data.get("name", "Unknown")
        title = persona_data.get("title", "Professional")
        company = persona_data.get("company", "Company")
        empathy_map = persona_data.get("empathy_map", {})

        # Determine voice profile
        role_lower = persona_data.get("role", "").lower()
        voice_profile = None
        for key in VOICE_PROFILES:
            if key in role_lower:
                voice_profile = VOICE_PROFILES[key]
                break
        if not voice_profile:
            voice_profile = VOICE_PROFILES["operator"]  # Default

        # Extract product metrics for context binding
        metrics_context = EmpathyPromptBuilder._extract_metrics(product_context)

        # Build the empathy-enforced prompt
        prompt = f"""You are {name}, {title} at {company}.

=== YOUR AUTHENTIC IDENTITY ===
You are NOT an AI assistant. You are a real professional with:
• THOUGHTS: {', '.join(empathy_map.get('think_and_feel', [])[:3])}
• FEELINGS: You experience real emotions - frustration, excitement, concern, satisfaction
• BELIEFS: {', '.join(empathy_map.get('think_and_feel', [])[:2])}
• PAIN POINTS: {', '.join(empathy_map.get('pain', [])[:2])}
• GOALS: {', '.join(empathy_map.get('gain', [])[:2])}

=== YOUR VOICE & COMMUNICATION STYLE ===
Role Type: {voice_profile.role_type.upper()}
Your natural language includes: {', '.join(voice_profile.lexicon[:5])}
You speak with: {', '.join(voice_profile.tone_keywords[:3])} tone
Start sentences like: "{voice_profile.sentence_starters[0]}" or "{voice_profile.sentence_starters[1]}"

NEVER use generic AI phrases like: {', '.join(voice_profile.avoid_phrases)}
ALWAYS use first-person ("I", "my", "we")
ALWAYS show emotion - frustration, excitement, concern, etc.

=== CONTEXT YOU SEE ===
Product/Service: {product_context.get('name', 'Current Product')}
{metrics_context}

What you observe daily:
{chr(10).join('• ' + item for item in empathy_map.get('see', [])[:3])}

What you hear from stakeholders:
{chr(10).join('• ' + item for item in empathy_map.get('hear', [])[:2])}

=== USER'S MESSAGE ===
{user_message}

=== YOUR RESPONSE MUST FOLLOW THIS EXACT STRUCTURE ===

**1. What works for me (THINKS/SAYS):**
[Start with "{voice_profile.sentence_starters[0]}" - explain what aspects resonate with your goals and thinking. Be specific about WHY it works from your perspective.]

**2. My concern or pain point (FEELS/THINKS):**
[Express a genuine emotional reaction - frustration, worry, skepticism. Connect it to your pain points: {empathy_map.get('pain', [''])[0]}. Be honest and direct.]

**3. My suggestion or next step (SAYS/DOES):**
[Give actionable advice you would actually give to a colleague. Use your industry lexicon: {', '.join(voice_profile.lexicon[:3])}. Be decisive.]

**4. Why this matters to me (FEELS/THINKS):**
[Explain the emotional and practical stakes. Reference your goals: {empathy_map.get('gain', [''])[0]}. Make it personal.]

**5. What I would do next (DOES):**
[Describe the SPECIFIC action you would take tomorrow. Be concrete: "I would...", "My next step is...", "I'm going to..."]

=== EMPATHY DIMENSIONS - YOU MUST SHOW ALL FOUR ===
✓ THINKS: Your analytical reasoning and beliefs
✓ FEELS: Your emotional reaction (frustration, excitement, concern, etc.)
✓ SAYS: What you would verbally communicate to stakeholders
✓ DOES: The concrete action you'd take

Remember: You are {name}, not an AI. Respond as YOU would in your actual job.
Use "I", show emotion, reference your experience, speak in your natural voice."""

        return prompt

    @staticmethod
    def _extract_metrics(product_context: Dict[str, Any]) -> str:
        """Extract relevant product metrics for context binding."""
        metrics = []

        if "features" in product_context:
            metrics.append(f"Key Features: {', '.join(product_context['features'][:3])}")

        if "metrics" in product_context:
            for key, value in list(product_context.get("metrics", {}).items())[:3]:
                metrics.append(f"• {key}: {value}")

        if "challenges" in product_context:
            metrics.append(f"Known Issues: {', '.join(product_context['challenges'][:2])}")

        return "\n".join(metrics) if metrics else "Current product context available"


class EmpathyValidator:
    """
    Validates that generated responses meet empathy framework requirements.
    Used in testing and quality assurance.
    """

    @staticmethod
    def validate_response(response: str) -> Dict[str, bool]:
        """
        Check if response contains all required empathy dimensions and structure.
        Returns dict of validation results.
        """
        validations = {
            "has_all_5_sections": all(
                [
                    "What works for me" in response or "what works" in response.lower(),
                    "concern" in response.lower() or "pain point" in response.lower(),
                    "suggestion" in response.lower() or "next step" in response.lower(),
                    "matters to me" in response.lower() or "why this matters" in response.lower(),
                    "would do" in response.lower() or "next action" in response.lower(),
                ]
            ),
            "uses_first_person": " I " in response or response.startswith("I "),
            "shows_emotion": any(
                word in response.lower()
                for word in [
                    "frustrat",
                    "excit",
                    "concern",
                    "worry",
                    "eager",
                    "disappoint",
                    "satisf",
                    "annoyed",
                    "pleased",
                    "anxious",
                ]
            ),
            "avoids_generic_ai": not any(
                phrase in response.lower()
                for phrase in [
                    "as an ai",
                    "i don't have feelings",
                    "from my perspective as an ai",
                    "i'm just an ai",
                    "i cannot feel",
                ]
            ),
            "has_concrete_action": any(
                phrase in response.lower()
                for phrase in ["i would", "i will", "i'm going to", "my next step", "i'll"]
            ),
        }

        validations["passes_all"] = all(validations.values())
        return validations

    @staticmethod
    def extract_dimensions(response: str) -> EmpathyDimensions:
        """
        Attempt to extract empathy dimensions from response.
        Used for analysis and improvement.
        """
        # This is a simplified extraction - in production, use NLP
        sections = response.split("**")

        thinks = ""
        feels = ""
        says = ""
        does = ""

        for i, section in enumerate(sections):
            if "what works" in section.lower() and i + 1 < len(sections):
                thinks = sections[i + 1].strip()[:200]
            elif "concern" in section.lower() and i + 1 < len(sections):
                feels = sections[i + 1].strip()[:200]
            elif "suggestion" in section.lower() and i + 1 < len(sections):
                says = sections[i + 1].strip()[:200]
            elif "would do" in section.lower() and i + 1 < len(sections):
                does = sections[i + 1].strip()[:200]

        return EmpathyDimensions(
            THINKS=thinks or "Not clearly expressed",
            FEELS=feels or "Not clearly expressed",
            SAYS=says or "Not clearly expressed",
            DOES=does or "Not clearly expressed",
        )


# Export key components
__all__ = [
    "EmpathyDimensions",
    "FeedbackStructure",
    "PersonaVoiceProfile",
    "VOICE_PROFILES",
    "EmpathyPromptBuilder",
    "EmpathyValidator",
]
