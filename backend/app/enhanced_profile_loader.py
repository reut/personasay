"""
Enhanced Profile Loader for PersonaSay
Loads detailed persona profiles with 5 new fields for Phase 1
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from app.logging_config import get_logger

logger = get_logger(__name__)

# Path to enhanced profiles directory
PERSONAS_DIR = Path(__file__).parent / "personas"


def load_enhanced_profile(persona_id: str) -> Optional[Dict[str, Any]]:
    """
    Load enhanced profile for a persona

    Args:
        persona_id: Persona identifier (e.g., "alex", "ben", "nina")

    Returns:
        Enhanced profile dict or None if not found
    """
    profile_path = PERSONAS_DIR / f"{persona_id}_enhanced.json"

    if not profile_path.exists():
        logger.warning(f"Enhanced profile not found for {persona_id} at {profile_path}")
        return None

    try:
        with open(profile_path, "r") as f:
            profile = json.load(f)

        logger.info(f"Loaded enhanced profile for {persona_id}")
        return profile
    except Exception as e:
        logger.error(f"Error loading enhanced profile for {persona_id}: {e}")
        return None


def merge_with_baseline_persona(
    baseline: Dict[str, Any], enhanced: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge baseline persona data with enhanced profile

    Args:
        baseline: Basic persona data from frontend/config
        enhanced: Enhanced profile from JSON file

    Returns:
        Merged persona data
    """
    # Start with baseline
    merged = baseline.copy()

    # Overlay enhanced fields
    if enhanced:
        # Core fields (override if present)
        for key in ["name", "role", "company", "description"]:
            if key in enhanced:
                merged[key] = enhanced[key]

        # Enhanced fields (add if not present)
        for key in [
            "career_history",
            "industry_awareness",
            "organizational_context",
            "communication_patterns",
            "incentives_and_motivations",
            "response_generation_rules",
        ]:
            if key in enhanced:
                merged[key] = enhanced[key]

        # Empathy map (prefer enhanced, fallback to baseline)
        if "empathy_map" in enhanced:
            merged["empathy_map"] = enhanced["empathy_map"]

        logger.debug(f"Merged enhanced profile into baseline for {merged.get('id', 'unknown')}")

    return merged


def get_persona_data(persona_id: str, baseline_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get complete persona data, merging baseline and enhanced if available

    Args:
        persona_id: Persona identifier
        baseline_data: Optional baseline persona data from frontend

    Returns:
        Complete persona data
    """
    # Load enhanced profile
    enhanced = load_enhanced_profile(persona_id)

    # If no baseline provided, use enhanced only
    if not baseline_data:
        if enhanced:
            return enhanced
        else:
            logger.warning(f"No persona data found for {persona_id}")
            return {"id": persona_id, "name": persona_id.capitalize()}

    # Merge baseline with enhanced
    return merge_with_baseline_persona(baseline_data, enhanced)


def extract_domain_expertise(persona_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract domain expertise for response validator

    Args:
        persona_data: Complete persona data

    Returns:
        Domain expertise dict compatible with ResponseValidator
    """
    domain_expertise = {}

    # Extract terms from communication_patterns
    comm_patterns = persona_data.get("communication_patterns", {})
    terminology = comm_patterns.get("domain_terminology", {})
    terms = terminology.get("terms_i_use_frequently", [])

    if terms:
        domain_expertise["terms_used_frequently"] = terms

    # Extract typical phrases
    baseline_style = comm_patterns.get("baseline_style", {})
    typical_phrases = baseline_style.get("typical_openers", []) + baseline_style.get(
        "typical_closers", []
    )

    if typical_phrases:
        domain_expertise["typical_phrases"] = typical_phrases

    return domain_expertise


def extract_communication_style(persona_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract communication style for response validator

    Args:
        persona_data: Complete persona data

    Returns:
        Communication style dict compatible with ResponseValidator
    """
    comm_patterns = persona_data.get("communication_patterns", {})
    baseline_style = comm_patterns.get("baseline_style", {})

    return {
        "tone": baseline_style.get("tone", "Professional"),
        "typical_phrases": baseline_style.get("typical_openers", [])
        + baseline_style.get("typical_closers", []),
        "vocabulary_level": baseline_style.get("vocabulary_level", "Professional"),
    }


def prepare_for_validator(persona_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare persona data for ResponseValidator

    Args:
        persona_data: Complete persona data

    Returns:
        Validator-compatible persona data
    """
    return {
        "name": persona_data.get("name", "Unknown"),
        "role": persona_data.get("role", "Unknown"),
        "company": persona_data.get("company", "Unknown"),
        "domain_expertise": extract_domain_expertise(persona_data),
        "communication_style": extract_communication_style(persona_data),
        "budget": persona_data.get("organizational_context", {}).get("budget_dynamics", {}),
        "team": persona_data.get("organizational_context", {}).get("team_structure", {}),
    }


def list_available_enhanced_profiles() -> list:
    """
    List all available enhanced profiles

    Returns:
        List of persona IDs with enhanced profiles
    """
    if not PERSONAS_DIR.exists():
        return []

    profiles = []
    for file in PERSONAS_DIR.glob("*_enhanced.json"):
        persona_id = file.stem.replace("_enhanced", "")
        profiles.append(persona_id)

    return profiles


def get_profile_summary(persona_id: str) -> Dict[str, Any]:
    """
    Get summary of enhanced profile (for debugging/testing)

    Args:
        persona_id: Persona identifier

    Returns:
        Profile summary
    """
    profile = load_enhanced_profile(persona_id)

    if not profile:
        return {"error": "Profile not found"}

    return {
        "id": profile.get("id"),
        "name": profile.get("name"),
        "role": profile.get("role"),
        "company": profile.get("company"),
        "has_career_history": "career_history" in profile,
        "has_industry_awareness": "industry_awareness" in profile,
        "has_organizational_context": "organizational_context" in profile,
        "has_communication_patterns": "communication_patterns" in profile,
        "has_incentives": "incentives_and_motivations" in profile,
        "domain_terms_count": len(
            profile.get("communication_patterns", {})
            .get("domain_terminology", {})
            .get("terms_i_use_frequently", [])
        ),
        "typical_phrases_count": len(
            profile.get("communication_patterns", {})
            .get("baseline_style", {})
            .get("typical_openers", [])
        )
        + len(
            profile.get("communication_patterns", {})
            .get("baseline_style", {})
            .get("typical_closers", [])
        ),
        "kpi_count": len(
            profile.get("incentives_and_motivations", {})
            .get("formal_kpis", {})
            .get("measured_quarterly_on", [])
        ),
    }


# Test/Debug function
if __name__ == "__main__":
    # Test loading Alex's profile
    print("Testing Enhanced Profile Loader\n")
    print("=" * 60)

    alex_profile = load_enhanced_profile("alex")
    if alex_profile:
        print("✓ Loaded Alex's profile")
        print(f"  - Name: {alex_profile['name']}")
        print(f"  - Role: {alex_profile['role']}")
        print(f"  - Company: {alex_profile['company']}")
        print(f"  - Has career history: {'career_history' in alex_profile}")
        print(f"  - Has industry awareness: {'industry_awareness' in alex_profile}")
        print(f"  - Has organizational context: {'organizational_context' in alex_profile}")
        print(f"  - Has communication patterns: {'communication_patterns' in alex_profile}")
        print(f"  - Has incentives: {'incentives_and_motivations' in alex_profile}")

        # Test domain expertise extraction
        print("\n" + "=" * 60)
        print("Domain Expertise Extraction:")
        domain = extract_domain_expertise(alex_profile)
        print(f"  - Terms: {len(domain.get('terms_used_frequently', []))} terms")
        if domain.get("terms_used_frequently"):
            print(f"    Examples: {', '.join(domain['terms_used_frequently'][:5])}")
        print(f"  - Phrases: {len(domain.get('typical_phrases', []))} phrases")
        if domain.get("typical_phrases"):
            print(f"    Examples: {domain['typical_phrases'][0][:60]}...")

        # Test validator preparation
        print("\n" + "=" * 60)
        print("Validator-Compatible Data:")
        validator_data = prepare_for_validator(alex_profile)
        print(f"  - Name: {validator_data['name']}")
        print(f"  - Role: {validator_data['role']}")
        print(f"  - Domain expertise present: {bool(validator_data.get('domain_expertise'))}")
        print(f"  - Communication style present: {bool(validator_data.get('communication_style'))}")

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
    else:
        print("✗ Failed to load Alex's profile")

    # List available profiles
    print("\n" + "=" * 60)
    print("Available Enhanced Profiles:")
    profiles = list_available_enhanced_profiles()
    if profiles:
        for pid in profiles:
            summary = get_profile_summary(pid)
            print(f"  - {pid}: {summary.get('name', 'Unknown')} ({summary.get('role', 'Unknown')})")
    else:
        print("  (none)")
