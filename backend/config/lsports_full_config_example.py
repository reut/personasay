"""
Example: How to scrape ALL LSports products (BOOST, TRADE, DEFEND, etc.)

This configuration scrapes multiple LSports product documentation pages
to give personas comprehensive knowledge of the entire LSports platform.
"""

from services.product_docs_service import ProductDocsConfig, ProductDocsService, set_service

def init_full_lsports_service():
    """
    Initialize service to scrape ALL LSports products.
    
    This will give personas knowledge of:
    - BOOST (Provider Performance Analytics)
    - TRADE (Trading platform)
    - DEFEND (Risk management)
    - Intelligence (Data insights)
    - And any other LSports products
    """
    
    config = ProductDocsConfig(
        # Main documentation - BOOST (most relevant for personas)
        main_docs_url="https://docs.lsports.eu/lsports/boost",
        
        # Additional LSports products to scrape
        additional_docs_urls=[
            # Data catalog
            "https://files.lsports.eu/",
            
            # Other LSports products (add as needed)
            # "https://docs.lsports.eu/lsports/trade",      # Trading platform
            # "https://docs.lsports.eu/lsports/defend",     # Risk management
            # "https://docs.lsports.eu/lsports/intelligence", # Data insights
            
            # You can add more product URLs here
            # Each URL will be scraped separately
        ],
        
        # Refresh every 6 hours
        cache_duration_hours=6,
        
        # Product metadata
        product_name="LSports Platform (Full Suite)",
        product_industry="Sports Betting Data & Analytics",
        
        # HTML parsing configuration
        heading_tags=['h1', 'h2', 'h3', 'h4'],
        description_tag='p'
    )
    
    service = ProductDocsService(config)
    set_service(service)
    
    print("✅ Configured to scrape full LSports platform documentation:")
    print(f"   Main: {config.main_docs_url}")
    print(f"   Additional: {len(config.additional_docs_urls)} sources")
    print(f"   Cache: {config.cache_duration_hours} hours")
    
    return service

# Usage in your app startup (e.g., in main.py or dependencies.py):
# from config.lsports_full_config_example import init_full_lsports_service
# init_full_lsports_service()

