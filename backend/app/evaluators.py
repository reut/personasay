"""
Custom evaluators for PersonaSay response quality
Automated quality checks for persona responses
"""

from typing import Dict, Any
from app.logging_config import get_logger

logger = get_logger(__name__)


def evaluate_response_length(response: str) -> Dict[str, Any]:
    """
    Evaluate if response length is within acceptable range (150-250 words)
    
    Args:
        response: The persona's response text
        
    Returns:
        Dict with score (0.0-1.0), word_count, and status
    """
    words = response.split()
    word_count = len(words)
    
    # Ideal range: 150-250 words
    if 150 <= word_count <= 250:
        score = 1.0
        status = "optimal"
    elif 100 <= word_count < 150:
        # Slightly short
        score = 0.8
        status = "acceptable_short"
    elif 250 < word_count <= 300:
        # Slightly long
        score = 0.8
        status = "acceptable_long"
    elif word_count < 100:
        # Too short
        score = 0.5
        status = "too_short"
    else:
        # Too long
        score = 0.5
        status = "too_long"
    
    return {
        "score": score,
        "word_count": word_count,
        "status": status,
        "target_range": "150-250 words"
    }


def evaluate_empathy_compliance(response: str, empathy_map: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Check if response shows empathy framework dimensions
    
    Args:
        response: The persona's response text
        empathy_map: Optional empathy map to check against
        
    Returns:
        Dict with score and detected dimensions
    """
    response_lower = response.lower()
    
    # Check for empathy framework keywords
    dimensions = {
        "thinks": any(word in response_lower for word in ["think", "believe", "consider", "assess"]),
        "feels": any(word in response_lower for word in ["feel", "concern", "worry", "excited", "frustrated"]),
        "sees": any(word in response_lower for word in ["see", "notice", "observe", "experience"]),
        "says_does": any(word in response_lower for word in ["would", "need to", "should", "must", "will"]),
    }
    
    dimensions_present = sum(dimensions.values())
    
    # Score based on number of dimensions present
    if dimensions_present >= 3:
        score = 1.0
        status = "strong_empathy"
    elif dimensions_present == 2:
        score = 0.8
        status = "moderate_empathy"
    elif dimensions_present == 1:
        score = 0.6
        status = "weak_empathy"
    else:
        score = 0.4
        status = "no_empathy_markers"
    
    return {
        "score": score,
        "dimensions_present": dimensions_present,
        "dimensions": dimensions,
        "status": status
    }


def evaluate_role_consistency(response: str, persona_role: str, persona_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Check if response is consistent with persona's role and expertise
    
    Args:
        response: The persona's response text
        persona_role: The persona's role/title
        persona_data: Full persona data including pain points, gains, etc.
        
    Returns:
        Dict with score and consistency indicators
    """
    response_lower = response.lower()
    role_lower = persona_role.lower()
    
    # Role-specific keywords
    role_keywords = {
        "trading": ["trading", "trader", "market", "provider", "uptime", "sla"],
        "product": ["product", "user", "feature", "ux", "experience", "interface"],
        "analyst": ["data", "analysis", "metrics", "kpi", "report", "insight"],
        "risk": ["risk", "compliance", "margin", "liability", "exposure"],
        "commercial": ["roi", "revenue", "cost", "business", "strategy", "value"],
        "support": ["customer", "support", "incident", "ticket", "response"],
    }
    
    # Find relevant keywords for this role
    relevant_keywords = []
    for category, keywords in role_keywords.items():
        if category in role_lower:
            relevant_keywords.extend(keywords)
    
    # Count keyword matches
    matches = sum(1 for keyword in relevant_keywords if keyword in response_lower)
    
    if not relevant_keywords:
        # Unknown role, can't evaluate
        return {
            "score": 0.7,  # Neutral score
            "status": "unknown_role",
            "matches": 0
        }
    
    # Score based on keyword density
    match_ratio = matches / len(relevant_keywords) if relevant_keywords else 0
    
    if match_ratio >= 0.3:
        score = 1.0
        status = "strong_consistency"
    elif match_ratio >= 0.2:
        score = 0.8
        status = "good_consistency"
    elif match_ratio >= 0.1:
        score = 0.6
        status = "moderate_consistency"
    else:
        score = 0.4
        status = "weak_consistency"
    
    return {
        "score": score,
        "matches": matches,
        "total_keywords": len(relevant_keywords),
        "match_ratio": match_ratio,
        "status": status
    }


def evaluate_specificity(response: str) -> Dict[str, Any]:
    """
    Check if response contains specific examples vs generic statements
    
    Args:
        response: The persona's response text
        
    Returns:
        Dict with score and specificity indicators
    """
    response_lower = response.lower()
    
    # Indicators of specificity
    specific_indicators = [
        # Numbers and metrics
        any(char.isdigit() for char in response),
        # Specific examples
        " for example" in response_lower or " e.g." in response_lower or " such as" in response_lower,
        # Concrete nouns (company names, product names, etc.)
        any(word[0].isupper() and word not in ["I", "The", "A", "An"] for word in response.split()),
        # Specific time references
        any(word in response_lower for word in ["yesterday", "last week", "last month", "recently", "currently"]),
        # Quotes or references
        '"' in response or "'" in response,
    ]
    
    specificity_count = sum(specific_indicators)
    
    # Score based on specificity indicators
    if specificity_count >= 3:
        score = 1.0
        status = "highly_specific"
    elif specificity_count == 2:
        score = 0.8
        status = "moderately_specific"
    elif specificity_count == 1:
        score = 0.6
        status = "somewhat_specific"
    else:
        score = 0.4
        status = "generic"
    
    return {
        "score": score,
        "specificity_count": specificity_count,
        "indicators": specific_indicators,
        "status": status
    }


def evaluate_overall_quality(
    response: str,
    persona_role: str = None,
    persona_data: Dict[str, Any] = None,
    empathy_map: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Run all evaluators and compute overall quality score
    
    Args:
        response: The persona's response text
        persona_role: The persona's role/title
        persona_data: Full persona data
        empathy_map: Empathy map data
        
    Returns:
        Dict with overall score and individual evaluation results
    """
    evaluations = {
        "length": evaluate_response_length(response),
        "empathy": evaluate_empathy_compliance(response, empathy_map),
        "specificity": evaluate_specificity(response),
    }
    
    if persona_role:
        evaluations["role_consistency"] = evaluate_role_consistency(response, persona_role, persona_data)
    
    # Compute weighted average
    weights = {
        "length": 0.2,
        "empathy": 0.3,
        "specificity": 0.3,
        "role_consistency": 0.2,
    }
    
    total_score = 0.0
    total_weight = 0.0
    
    for eval_name, eval_result in evaluations.items():
        weight = weights.get(eval_name, 0.25)
        total_score += eval_result["score"] * weight
        total_weight += weight
    
    overall_score = total_score / total_weight if total_weight > 0 else 0.0
    
    return {
        "overall_score": round(overall_score, 2),
        "evaluations": evaluations,
        "status": "excellent" if overall_score >= 0.9 else
                  "good" if overall_score >= 0.75 else
                  "acceptable" if overall_score >= 0.6 else
                  "needs_improvement"
    }


# Optional: LLM-based hallucination detection (requires additional OpenAI call)
async def evaluate_hallucination(
    response: str,
    product_context: Dict[str, Any],
    llm = None
) -> Dict[str, Any]:
    """
    Use LLM to check if response contains facts not in product context
    
    Args:
        response: The persona's response text
        product_context: Product context dictionary
        llm: ChatOpenAI instance (optional, for LLM-based evaluation)
        
    Returns:
        Dict with score and hallucination indicators
    """
    # This is a placeholder for LLM-based hallucination detection
    # In production, you would call an LLM to verify facts
    
    if not llm:
        return {
            "score": 0.8,  # Neutral score without LLM
            "status": "not_evaluated",
            "confidence": "low",
            "note": "LLM-based hallucination detection not configured"
        }
    
    # TODO: Implement LLM-based fact checking
    # Example prompt: "Does this response contain any facts not present in the context?"
    
    return {
        "score": 0.8,
        "status": "not_implemented",
        "confidence": "medium"
    }
