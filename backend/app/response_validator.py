"""
Response Validator for PersonaSay
Ensures persona responses meet quality standards
"""

import re
from typing import Any, Dict, List

from app.logging_config import get_logger

logger = get_logger(__name__)


class ResponseValidator:
    """Validates persona responses for quality and uniqueness"""

    def __init__(self):
        self.min_word_count = 150
        self.max_word_count = 250
        self.target_word_count = 200
        self.min_quality_score = 75

    def validate_response_quality(
        self, response: str, persona_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive quality check for persona responses

        Args:
            response: The generated response text
            persona_data: Persona profile with constraints, terms, phrases

        Returns:
            dict with validation results:
            {
                "passed": bool,
                "score": int (0-100),
                "checks": dict of individual check results,
                "issues": list of failed checks,
                "word_count": int
            }
        """
        checks = {}

        # Check 1: Word count (20 points)
        word_count = len(response.split())
        checks["word_count_in_range"] = self.min_word_count <= word_count <= self.max_word_count
        checks["word_count_optimal"] = abs(word_count - self.target_word_count) <= 25

        # Check 2: Has specific numbers (20 points)
        # Look for: $X, X%, X people, X years, X minutes, X hours
        number_patterns = [
            r"\$[\d,]+K?",  # Money ($25K, $3.2M)
            r"\d+%",  # Percentages (25%, 99.95%)
            r"\d+ (people|person|traders|employees)",  # Team sizes
            r"\d+ (years?|months?|weeks?|days?)",  # Time periods
            r"\d+ (minutes?|hours?)",  # Durations
        ]
        has_numbers = any(
            re.search(pattern, response, re.IGNORECASE) for pattern in number_patterns
        )
        checks["has_specific_numbers"] = has_numbers

        # Check 3: Uses role-specific terminology (25 points)
        domain_terms = persona_data.get("domain_expertise", {}).get("terms_used_frequently", [])
        if domain_terms:
            terms_found = sum(1 for term in domain_terms if term.lower() in response.lower())
            checks["uses_domain_terms"] = terms_found >= 2
            checks["domain_terms_count"] = terms_found
        else:
            checks["uses_domain_terms"] = None  # Can't check without terms list
            checks["domain_terms_count"] = 0

        # Check 4: References constraints (20 points)
        # Look for budget, approval, team size, goals, etc.
        constraint_keywords = [
            "budget",
            "approval",
            "cfo",
            "team",
            "goal",
            "constraint",
            "limit",
            "require",
            "need to justify",
        ]
        has_constraints = any(keyword in response.lower() for keyword in constraint_keywords)
        checks["mentions_constraints"] = has_constraints

        # Check 5: Uses typical phrases (15 points)
        typical_phrases = persona_data.get("communication_style", {}).get("typical_phrases", [])
        if typical_phrases:
            phrases_found = sum(
                1 for phrase in typical_phrases if phrase.lower() in response.lower()
            )
            checks["uses_typical_phrases"] = phrases_found >= 1
            checks["phrases_count"] = phrases_found
        else:
            checks["uses_typical_phrases"] = None
            checks["phrases_count"] = 0

        # Calculate overall score
        score_components = {
            "word_count_in_range": 15 if checks["word_count_in_range"] else 0,
            "word_count_optimal": 5 if checks.get("word_count_optimal") else 0,
            "has_specific_numbers": 20 if checks["has_specific_numbers"] else 0,
            "uses_domain_terms": 25 if checks.get("uses_domain_terms") else 0,
            "mentions_constraints": 20 if checks["mentions_constraints"] else 0,
            "uses_typical_phrases": 15 if checks.get("uses_typical_phrases") else 0,
        }

        # Adjust for missing data (can't penalize if persona doesn't have domain terms)
        total_possible = 100
        if checks["uses_domain_terms"] is None:
            total_possible -= 25
        if checks["uses_typical_phrases"] is None:
            total_possible -= 15

        total_score = sum(score_components.values())
        if total_possible < 100:
            # Normalize score to 0-100 range
            score = (total_score / total_possible) * 100 if total_possible > 0 else 0
        else:
            score = total_score

        # Identify issues
        issues = []
        if not checks["word_count_in_range"]:
            if word_count < self.min_word_count:
                issues.append(f"Too short ({word_count} words, need {self.min_word_count}+)")
            else:
                issues.append(f"Too long ({word_count} words, max {self.max_word_count})")

        if not checks["has_specific_numbers"]:
            issues.append("Missing specific numbers (budget, team size, metrics)")

        if checks["uses_domain_terms"] is False:
            issues.append(f"Only {checks['domain_terms_count']} domain terms (need 2+)")

        if not checks["mentions_constraints"]:
            issues.append("Doesn't reference constraints (budget, approval, goals)")

        if checks["uses_typical_phrases"] is False:
            issues.append(f"Only {checks['phrases_count']} typical phrases (need 1+)")

        passed = score >= self.min_quality_score

        result = {
            "passed": passed,
            "score": round(score, 1),
            "checks": checks,
            "issues": issues,
            "word_count": word_count,
            "score_breakdown": score_components,
        }

        # Log validation results
        if not passed:
            logger.warning(
                f"Response quality check failed: score={score:.1f}, "
                f"word_count={word_count}, issues={issues}"
            )
        else:
            logger.debug(f"Response quality check passed: score={score:.1f}")

        return result

    def calculate_uniqueness_score(
        self, response: str, other_responses: List[str], threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Calculate how unique this response is compared to others

        Args:
            response: The response to check
            other_responses: List of other persona responses to compare against
            threshold: Similarity threshold (0.0-1.0, default 0.7)

        Returns:
            dict with uniqueness results:
            {
                "is_unique": bool,
                "uniqueness_score": float (0.0-1.0),
                "most_similar_score": float,
                "similarities": list of similarity scores
            }
        """
        if not other_responses:
            return {
                "is_unique": True,
                "uniqueness_score": 1.0,
                "most_similar_score": 0.0,
                "similarities": [],
            }

        similarities = []
        for other in other_responses:
            similarity = self._calculate_text_similarity(response, other)
            similarities.append(similarity)

        most_similar = max(similarities) if similarities else 0.0
        uniqueness_score = 1.0 - most_similar
        is_unique = most_similar < threshold

        result = {
            "is_unique": is_unique,
            "uniqueness_score": round(uniqueness_score, 3),
            "most_similar_score": round(most_similar, 3),
            "similarities": [round(s, 3) for s in similarities],
        }

        if not is_unique:
            logger.warning(
                f"Response similarity too high: {most_similar:.1%} " f"(threshold: {threshold:.1%})"
            )

        return result

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate Jaccard similarity between two texts

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0.0-1.0)
        """
        # Convert to lowercase and split into words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        # Remove common stop words that don't indicate similarity
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
        }

        words1 = words1 - stop_words
        words2 = words2 - stop_words

        if not words1 or not words2:
            return 0.0

        # Jaccard similarity: intersection / union
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def get_improvement_suggestions(
        self, validation_result: Dict[str, Any], persona_data: Dict[str, Any]
    ) -> List[str]:
        """
        Generate specific improvement suggestions based on validation results

        Args:
            validation_result: Result from validate_response_quality
            persona_data: Persona profile data

        Returns:
            List of actionable suggestions
        """
        suggestions = []

        checks = validation_result["checks"]
        word_count = validation_result["word_count"]

        # Word count suggestions
        if word_count < self.min_word_count:
            suggestions.append(
                f"Add more detail: expand on constraints, decision criteria, or experience. "
                f"Need {self.min_word_count - word_count} more words."
            )
        elif word_count > self.max_word_count:
            suggestions.append(
                f"Be more concise: remove least critical details. "
                f"Cut {word_count - self.max_word_count} words."
            )

        # Number suggestions
        if not checks["has_specific_numbers"]:
            budget = persona_data.get("budget", {})
            team = persona_data.get("team", {})
            suggestions.append(
                f"Add specific numbers: mention budget (${budget.get('total')}), "
                f"team size ({team.get('size')}), or metrics tracked."
            )

        # Domain terms suggestions
        if checks.get("uses_domain_terms") is False:
            terms = persona_data.get("domain_expertise", {}).get("terms_used_frequently", [])
            if terms:
                suggestions.append(
                    f"Use role-specific terms: include at least 2 from {', '.join(terms[:5])}."
                )

        # Constraints suggestions
        if not checks["mentions_constraints"]:
            suggestions.append(
                "Reference constraints: mention budget limits, approval processes, "
                "team capacity, or current goals."
            )

        # Phrases suggestions
        if checks.get("uses_typical_phrases") is False:
            phrases = persona_data.get("communication_style", {}).get("typical_phrases", [])
            if phrases:
                suggestions.append(
                    f"Use typical phrases: incorporate phrases like '{phrases[0]}' "
                    f"to sound more authentic."
                )

        return suggestions


def validate_persona_response(
    response: str, persona_data: Dict[str, Any], other_responses: List[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to validate a persona response

    Args:
        response: The generated response text
        persona_data: Persona profile data
        other_responses: Optional list of other persona responses for uniqueness check

    Returns:
        Combined validation results
    """
    validator = ResponseValidator()

    # Quality check
    quality = validator.validate_response_quality(response, persona_data)

    # Uniqueness check (if other responses provided)
    uniqueness = None
    if other_responses:
        uniqueness = validator.calculate_uniqueness_score(response, other_responses)

    # Improvement suggestions
    suggestions = validator.get_improvement_suggestions(quality, persona_data)

    return {
        "quality": quality,
        "uniqueness": uniqueness,
        "suggestions": suggestions,
        "overall_passed": quality["passed"] and (uniqueness["is_unique"] if uniqueness else True),
    }
