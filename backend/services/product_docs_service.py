"""
Product Documentation Service - Generic Template
================================================
Hybrid service for scraping and caching product documentation.

CUSTOMIZE FOR YOUR PRODUCT:
1. Create a ProductDocsConfig with your documentation URLs
2. Modify _load_static_content() with your product features
3. Adjust HTML parsing selectors if needed for your site structure
4. Configure refresh interval based on your documentation update frequency
5. Enable/configure recursive crawling to automatically discover subpages

This service combines:
- Static fallback content (reliable baseline)
- Dynamic web scraping (live documentation updates)
- **NEW: Recursive link following** (automatically discovers subpages)
- Smart caching (configurable refresh intervals)
- Graceful degradation (falls back to static if scraping fails)

NEW FEATURE: RECURSIVE CRAWLING
- Set follow_links=True to automatically discover and crawl subpages
- Configure max_depth to control how deep to crawl (default: 2 levels)
- Use link_pattern to filter which links to follow (regex)
- Set max_pages as a safety limit (default: 50 pages)

EXAMPLE: LSports BOOST (Default Configuration)
This implementation uses LSports BOOST as an example.
Replace URLs and content with your own product documentation.
"""

import asyncio
import aiohttp
import ssl
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

# Import product configuration
from config.product_config import MAIN_DOCS_URL, PRODUCT_NAME, PRODUCT_INDUSTRY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProductFeature:
    """
    Represents a single product feature or capability.
    
    CUSTOMIZE: Add additional fields as needed for your product.
    """
    name: str
    description: str
    category: str  # e.g., 'core_features', 'integrations', 'analytics', 'api'
    source: str    # 'static', 'dynamic', or 'hybrid'
    last_updated: str
    details: Dict[str, Any] = None


class ProductDocsConfig:
    """
    Configuration for product documentation sources.
    
    CUSTOMIZE THIS CLASS:
    Create an instance with your own documentation URLs and settings.
    
    EXAMPLE:
        config = ProductDocsConfig(
            main_docs_url="https://docs.yourproduct.com",
            additional_docs_urls=["https://docs.yourproduct.com/api"],
            product_name="YourProduct",
            product_industry="Your Industry"
        )
    """
    
    def __init__(
        self,
        # Main documentation URL (REQUIRED - replace with your docs URL)
        main_docs_url: str = MAIN_DOCS_URL,
        
        # Additional documentation sources (optional)
        additional_docs_urls: List[str] = None,
        
        # Cache configuration
        cache_duration_hours: int = 6,
        
        # HTML parsing selectors (customize for your HTML structure)
        heading_tags: List[str] = None,
        description_tag: str = "p",
        
        # Product-specific metadata
        product_name: str = PRODUCT_NAME,
        product_industry: str = PRODUCT_INDUSTRY,
        
        # User agent for HTTP requests
        user_agent: str = None,
        
        # Recursive crawling configuration (NEW FEATURE!)
        follow_links: bool = True,
        max_depth: int = 2,
        link_pattern: str = None,
        max_pages: int = 50,
    ):
        """
        Initialize documentation configuration.
        
        Args:
            main_docs_url: Primary documentation URL to scrape
            additional_docs_urls: List of additional documentation pages
            cache_duration_hours: How often to refresh dynamic content
            heading_tags: HTML tags to extract as feature names
            description_tag: HTML tag containing feature descriptions
            product_name: Your product's name (used in logs and context)
            product_industry: Your product's industry (added to context)
            user_agent: Custom user agent for requests
            
            # RECURSIVE CRAWLING (NEW FEATURE!)
            follow_links: Whether to automatically follow internal links (default: True)
            max_depth: Maximum depth to crawl (0 = only start URL, 1 = one level deep, etc.)
            link_pattern: Regex pattern for links to follow (e.g., r'/product/docs/.*')
                         If None, follows all links within the same domain and path prefix
            max_pages: Maximum number of pages to crawl (safety limit to prevent infinite loops)
        """
        self.main_docs_url = main_docs_url
        self.additional_docs_urls = additional_docs_urls or []
        self.cache_duration_hours = cache_duration_hours
        self.heading_tags = heading_tags or ['h1', 'h2', 'h3', 'h4']
        self.description_tag = description_tag
        self.product_name = product_name
        self.product_industry = product_industry
        self.user_agent = user_agent or f"{product_name.replace(' ', '-')}-Documentation-Scraper/1.0"
        
        # Recursive crawling settings
        self.follow_links = follow_links
        self.max_depth = max_depth
        self.link_pattern = link_pattern
        self.max_pages = max_pages


class ProductDocsService:
    """
    Generic product documentation service with hybrid static/dynamic content.
    
    USAGE:
        # 1. Create config
        config = ProductDocsConfig(
            main_docs_url="https://docs.yourproduct.com",
            product_name="YourProduct"
        )
        
        # 2. Create service
        service = ProductDocsService(config)
        
        # 3. Get enriched context for AI prompts
        context = await service.get_product_context()
    
    FEATURES:
    - Automatically scrapes your documentation
    - Caches results to minimize requests
    - Falls back to static content if scraping fails
    - Provides formatted context ready for LLM prompts
    """
    
    def __init__(self, config: ProductDocsConfig = None):
        """
        Initialize the service with configuration.
        
        Args:
            config: ProductDocsConfig instance. If None, uses default (LSports) config.
                    For your product, always provide a custom config!
        """
        self.config = config or self._get_default_config()
        self.cache_duration = timedelta(hours=self.config.cache_duration_hours)
        self.last_fetch = None
        self.dynamic_content = {}
        self.static_content = self._load_static_content()
        self.session = None
        
        logger.info(f"Initialized ProductDocsService for '{self.config.product_name}'")
        logger.info(f"   Main docs: {self.config.main_docs_url}")
        logger.info(f"   Cache duration: {self.config.cache_duration_hours} hours")
    
    def _get_default_config(self) -> ProductDocsConfig:
        """
        Default configuration using LSports BOOST as an example.
        
        FOR YOUR PRODUCT:
        - Don't rely on this default
        - Create your own ProductDocsConfig
        - Pass it when initializing ProductDocsService
        
        EXAMPLE (replace with your URLs and product info):
        """
        return ProductDocsConfig(
            main_docs_url=MAIN_DOCS_URL,
            additional_docs_urls=[],
            cache_duration_hours=6,
            product_name=PRODUCT_NAME,
            product_industry=PRODUCT_INDUSTRY,
            # Recursive crawling (NEW!)
            follow_links=True,
            max_depth=2,
            link_pattern=None,  # Will follow links within same domain
            max_pages=50
        )
    
    def _load_static_content(self) -> Dict[str, ProductFeature]:
        """
        Load static product features as reliable fallback.
        
        IMPORTANT: CUSTOMIZE THIS METHOD FOR YOUR PRODUCT!
        
        Replace the features below with your own product's features.
        These serve as a fallback if dynamic scraping fails.
        
        STRUCTURE:
            {
                "feature_key": ProductFeature(
                    name="Feature Name",
                    description="What this feature does",
                    category="core_features|integrations|analytics|monitoring|...",
                    source="static",
                    last_updated=datetime.now().isoformat(),
                    details={"any": "additional", "info": "you want"}
                )
            }
        
        EXAMPLE: LSports BOOST features (replace with yours)
        """
        
        # ========================================================================
        # CUSTOMIZE: Replace these features with your own product features
        # ========================================================================
        
        static_features = {
            # Core Features
            "main_platform": ProductFeature(
                name="BOOST Platform",
                description="Main monitoring screen for tracking fixtures, providers, and markets with real-time status updates",
                category="core_features",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "url": "https://monitoring.lsports.eu",
                    "key_features": ["fixture_monitoring", "provider_filtering", "sports_bar", "real_time_updates"]
                }
            ),
            
            "coverage_hub": ProductFeature(
                name="Coverage Hub",
                description="Provider rankings and coverage analysis for optimal provider selection across sports, leagues, and markets",
                category="analytics",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "reports": ["markets", "livescore", "settlement"],
                    "features": ["provider_rankings", "fixture_coverage", "hierarchy_filtering"]
                }
            ),
            
            "settlement_coverage": ProductFeature(
                name="Settlement Coverage",
                description="Historical settlement reliability data with Yes/No indicators based on 12 months and 30 recent fixtures",
                category="analytics",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "data_period": "12_months",
                    "fixture_sample": "30_recent",
                    "indicators": ["yes_no_settlement", "last_supported", "market_level"]
                }
            ),
            
            "livescore_coverage": ProductFeature(
                name="Livescore Coverage",
                description="Incident-level data analysis for recent matches showing livescore support quality per league",
                category="analytics",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "metrics_basis": "30_fixtures_12_months",
                    "scope": "incident_level",
                    "evaluation": "league_support_level"
                }
            ),
            
            # Monitoring Features
            "provider_monitoring": ProductFeature(
                name="Provider Monitoring",
                description="Real-time comparison of multiple providers' performance, reliability, and coverage",
                category="monitoring",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "comparison_types": ["performance", "reliability", "coverage"],
                    "real_time": True
                }
            ),
            
            "market_monitoring": ProductFeature(
                name="Market Monitoring",
                description="Market-level monitoring and filtering capabilities for detailed market analysis",
                category="monitoring",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "granularity": "market_level",
                    "capabilities": ["monitoring", "filtering", "analysis"]
                }
            ),
            
            # Data Features
            "data_feeds": ProductFeature(
                name="Data Feeds",
                description="Real-time PreMatch and InPlay data including incidents, fixtures, leagues, and odds",
                category="data_sources",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "feed_types": ["real_time", "prematch", "inplay"],
                    "data_types": ["incidents", "fixtures", "leagues", "odds"]
                }
            ),
            
            "premium_data": ProductFeature(
                name="Premium Data",
                description="Advanced player props and betting markets data for enhanced experiences",
                category="data_sources",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "data_types": ["player_props", "advanced_betting"],
                    "purpose": "enhanced_experience"
                }
            ),
        }
        
        logger.info(f"Loaded {len(static_features)} static features for {self.config.product_name}")
        return static_features
    
    async def _create_session(self):
        """Create aiohttp session if not exists"""
        if self.session is None:
            # SSL context configuration (adjust if needed)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=10),
                headers={'User-Agent': self.config.user_agent}
            )
    
    async def _close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """
        Extract all links from HTML page.
        
        Args:
            soup: BeautifulSoup parsed HTML
            base_url: Base URL for resolving relative links
            
        Returns:
            Set of absolute URLs
        """
        links = set()
        
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            
            # Skip anchors, javascript, and mailto links
            if href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Remove fragments and query params for consistency
            parsed = urlparse(absolute_url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            # Remove trailing slash for consistency
            clean_url = clean_url.rstrip('/')
            
            links.add(clean_url)
        
        return links
    
    def _is_valid_link(self, url: str, start_url: str) -> bool:
        """
        Check if a link should be followed based on configuration.
        
        Args:
            url: URL to check
            start_url: Starting URL for crawl
            
        Returns:
            True if link should be followed
        """
        parsed_url = urlparse(url)
        parsed_start = urlparse(start_url)
        
        # Must be same domain
        if parsed_url.netloc != parsed_start.netloc:
            return False
        
        # If link pattern specified, must match
        if self.config.link_pattern:
            if not re.search(self.config.link_pattern, parsed_url.path):
                return False
        else:
            # Default: must be within the same path prefix
            # e.g., if start is /product/docs, only follow /product/docs/*
            start_path_parts = parsed_start.path.rstrip('/').split('/')
            url_path_parts = parsed_url.path.rstrip('/').split('/')
            
            # URL path must start with the same path prefix
            if len(url_path_parts) < len(start_path_parts):
                return False
            
            for i, part in enumerate(start_path_parts):
                if i >= len(url_path_parts) or url_path_parts[i] != part:
                    return False
        
        return True
    
    async def _fetch_page_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and parse a single page.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with page content and links, or None if failed
        """
        try:
            await self._create_session()
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Extract features from this page
                    features = {}
                    headings = soup.find_all(self.config.heading_tags)
                    
                    for heading in headings:
                        if heading.text and len(heading.text.strip()) > 3:
                            feature_name = heading.text.strip()
                            
                            # Get description from next paragraph
                            description = ""
                            next_elem = heading.find_next_sibling(self.config.description_tag)
                            if next_elem:
                                description = next_elem.get_text().strip()
                            
                            # Filter out navigation/meta content
                            if len(description) > 20 and not self._is_navigation_content(description):
                                feature_key = self._create_feature_key(feature_name)
                                features[feature_key] = {
                                    'name': feature_name,
                                    'description': description,
                                    'category': self._infer_category(feature_name),
                                    'source': 'dynamic',
                                    'last_updated': datetime.now().isoformat(),
                                    'source_url': url
                                }
                    
                    # Extract links from this page
                    links = self._extract_links(soup, url)
                    
                    return {
                        'features': features,
                        'links': links,
                        'url': url
                    }
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    async def _crawl_recursively(
        self, 
        start_url: str, 
        max_depth: int,
        visited: Set[str] = None,
        depth: int = 0
    ) -> Dict[str, Any]:
        """
        Recursively crawl documentation pages.
        
        Args:
            start_url: URL to start crawling from
            max_depth: Maximum depth to crawl
            visited: Set of already visited URLs (for recursion tracking)
            depth: Current depth (for recursion tracking)
            
        Returns:
            Dictionary of all discovered features
        """
        if visited is None:
            visited = set()
        
        all_features = {}
        
        # Check if we should stop
        if depth > max_depth:
            return all_features
        
        if len(visited) >= self.config.max_pages:
            logger.warning(f"Reached max_pages limit ({self.config.max_pages}), stopping crawl")
            return all_features
        
        if start_url in visited:
            return all_features
        
        # Mark as visited
        visited.add(start_url)
        
        # Fetch this page
        logger.info(f"Crawling [{depth}/{max_depth}]: {start_url}")
        page_data = await self._fetch_page_content(start_url)
        
        if not page_data:
            return all_features
        
        # Add features from this page
        all_features.update(page_data['features'])
        logger.info(f"   Found {len(page_data['features'])} features")
        
        # If we haven't reached max depth, follow links
        if depth < max_depth:
            valid_links = [
                link for link in page_data['links']
                if self._is_valid_link(link, start_url) and link not in visited
            ]
            
            logger.info(f"   Found {len(valid_links)} valid links to follow")
            
            # Crawl each valid link
            for link in valid_links:
                if len(visited) >= self.config.max_pages:
                    break
                
                child_features = await self._crawl_recursively(
                    link, 
                    max_depth, 
                    visited, 
                    depth + 1
                )
                all_features.update(child_features)
        
        return all_features
    
    async def _fetch_main_documentation(self) -> Dict[str, Any]:
        """
        Fetch documentation from main documentation URL.
        
        NOW WITH RECURSIVE CRAWLING!
        - If follow_links=True: Automatically discovers and crawls subpages
        - If follow_links=False: Only scrapes the main URL (old behavior)
        
        CUSTOMIZE HTML PARSING:
        If your documentation has a different HTML structure,
        adjust the BeautifulSoup selectors below.
        """
        try:
            url = self.config.main_docs_url
            
            # NEW: Recursive crawling if enabled
            if self.config.follow_links:
                logger.info(f"Starting recursive crawl from: {url}")
                logger.info(f"   Max depth: {self.config.max_depth}, Max pages: {self.config.max_pages}")
                
                features = await self._crawl_recursively(
                    start_url=url,
                    max_depth=self.config.max_depth
                )
                
                logger.info(f"Recursive crawl complete: {len(features)} total features discovered")
                return features
            
            # OLD: Single-page scraping (backward compatible)
            else:
                await self._create_session()
                logger.info(f"Fetching documentation from: {url} (single page mode)")
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Parse HTML content
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        features = {}
                        
                        # Extract features from headings and descriptions
                        # CUSTOMIZE: Adjust selectors for your HTML structure
                        headings = soup.find_all(self.config.heading_tags)
                        
                        for heading in headings:
                            if heading.text and len(heading.text.strip()) > 3:
                                feature_name = heading.text.strip()
                                
                                # Get description from next paragraph
                                # CUSTOMIZE: Adjust based on your HTML layout
                                description = ""
                                next_elem = heading.find_next_sibling(self.config.description_tag)
                                if next_elem:
                                    description = next_elem.get_text().strip()
                                
                                # Filter out navigation/meta content
                                if len(description) > 20 and not self._is_navigation_content(description):
                                    feature_key = self._create_feature_key(feature_name)
                                    features[feature_key] = {
                                        'name': feature_name,
                                        'description': description,
                                        'category': self._infer_category(feature_name),
                                        'source': 'dynamic',
                                        'last_updated': datetime.now().isoformat()
                                    }
                        
                        logger.info(f"Fetched {len(features)} features from main documentation")
                        return features
                        
                    else:
                        logger.warning(f"Failed to fetch documentation: HTTP {response.status}")
                        return {}
                    
        except Exception as e:
            logger.error(f"Error fetching documentation from {self.config.main_docs_url}: {str(e)}")
            return {}
    
    async def _fetch_additional_sources(self) -> Dict[str, Any]:
        """
        Fetch content from additional documentation sources.
        
        CUSTOMIZE:
        Add logic specific to your additional documentation pages.
        The default implementation works for simple HTML pages.
        """
        all_features = {}
        
        for url in self.config.additional_docs_urls:
            try:
                await self._create_session()
                logger.info(f"Fetching from additional source: {url}")
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Extract features - customize parsing as needed
                        sections = soup.find_all(['h2', 'h3'])
                        for section in sections:
                            if section.text and len(section.text.strip()) > 3:
                                feature_name = section.text.strip()
                                
                                # Get description if available
                                description = ""
                                next_elem = section.find_next_sibling('p')
                                if next_elem:
                                    description = next_elem.get_text().strip()
                                
                                if not description:
                                    description = f"Feature documented at {url}"
                                
                                feature_key = self._create_feature_key(feature_name)
                                all_features[feature_key] = {
                                    'name': feature_name,
                                    'description': description,
                                    'category': 'additional',
                                    'source': 'dynamic',
                                    'last_updated': datetime.now().isoformat(),
                                    'source_url': url
                                }
                        
                        logger.info(f"Fetched {len(sections)} items from {url}")
                        
            except Exception as e:
                logger.error(f"Error fetching {url}: {str(e)}")
                continue
        
        return all_features
    
    def _is_navigation_content(self, text: str) -> bool:
        """
        Filter out navigation/meta content that shouldn't be treated as features.
        
        CUSTOMIZE: Add keywords specific to your documentation site.
        """
        navigation_keywords = [
            'on this page',
            'table of contents',
            'navigation',
            'breadcrumb',
            'previous',
            'next',
            'see also',
            'related pages',
            'jump to'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in navigation_keywords)
    
    def _create_feature_key(self, name: str) -> str:
        """Create a consistent key from feature name"""
        return name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_').replace('/', '_')
    
    def _infer_category(self, feature_name: str) -> str:
        """
        Infer feature category from name using keyword matching.
        
        CUSTOMIZE:
        Add your own category inference logic based on your product's structure.
        
        CATEGORIES:
        - core_features: Main product capabilities
        - integrations: Third-party integrations, APIs, webhooks
        - analytics: Reporting, dashboards, data analysis
        - monitoring: Real-time monitoring, alerts, tracking
        - data_sources: Data feeds, imports, exports
        """
        name_lower = feature_name.lower()
        
        if any(word in name_lower for word in ['api', 'integration', 'webhook', 'connector', 'plugin']):
            return 'integrations'
        elif any(word in name_lower for word in ['analytics', 'report', 'dashboard', 'chart', 'visualization']):
            return 'analytics'
        elif any(word in name_lower for word in ['monitor', 'alert', 'notification', 'tracking', 'watch']):
            return 'monitoring'
        elif any(word in name_lower for word in ['data', 'feed', 'source', 'catalog', 'import', 'export']):
            return 'data_sources'
        else:
            return 'core_features'
    
    def _should_refresh_cache(self) -> bool:
        """Check if cache needs refreshing"""
        if self.last_fetch is None:
            return True
        return datetime.now() - self.last_fetch > self.cache_duration
    
    async def refresh_dynamic_content(self) -> bool:
        """
        Refresh dynamic content from all documentation sources.
        
        This method is called automatically when cache expires.
        You can also call it manually with force_refresh=True.
        """
        try:
            logger.info(f"Refreshing dynamic content for {self.config.product_name}...")
            
            # Fetch from all sources
            main_docs = await self._fetch_main_documentation()
            additional_docs = await self._fetch_additional_sources()
            
            # Merge dynamic content
            self.dynamic_content = {
                **main_docs,
                **additional_docs
            }
            
            self.last_fetch = datetime.now()
            
            logger.info(f"Dynamic content refreshed: {len(self.dynamic_content)} items")
            logger.info(f"   Next refresh: {(self.last_fetch + self.cache_duration).strftime('%Y-%m-%d %H:%M')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh dynamic content: {str(e)}")
            return False
        finally:
            await self._close_session()
    
    def get_merged_content(self) -> Dict[str, Any]:
        """
        Get merged static + dynamic content with smart prioritization.
        
        Strategy:
        1. Start with static content (reliable baseline)
        2. Overlay with dynamic content (latest updates)
        3. Mark overlapping features as 'hybrid'
        """
        merged = {}
        
        # Start with static content (reliable base)
        for key, feature in self.static_content.items():
            merged[key] = asdict(feature)
        
        # Overlay with dynamic content (latest updates)
        for key, feature in self.dynamic_content.items():
            if key in merged:
                # Update existing feature with dynamic data
                merged[key]['description'] = feature.get('description', merged[key]['description'])
                merged[key]['source'] = 'hybrid'
                merged[key]['last_updated'] = feature.get('last_updated', merged[key]['last_updated'])
                merged[key]['dynamic_details'] = feature
            else:
                # Add new dynamic feature
                merged[key] = feature
        
        return merged
    
    async def get_product_context(self, force_refresh: bool = False) -> str:
        """
        Get formatted product context for AI prompts.
        
        This is the MAIN METHOD to use - returns a formatted string
        ready to inject into LLM prompts.
        
        Args:
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            Formatted markdown string with product features and capabilities
            
        USAGE:
            context = await service.get_product_context()
            # Inject 'context' into your LLM system prompt or user message
        """
        
        # Refresh if needed
        if force_refresh or self._should_refresh_cache():
            await self.refresh_dynamic_content()
        
        # Get merged content
        content = self.get_merged_content()
        
        # Format for prompt
        context_lines = [
            f"{self.config.product_name} - Product Knowledge",
            f"Industry: {self.config.product_industry}",
            "",
            "=" * 70,
            ""
        ]
        
        # Group by category
        categories = {}
        for key, feature in content.items():
            category = feature.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(feature)
        
        # Format each category
        category_display_names = {
            'core_features': 'Core Features',
            'integrations': 'Integrations & APIs',
            'analytics': 'Analytics & Reporting',
            'monitoring': 'Monitoring & Alerts',
            'data_sources': 'Data Sources & Feeds',
            'additional': 'Additional Features'
        }
        
        for category, features in sorted(categories.items()):
            display_name = category_display_names.get(category, category.replace('_', ' ').title())
            context_lines.append(f"\n## {display_name}\n")
            
            for feature in features:
                source_label = {
                    'static': '[Static]',
                    'dynamic': '[Dynamic]',
                    'hybrid': '[Hybrid]'
                }.get(feature.get('source'), '')
                
                context_lines.append(f"{source_label} **{feature['name']}**")
                context_lines.append(f"   {feature['description']}")
                
                # Add details if available
                if feature.get('details'):
                    details = feature['details']
                    if isinstance(details, dict):
                        for key, value in list(details.items())[:2]:  # Show first 2 details
                            context_lines.append(f"   • {key}: {value}")
                
                context_lines.append("")
        
        # Add metadata
        context_lines.append("\n" + "=" * 70)
        last_update = self.last_fetch.strftime("%Y-%m-%d %H:%M") if self.last_fetch else "Never"
        context_lines.append(f"\nContent last updated: {last_update}")
        context_lines.append(f"Total features: {len(content)}")
        context_lines.append(f"   • Static (reliable baseline): {len([f for f in content.values() if f.get('source') == 'static'])}")
        context_lines.append(f"   • Dynamic (live scraped): {len([f for f in content.values() if f.get('source') == 'dynamic'])}")
        context_lines.append(f"   • Hybrid (enhanced): {len([f for f in content.values() if f.get('source') == 'hybrid'])}")
        
        return "\n".join(context_lines)
    
    def get_content_stats(self) -> Dict[str, Any]:
        """
        Get statistics about content sources.
        
        Useful for monitoring and debugging.
        """
        merged = self.get_merged_content()
        
        stats = {
            'product_name': self.config.product_name,
            'total_features': len(merged),
            'static_features': len([f for f in merged.values() if f.get('source') == 'static']),
            'dynamic_features': len([f for f in merged.values() if f.get('source') == 'dynamic']),
            'hybrid_features': len([f for f in merged.values() if f.get('source') == 'hybrid']),
            'last_refresh': self.last_fetch.isoformat() if self.last_fetch else None,
            'cache_valid': not self._should_refresh_cache(),
            'cache_expires_in_hours': (
                (self.cache_duration - (datetime.now() - self.last_fetch)).total_seconds() / 3600
                if self.last_fetch else None
            ),
            'docs_url': self.config.main_docs_url,
            'additional_sources': len(self.config.additional_docs_urls)
        }
        
        return stats


# ============================================================================
# INITIALIZATION - Customize this section for your product
# ============================================================================

def create_default_service() -> ProductDocsService:
    """
    Create service instance with default configuration.
    
    FOR PRODUCTION: Replace this with your own configuration!
    
    This example uses LSports BOOST with recursive crawling enabled - 
    replace with your product details.
    
    EXAMPLE for your product:
        config = ProductDocsConfig(
            main_docs_url="https://docs.yourproduct.com",
            additional_docs_urls=["https://docs.yourproduct.com/api"],
            product_name="YourProduct",
            product_industry="Your Industry",
            cache_duration_hours=6,
            # Recursive crawling (NEW!)
            follow_links=True,
            max_depth=2,
            link_pattern=r'/yourproduct/.*',  # Optional: filter links
            max_pages=50
        )
        return ProductDocsService(config)
    """
    config = ProductDocsConfig(
        main_docs_url=MAIN_DOCS_URL,
        additional_docs_urls=[],  # No longer needed with recursive crawling!
        cache_duration_hours=6,
        product_name=PRODUCT_NAME,
        product_industry=PRODUCT_INDUSTRY,
        # Recursive crawling configuration
        follow_links=True,
        max_depth=2,
        link_pattern=None,  # Will follow links within same domain
        max_pages=50
    )
    return ProductDocsService(config)


# Global service instance
_service_instance: Optional[ProductDocsService] = None


def get_service() -> ProductDocsService:
    """
    Get or create the global service instance.
    
    This creates a singleton instance that persists across requests.
    The instance caches documentation and refreshes periodically.
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = create_default_service()
    return _service_instance


def set_service(service: ProductDocsService):
    """
    Set a custom service instance.
    
    Use this to replace the default service with your own configuration.
    
    EXAMPLE:
        from services.product_docs_service import ProductDocsConfig, ProductDocsService, set_service
        
        my_config = ProductDocsConfig(
            main_docs_url="https://docs.myproduct.com",
            product_name="MyProduct"
        )
        my_service = ProductDocsService(my_config)
        set_service(my_service)
    """
    global _service_instance
    _service_instance = service


# ============================================================================
# HELPER FUNCTIONS - Public API
# ============================================================================

async def get_product_context(force_refresh: bool = False) -> str:
    """
    Helper function to get product context.
    
    USAGE IN YOUR CODE:
        from services.product_docs_service import get_product_context
        
        # In your route or service:
        product_knowledge = await get_product_context()
        
        # Inject into LLM prompt:
        system_prompt = f'''
        You are an AI assistant with knowledge about our product.
        
        {product_knowledge}
        
        Answer user questions based on the above product information.
        '''
    
    Args:
        force_refresh: Force refresh even if cache is valid
        
    Returns:
        Formatted product context string
    """
    service = get_service()
    return await service.get_product_context(force_refresh)


def get_content_stats() -> Dict[str, Any]:
    """
    Helper function to get content statistics.
    
    USAGE:
        from services.product_docs_service import get_content_stats
        
        stats = get_content_stats()
        print(f"Total features: {stats['total_features']}")
        print(f"Last refresh: {stats['last_refresh']}")
    """
    service = get_service()
    return service.get_content_stats()


# ============================================================================
# EXAMPLE USAGE & TESTING
# ============================================================================

if __name__ == "__main__":
    """
    Example usage and testing.
    
    Run this file directly to test the service:
        python services/product_docs_service.py
    """
    
    async def test_default_service():
        """Test with default LSports configuration"""
        print("\n" + "=" * 70)
        print("Testing ProductDocsService with DEFAULT configuration (LSports BOOST)")
        print("=" * 70 + "\n")
        
        service = get_service()
        
        # Get context
        context = await service.get_product_context(force_refresh=True)
        print(context)
        
        # Get stats
        print("\n" + "=" * 70)
        print("STATISTICS")
        print("=" * 70)
        stats = service.get_content_stats()
        print(json.dumps(stats, indent=2))
    
    async def test_custom_service():
        """Test with custom configuration (example)"""
        print("\n\n" + "=" * 70)
        print("Example: Custom Product Configuration")
        print("=" * 70 + "\n")
        
        # Create custom config
        custom_config = ProductDocsConfig(
            main_docs_url="https://docs.yourproduct.com",  # Replace with your URL
            product_name="YourProduct",
            product_industry="YourIndustry",
            cache_duration_hours=12
        )
        
        print(f"Configuration:")
        print(f"  Product: {custom_config.product_name}")
        print(f"  Industry: {custom_config.product_industry}")
        print(f"  Docs URL: {custom_config.main_docs_url}")
        print(f"  Cache: {custom_config.cache_duration_hours} hours")
        print("\n(This is just configuration - URL doesn't exist)")
    
    # Run tests
    asyncio.run(test_default_service())
    asyncio.run(test_custom_service())

