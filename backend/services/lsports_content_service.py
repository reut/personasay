"""
DEPRECATED: This module has been renamed.

This file exists for backward compatibility only.
Please update your imports to use the new generic module:

OLD (deprecated):
    from services.lsports_content_service import get_lsports_context

NEW (recommended):
    from services.product_docs_service import get_product_context

The new module is generic and can be configured for any product.
LSports BOOST is provided as the default example configuration.
"""

import warnings
from services.product_docs_service import (
    ProductDocsService,
    ProductDocsConfig,
    ProductFeature,
    get_product_context,
    get_content_stats,
    get_service,
    set_service
)

# Deprecated aliases for backward compatibility
LSportsContentService = ProductDocsService
LSportsFeature = ProductFeature

async def get_lsports_context(force_refresh: bool = False) -> str:
    """
    DEPRECATED: Use get_product_context() instead.
    
    This function is provided for backward compatibility only.
    """
    warnings.warn(
        "get_lsports_context() is deprecated. Use get_product_context() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return await get_product_context(force_refresh)


def get_lsports_service():
    """
    DEPRECATED: Use get_service() instead.
    
    This function is provided for backward compatibility only.
    """
    warnings.warn(
        "get_lsports_service() is deprecated. Use get_service() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return get_service()


# Legacy global instance name
lsports_service = None  # Will be lazily initialized

def _get_legacy_service():
    """Get service instance with legacy variable name"""
    global lsports_service
    if lsports_service is None:
        lsports_service = get_service()
    return lsports_service


__all__ = [
    'LSportsContentService',  # Deprecated alias
    'LSportsFeature',  # Deprecated alias
    'get_lsports_context',  # Deprecated function
    'get_lsports_service',  # Deprecated function
    'lsports_service',  # Deprecated variable
    # New recommended imports:
    'ProductDocsService',
    'ProductDocsConfig',
    'ProductFeature',
    'get_product_context',
    'get_content_stats',
    'get_service',
    'set_service',
]

