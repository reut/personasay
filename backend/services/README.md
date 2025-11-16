# Product Documentation Service

**Generic service for scraping and caching product documentation to enrich AI persona knowledge.**

---

## Overview

The `product_docs_service.py` provides a hybrid approach to keeping AI personas updated with your product knowledge:

- **Static Content**: Reliable fallback features you define
- **Dynamic Scraping**: Live updates from your documentation
- **Smart Caching**: Configurable refresh intervals
- **Graceful Degradation**: Falls back to static content if scraping fails

---

## Quick Start

### For LSports BOOST Users (Default)

Works out of the box with LSports configuration:

```python
from services.product_docs_service import get_product_context

# Get enriched product context
context = await get_product_context()

# Use in LLM prompts
system_prompt = f"""
You are an AI assistant for BOOST.

{context}

Answer based on the product knowledge above.
"""
```

### For Custom Products

**1. Create Your Configuration**

```python
from services.product_docs_service import ProductDocsConfig, ProductDocsService, set_service

# Configure for your product
my_config = ProductDocsConfig(
    main_docs_url="https://docs.yourproduct.com/features",
    additional_docs_urls=[
        "https://docs.yourproduct.com/api",
        "https://docs.yourproduct.com/integrations"
    ],
    product_name="YourProduct",
    product_industry="Your Industry",
    cache_duration_hours=6,  # Refresh every 6 hours
    heading_tags=['h1', 'h2', 'h3'],  # HTML tags to parse
    description_tag='p'  # Where descriptions are found
)

# Create and set your service
my_service = ProductDocsService(my_config)
set_service(my_service)
```

**2. Customize Static Content**

Edit the `_load_static_content()` method in `product_docs_service.py`:

```python
def _load_static_content(self) -> Dict[str, ProductFeature]:
    """Define your product's core features as fallback"""
    
    static_features = {
        "feature_dashboard": ProductFeature(
            name="Dashboard",
            description="Main control panel with real-time metrics",
            category="core_features",
            source="static",
            last_updated=datetime.now().isoformat(),
            details={
                "url": "https://docs.yourproduct.com/dashboard",
                "capabilities": ["real_time_data", "custom_views"]
            }
        ),
        
        # Add more features...
    }
    
    return static_features
```

**3. Use in Your Application**

```python
from services.product_docs_service import get_product_context

# In your route/service
async def handle_chat(user_message: str):
    # Get latest product knowledge
    product_knowledge = await get_product_context()
    
    # Inject into LLM
    response = await llm.generate(
        system=f"Product Knowledge:\n{product_knowledge}",
        user=user_message
    )
    return response
```

---

## Configuration Options

### ProductDocsConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `main_docs_url` | str | Required | Primary documentation URL to scrape |
| `additional_docs_urls` | List[str] | `[]` | Additional documentation pages |
| `cache_duration_hours` | int | `6` | How often to refresh dynamic content |
| `heading_tags` | List[str] | `['h1','h2','h3','h4']` | HTML tags to extract as features |
| `description_tag` | str | `'p'` | Tag containing feature descriptions |
| `product_name` | str | Required | Your product's name |
| `product_industry` | str | Required | Your product's industry |
| `user_agent` | str | Auto | Custom user agent for HTTP requests |

---

## HTML Parsing Customization

If your documentation has a different HTML structure, adjust the parsing logic:

### Example: Custom Selector

```python
async def _fetch_main_documentation(self) -> Dict[str, Any]:
    # ... existing code ...
    
    # CUSTOMIZE: If your docs use different HTML structure
    # Instead of: headings = soup.find_all(['h1', 'h2', 'h3'])
    
    # Option 1: CSS selectors
    features = soup.select('.feature-card')
    
    # Option 2: Class-based
    features = soup.find_all('div', class_='documentation-item')
    
    # Option 3: Specific structure
    feature_sections = soup.find_all('article', {'data-type': 'feature'})
    
    # Parse each section based on your HTML
    for section in feature_sections:
        title = section.find('h2', class_='feature-title')
        desc = section.find('p', class_='feature-description')
        # ... extract data ...
```

---

## Category Customization

Customize how features are categorized:

```python
def _infer_category(self, feature_name: str) -> str:
    """Infer category based on your product structure"""
    name_lower = feature_name.lower()
    
    # Add your own keywords
    if any(word in name_lower for word in ['api', 'webhook', 'sdk']):
        return 'integrations'
    elif any(word in name_lower for word in ['dashboard', 'report', 'analytics']):
        return 'analytics'
    elif any(word in name_lower for word in ['security', 'auth', 'sso']):
        return 'security'
    # Add more categories...
    else:
        return 'core_features'
```

---

## Monitoring & Debugging

### Get Statistics

```python
from services.product_docs_service import get_content_stats

stats = get_content_stats()
print(f"Total features: {stats['total_features']}")
print(f"Static: {stats['static_features']}")
print(f"Dynamic: {stats['dynamic_features']}")
print(f"Last refresh: {stats['last_refresh']}")
print(f"Cache valid: {stats['cache_valid']}")
```

### Force Refresh

```python
# Force refresh even if cache is valid
context = await get_product_context(force_refresh=True)
```

### Manual Service Control

```python
service = get_service()

# Manual refresh
success = await service.refresh_dynamic_content()

# Get raw content
raw_content = service.get_merged_content()

# Check cache status
needs_refresh = service._should_refresh_cache()
```

---

## Testing

Test your configuration:

```bash
# From backend directory
cd backend
source venv/bin/activate

# Run the service directly
python services/product_docs_service.py
```

This will:
1. Scrape your documentation
2. Show all features found
3. Display statistics
4. Print formatted context

---

## Example: Complete Custom Setup

```python
# File: backend/services/my_product_config.py

from services.product_docs_service import ProductDocsConfig, ProductDocsService, set_service

def initialize_my_product_service():
    """Initialize service with custom product configuration"""
    
    config = ProductDocsConfig(
        # Your documentation URLs
        main_docs_url="https://docs.myapp.com/features",
        additional_docs_urls=[
            "https://docs.myapp.com/api",
            "https://docs.myapp.com/integrations"
        ],
        
        # Product metadata
        product_name="MyApp",
        product_industry="Project Management",
        
        # Refresh settings
        cache_duration_hours=12,  # Refresh twice daily
        
        # HTML parsing (if your docs use different structure)
        heading_tags=['h2', 'h3'],  # Only h2 and h3
        description_tag='div',  # Descriptions in divs
    )
    
    service = ProductDocsService(config)
    set_service(service)
    
    return service

# In your app startup:
initialize_my_product_service()
```

---

## Troubleshooting

### Scraping Returns Empty

**Problem**: `get_product_context()` only shows static features

**Solutions**:
1. Check URL is accessible: `curl https://your-docs-url.com`
2. Check HTML structure matches your selectors
3. Enable debug logging: `logging.getLogger('product_docs_service').setLevel(logging.DEBUG)`
4. Verify SSL settings if using HTTPS

### Categories Wrong

**Problem**: Features categorized incorrectly

**Solution**: Customize `_infer_category()` with your product's keywords

### Parse Errors

**Problem**: BeautifulSoup parsing errors

**Solutions**:
1. Check HTML is valid
2. Try different parser: `BeautifulSoup(content, 'lxml')` or `'html5lib'`
3. Inspect actual HTML: `print(soup.prettify())`

---

## Backward Compatibility

Old LSports-specific imports still work but are deprecated:

```python
# OLD (deprecated but works)
from services.lsports_content_service import get_lsports_context
context = await get_lsports_context()

# NEW (recommended)
from services.product_docs_service import get_product_context
context = await get_product_context()
```

---

## Integration with PersonaSay

How to inject product context into persona prompts:

```python
# In langchain_personas.py
from services.product_docs_service import get_product_context

async def think_and_respond(self, user_message: str, ...):
    # Get product knowledge
    product_knowledge = await get_product_context()
    
    # Inject into prompt
    messages = [
        {"role": "system", "content": self.system_prompt},
        {"role": "user", "content": f"""
            Product Context:
            {product_knowledge}
            
            User Question: {user_message}
        """}
    ]
    # ... generate response
```

---

## Contributing

When adding features to this service:

1. **Keep it generic** - Use parameter names that work for any product
2. **Document clearly** - Add comments explaining customization points
3. **Test with examples** - Include example configurations
4. **Handle errors gracefully** - Fall back to static content

---

## Support

- **Issues**: Report bugs specific to documentation scraping
- **Questions**: Ask in GitHub Discussions
- **Examples**: Share your configurations in the community!

---

For questions or issues, please open a GitHub issue or discussion.
