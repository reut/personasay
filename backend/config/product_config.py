"""
Product Configuration
=====================
Central configuration for product-specific values used throughout the application.

Customize these values for your product, or set via environment variables.
Default values use LSports BOOST as an example.
"""
import os


# Product Identity
PRODUCT_NAME = os.getenv("PRODUCT_NAME", "BOOST by LSports")
PRODUCT_SHORT_NAME = os.getenv("PRODUCT_SHORT_NAME", "BOOST")
PRODUCT_INDUSTRY = os.getenv("PRODUCT_INDUSTRY", "Sports Betting Analytics")

# Target User/Customer Type
# Used in prompts to describe who the personas represent
USER_TYPE = os.getenv("USER_TYPE", "betting operator")
USER_TYPE_PLURAL = os.getenv("USER_TYPE_PLURAL", "betting operators")

# Company/Business Context
# Describes what kind of companies use your product
COMPANY_INDUSTRY = os.getenv("COMPANY_INDUSTRY", "betting operator industry")


def get_product_context() -> dict:
    """
    Get product configuration as a dictionary.
    
    Returns:
        dict: Product configuration values
    """
    return {
        "product_name": PRODUCT_NAME,
        "product_short_name": PRODUCT_SHORT_NAME,
        "product_industry": PRODUCT_INDUSTRY,
        "user_type": USER_TYPE,
        "user_type_plural": USER_TYPE_PLURAL,
        "company_industry": COMPANY_INDUSTRY,
    }


# Example: To customize for your product, set environment variables:
# export PRODUCT_NAME="MyProduct Platform"
# export PRODUCT_SHORT_NAME="MyProduct"
# export PRODUCT_INDUSTRY="Healthcare Technology"
# export USER_TYPE="healthcare provider"
# export USER_TYPE_PLURAL="healthcare providers"
# export COMPANY_INDUSTRY="healthcare industry"

