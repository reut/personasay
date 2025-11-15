"""
LSports Content Service - Hybrid Dynamic/Static Content Management
Combines static LSports knowledge with dynamic content fetching and caching.
"""

import asyncio
import aiohttp
import ssl
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import re
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LSportsFeature:
    """Represents a single LSports feature/capability"""
    name: str
    description: str
    category: str  # 'boost', 'data', 'api', 'monitoring'
    source: str    # 'static' or 'dynamic'
    last_updated: str
    details: Dict[str, Any] = None

class LSportsContentService:
    """
    Hybrid service that manages both static and dynamic LSports content.
    
    Features:
    - Static core knowledge for reliability
    - Dynamic updates from LSports documentation
    - Intelligent caching with configurable refresh intervals
    - Fallback to static content if dynamic fetch fails
    """
    
    def __init__(self, cache_duration_hours: int = 6):
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.last_fetch = None
        self.dynamic_content = {}
        self.static_content = self._load_static_content()
        self.session = None
        
    def _load_static_content(self) -> Dict[str, LSportsFeature]:
        """Load reliable static LSports knowledge as fallback"""
        
        static_features = {
            "boost_platform": LSportsFeature(
                name="BOOST Platform",
                description="Main monitoring screen for tracking fixtures, providers, and markets with real-time status updates",
                category="boost",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "url": "https://monitoring.lsports.eu",
                    "key_features": ["fixture_monitoring", "provider_filtering", "sports_bar", "real_time_updates"]
                }
            ),
            "coverage_hub": LSportsFeature(
                name="Coverage Hub",
                description="Provider rankings and coverage analysis for optimal provider selection across sports, leagues, and markets",
                category="boost",
                source="static", 
                last_updated=datetime.now().isoformat(),
                details={
                    "reports": ["markets", "livescore", "settlement"],
                    "features": ["provider_rankings", "fixture_coverage", "hierarchy_filtering"]
                }
            ),
            "settlement_coverage": LSportsFeature(
                name="Settlement Coverage", 
                description="Historical settlement reliability data with Yes/No indicators based on 12 months and 30 recent fixtures",
                category="boost",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "data_period": "12_months",
                    "fixture_sample": "30_recent",
                    "indicators": ["yes_no_settlement", "last_supported", "market_level"]
                }
            ),
            "livescore_coverage": LSportsFeature(
                name="Livescore Coverage",
                description="Incident-level data analysis for recent matches showing livescore support quality per league",
                category="boost", 
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "metrics_basis": "30_fixtures_12_months",
                    "scope": "incident_level",
                    "evaluation": "league_support_level"
                }
            ),
            "provider_view": LSportsFeature(
                name="Provider View",
                description="Real-time comparison of multiple providers' performance, reliability, and coverage",
                category="monitoring",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "comparison_types": ["performance", "reliability", "coverage"],
                    "real_time": True
                }
            ),
            "market_view": LSportsFeature(
                name="Market View", 
                description="Market-level monitoring and filtering capabilities for detailed market analysis",
                category="monitoring",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "granularity": "market_level",
                    "capabilities": ["monitoring", "filtering", "analysis"]
                }
            ),
            "premium_markets": LSportsFeature(
                name="Premium Markets",
                description="Advanced player props and betting markets data for enhanced betting experiences",
                category="data",
                source="static", 
                last_updated=datetime.now().isoformat(),
                details={
                    "market_types": ["player_props", "advanced_betting"],
                    "purpose": "enhanced_experience"
                }
            ),
            "data_feeds": LSportsFeature(
                name="LSports Data Feeds",
                description="Real-time PreMatch and InPlay data including incidents, fixtures, leagues, and odds",
                category="data",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "feed_types": ["real_time", "prematch", "inplay"],
                    "data_types": ["incidents", "fixtures", "leagues", "odds"]
                }
            ),
            "lsports_incidents": LSportsFeature(
                name="LSports Incidents",
                description="Incident data feeds for live events and match updates",
                category="data_catalog",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "type": "incident_data",
                    "source_url": "https://files.lsports.eu/"
                }
            ),
            "lsports_providers": LSportsFeature(
                name="LSports Providers",
                description="Data provider information and capabilities catalog",
                category="data_catalog", 
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "type": "provider_data",
                    "source_url": "https://files.lsports.eu/"
                }
            ),
            "lsports_leagues_and_sports": LSportsFeature(
                name="LSports Leagues and Sports",
                description="Comprehensive sports and leagues data catalog",
                category="data_catalog",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "type": "sports_leagues_data",
                    "source_url": "https://files.lsports.eu/"
                }
            ),
            "lsports_e_games": LSportsFeature(
                name="LSports E-Games",
                description="ESports and electronic gaming data offerings",
                category="data_catalog",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "type": "esports_data",
                    "source_url": "https://files.lsports.eu/"
                }
            ),
            "fixtures_prematch": LSportsFeature(
                name="Fixtures PreMatch",
                description="PreMatch fixture data with upcoming events and markets",
                category="data_catalog",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "type": "prematch_fixtures",
                    "source_url": "https://files.lsports.eu/"
                }
            ),
            "fixtures_inplay": LSportsFeature(
                name="Fixtures Inplay", 
                description="Live InPlay fixture data with real-time updates",
                category="data_catalog",
                source="static",
                last_updated=datetime.now().isoformat(),
                details={
                    "type": "inplay_fixtures",
                    "source_url": "https://files.lsports.eu/"
                }
            )
        }
        
        logger.info(f"📚 Loaded {len(static_features)} static LSports features")
        return static_features
    
    async def _create_session(self):
        """Create aiohttp session if not exists"""
        if self.session is None:
            # Create SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=10),
                headers={
                    'User-Agent': 'PersonaSay-LSports-Integration/1.0'
                }
            )
    
    async def _close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _fetch_boost_documentation(self) -> Dict[str, Any]:
        """Fetch latest BOOST documentation dynamically"""
        try:
            await self._create_session()
            
            url = "https://docs.lsports.eu/lsports/boost"
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse HTML content
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Extract features and updates
                    features = {}
                    
                    # Look for feature headings and descriptions
                    headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
                    for heading in headings:
                        if heading.text and len(heading.text.strip()) > 3:
                            feature_name = heading.text.strip()
                            
                            # Get description from following paragraph
                            description = ""
                            next_elem = heading.find_next_sibling()
                            if next_elem and next_elem.name == 'p':
                                description = next_elem.get_text().strip()
                            
                            # Skip very short or generic descriptions
                            if len(description) > 20 and not description.lower().startswith('on this page'):
                                features[feature_name.lower().replace(' ', '_')] = {
                                    'name': feature_name,
                                    'description': description,
                                    'source': 'dynamic',
                                    'last_updated': datetime.now().isoformat()
                                }
                    
                    logger.info(f"🔄 Fetched {len(features)} dynamic features from BOOST docs")
                    return features
                    
                else:
                    logger.warning(f"⚠️ Failed to fetch BOOST docs: HTTP {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Error fetching BOOST documentation: {str(e)}")
            return {}
    
    async def _fetch_lsports_offerings(self) -> Dict[str, Any]:
        """Fetch latest LSports offerings information from files.lsports.eu"""
        try:
            await self._create_session()
            
            url = "https://files.lsports.eu/"
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse HTML content for data offerings
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    offerings = {}
                    
                    # Look for data offerings sections
                    data_sections = soup.find_all(['h3', 'h2'])
                    for section in data_sections:
                        if section.text and len(section.text.strip()) > 3:
                            offering_name = section.text.strip()
                            
                            # Get date from next sibling or parent
                            date_text = ""
                            next_elem = section.find_next_sibling()
                            if next_elem:
                                date_text = next_elem.get_text().strip()
                            
                            # Create offering entry
                            key = offering_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
                            offerings[key] = {
                                'name': offering_name,
                                'description': f"LSports data offering: {offering_name}",
                                'category': 'data_catalog',
                                'source': 'dynamic',
                                'last_updated': datetime.now().isoformat(),
                                'availability_date': date_text,
                                'details': {
                                    'type': 'data_feed',
                                    'source_url': 'https://files.lsports.eu/'
                                }
                            }
                    
                    logger.info(f"🔄 Fetched {len(offerings)} data offerings from LSports catalog")
                    return offerings
                    
                else:
                    logger.warning(f"⚠️ Failed to fetch LSports offerings: HTTP {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Error fetching LSports offerings: {str(e)}")
            return {}
    
    def _should_refresh_cache(self) -> bool:
        """Check if cache needs refreshing"""
        if self.last_fetch is None:
            return True
        return datetime.now() - self.last_fetch > self.cache_duration
    
    async def refresh_dynamic_content(self) -> bool:
        """Refresh dynamic content from LSports sources"""
        try:
            logger.info("🔄 Refreshing dynamic LSports content...")
            
            # Fetch from multiple sources
            boost_content = await self._fetch_boost_documentation()
            offerings_content = await self._fetch_lsports_offerings()
            
            # Merge dynamic content
            self.dynamic_content = {
                **boost_content,
                **offerings_content
            }
            
            self.last_fetch = datetime.now()
            
            logger.info(f"✅ Dynamic content refreshed: {len(self.dynamic_content)} items")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to refresh dynamic content: {str(e)}")
            return False
        finally:
            await self._close_session()
    
    def get_merged_content(self) -> Dict[str, Any]:
        """Get merged static + dynamic content with smart prioritization"""
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
    
    async def get_lsports_context(self, force_refresh: bool = False) -> str:
        """Get formatted LSports context for prompts"""
        
        # Refresh if needed
        if force_refresh or self._should_refresh_cache():
            await self.refresh_dynamic_content()
        
        # Get merged content
        content = self.get_merged_content()
        
        # Format for prompt
        context_lines = [
            "LSports Platform Knowledge (Updated):",
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
        for category, features in categories.items():
            context_lines.append(f"## {category.upper()} Features:")
            for feature in features:
                source_indicator = "🔄" if feature.get('source') == 'dynamic' else "📋" if feature.get('source') == 'static' else "🔀"
                context_lines.append(f"- {source_indicator} **{feature['name']}**: {feature['description']}")
            context_lines.append("")
        
        # Add update info
        last_update = self.last_fetch.strftime("%Y-%m-%d %H:%M") if self.last_fetch else "Never"
        context_lines.append(f"_Content last updated: {last_update}_")
        
        return "\n".join(context_lines)
    
    def get_content_stats(self) -> Dict[str, Any]:
        """Get statistics about content sources"""
        merged = self.get_merged_content()
        
        stats = {
            'total_features': len(merged),
            'static_features': len([f for f in merged.values() if f.get('source') == 'static']),
            'dynamic_features': len([f for f in merged.values() if f.get('source') == 'dynamic']),
            'hybrid_features': len([f for f in merged.values() if f.get('source') == 'hybrid']),
            'last_refresh': self.last_fetch.isoformat() if self.last_fetch else None,
            'cache_valid': not self._should_refresh_cache()
        }
        
        return stats

# Global instance
lsports_service = LSportsContentService(cache_duration_hours=6)

async def get_lsports_context(force_refresh: bool = False) -> str:
    """Helper function to get LSports context"""
    return await lsports_service.get_lsports_context(force_refresh)

def get_content_stats() -> Dict[str, Any]:
    """Helper function to get content statistics"""
    return lsports_service.get_content_stats()