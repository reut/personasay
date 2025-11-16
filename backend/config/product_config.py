"""
Product Configuration
=====================
Central configuration for product-specific values used throughout the application.

This is the SINGLE SOURCE OF TRUTH for product information.
Frontend will fetch this via API endpoint.

Customize these values for your product, or set via environment variables.
Default values use LSports BOOST as an example.
"""
import os
from typing import List, Dict, Any


# ============================================================================
# BASIC IDENTITY (Used in system prompts)
# ============================================================================

PRODUCT_NAME = os.getenv("PRODUCT_NAME", "BOOST by LSports")
PRODUCT_SHORT_NAME = os.getenv("PRODUCT_SHORT_NAME", "BOOST")
PRODUCT_TAGLINE = os.getenv("PRODUCT_TAGLINE", "Provider Performance Analytics Platform")
PRODUCT_INDUSTRY = os.getenv("PRODUCT_INDUSTRY", "Sports Betting & iGaming")

# Target User/Customer Type (for system prompts)
USER_TYPE = os.getenv("USER_TYPE", "sportsbook operator")
USER_TYPE_PLURAL = os.getenv("USER_TYPE_PLURAL", "sportsbook operators")
COMPANY_INDUSTRY = os.getenv("COMPANY_INDUSTRY", "sports betting industry")


# ============================================================================
# FULL PRODUCT CONTEXT (Source of truth for AI and UI)
# ============================================================================

PRODUCT_DESCRIPTION = """BOOST is LSports' centralized, data-driven performance analytics platform designed to help sportsbook operators evaluate, compare, and optimize their sportsbook content across multiple providers. It provides full visibility into market coverage, uptime, and pricing competitiveness – empowering trading and operations teams to make smarter, data-backed decisions.

Whether you're identifying coverage gaps, tracking uptime stability, or benchmarking odds against competitors, BOOST delivers clear, actionable insights that help increase profitability, improve efficiency, and stay ahead of the game."""

TARGET_USERS = [
    "Sportsbook Traders & Trading Managers",
    "Product Owners & Product Managers",
    "Performance Analysts & Data Scientists",
    "Operations & Support Teams",
    "Technical Integration Teams",
    "Business Stakeholders & Decision Makers"
]

KEY_FEATURES = [
    "Benchmark Comparison Module: Full comparative view of fixture & market coverage across providers",
    "Measure coverage levels across sports, competitions, fixtures and markets",
    "Identify missing or delayed fixtures and markets per provider",
    "Compare pre-match and in-play coverage availability",
    "Trading Performance Module: Track market uptime (pre-match and in-play)",
    "Compare margins to assess pricing competitiveness",
    "Monitor overall performance to support trading optimization",
    "Intuitive dashboards and comparison tables for analytics and reporting",
    "Export data or generate scheduled reports",
    "Integration with LSports TRADE for market adjustments"
]

PAIN_POINTS = [
    "Difficulty comparing multiple odds feed providers objectively",
    "Coverage gaps leading to customer dissatisfaction",
    "Lack of visibility into provider performance",
    "Manual data collection and reporting is time-consuming",
    "Hard to justify provider costs without performance data",
    "Missed opportunities due to incomplete market coverage",
    "Technical issues not detected until customer complaints",
    "No unified view across multiple providers"
]

VALUE_PROPOSITION = "BOOST provides sportsbook operators with the data transparency and actionable insights needed to optimize provider selection, improve market coverage, enhance pricing competitiveness, and ultimately increase profitability and efficiency."

TECHNICAL_CONTEXT = "BOOST consolidates sports data from multiple providers into a unified analytical layer. For TRADE integrated customers, all subscriptions (fixtures, markets, sports, competitions) are reflected in BOOST with near real-time updates. When coverage gaps or downtime are detected, traders can navigate directly to TRADE to adjust, open, or close markets efficiently."

# Mock generation context (for visual SVG generation)
MOCK_GENERATION_CONTEXT = {
    "domain": "Sports betting operations, sportsbook trading, odds feed providers, sports data analytics",
    "requirements": [
        "Content MUST be relevant to: sports betting, odds providers, fixture coverage, market uptime, settlement data, sports leagues, trading operations",
        "Include: sports-specific metrics (e.g., Premier League coverage 98%, Provider A latency 1.2s, Settlement Success 95%), fixture lists, provider comparisons, market performance data",
        "Make it visually rich, professional, mature, and unique to sports betting analytics",
        "NO placeholder text—show realistic sports betting data (leagues, teams, providers, odds, coverage %)"
    ],
    "example_sports": ["Football/Soccer", "Basketball", "Tennis", "American Football", "Ice Hockey", "Baseball", "Esports"],
    "example_leagues": ["Premier League", "La Liga", "NBA", "NFL", "Champions League", "ATP Tour"],
    "example_providers": ["LSports", "Betradar", "BetGenius", "Kambi", "SBTech"],
    "example_metrics": ["Coverage %", "Uptime", "Latency (ms)", "Settlement Success", "Market Count", "Odds Margin"]
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_product_context() -> Dict[str, Any]:
    """
    Get complete product configuration as a dictionary.
    
    This is used by:
    - API endpoint to serve product config to frontend
    - AI system to enrich persona prompts with product knowledge
    - Summary generation and reporting
    
    Returns:
        dict: Complete product configuration
    """
    return {
        # Basic identity
        "name": PRODUCT_NAME,
        "short_name": PRODUCT_SHORT_NAME,
        "tagline": PRODUCT_TAGLINE,
        "industry": PRODUCT_INDUSTRY,
        
        # Full context
        "description": PRODUCT_DESCRIPTION,
        "target_users": TARGET_USERS,
        "key_features": KEY_FEATURES,
        "pain_points": PAIN_POINTS,
        "value_proposition": VALUE_PROPOSITION,
        "technical_context": TECHNICAL_CONTEXT,
        
        # Mock generation
        "mock_generation_context": MOCK_GENERATION_CONTEXT,
        
        # For system prompts
        "user_type": USER_TYPE,
        "user_type_plural": USER_TYPE_PLURAL,
        "company_industry": COMPANY_INDUSTRY,
    }


def get_system_prompt_context() -> Dict[str, str]:
    """
    Get minimal context for system prompts.
    
    Returns:
        dict: Minimal context for prompts
    """
    return {
        "product_name": PRODUCT_NAME,
        "product_short_name": PRODUCT_SHORT_NAME,
        "product_industry": PRODUCT_INDUSTRY,
        "user_type": USER_TYPE,
        "user_type_plural": USER_TYPE_PLURAL,
        "company_industry": COMPANY_INDUSTRY,
    }


# ============================================================================
# CUSTOMIZATION INSTRUCTIONS
# ============================================================================

# To customize for your product:
#
# Option 1: Edit this file directly
# - Change the default values above
#
# Option 2: Set environment variables
# export PRODUCT_NAME="MyProduct Platform"
# export PRODUCT_SHORT_NAME="MyProduct"
# export PRODUCT_TAGLINE="Your Product Tagline"
# export PRODUCT_INDUSTRY="Your Industry"
# export USER_TYPE="your customer type"
# export USER_TYPE_PLURAL="your customers"
# export COMPANY_INDUSTRY="your industry"
#
# Option 3: Programmatically update (advanced)
# - Import and modify the module-level variables
# - Useful for multi-tenant or dynamic configurations

