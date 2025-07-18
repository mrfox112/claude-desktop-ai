"""
Advanced Web Intelligence System for Ether AI
Provides real-time internet access, live data, and web-based intelligence
"""

import asyncio
import aiohttp
import requests
import json
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlencode, urlparse
import threading
from dataclasses import dataclass
from bs4 import BeautifulSoup
import feedparser
import yfinance as yf
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WebResult:
    """Structured web search result"""
    title: str
    url: str
    snippet: str
    timestamp: datetime
    source: str
    relevance_score: float = 0.0
    content_type: str = "text"

@dataclass
class NewsArticle:
    """News article structure"""
    title: str
    url: str
    summary: str
    published: datetime
    source: str
    category: str
    sentiment: str = "neutral"

@dataclass
class MarketData:
    """Financial market data"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    timestamp: datetime = None

class AdvancedWebIntelligence:
    """Advanced web intelligence system with real-time capabilities"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # API endpoints and keys
        self.search_engines = {
            'duckduckgo': 'https://api.duckduckgo.com/',
            'serp': 'https://serpapi.com/search',
            'bing': 'https://api.bing.microsoft.com/v7.0/search'
        }
        
        # News sources
        self.news_sources = {
            'rss_feeds': [
                'https://feeds.bbci.co.uk/news/rss.xml',
                'https://rss.cnn.com/rss/edition.rss',
                'https://feeds.reuters.com/Reuters/worldNews',
                'https://feeds.feedburner.com/TechCrunch',
                'https://feeds.arstechnica.com/arstechnica/index'
            ],
            'api_endpoints': [
                'https://newsapi.org/v2/top-headlines',
                'https://api.currentsapi.services/v1/latest-news'
            ]
        }
        
        # Cache for recent results
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
        # Real-time data sources
        self.realtime_sources = {
            'weather': 'https://api.openweathermap.org/data/2.5/weather',
            'stocks': 'https://query1.finance.yahoo.com/v8/finance/chart',
            'crypto': 'https://api.coingecko.com/api/v3/simple/price',
            'exchange_rates': 'https://api.exchangerate-api.com/v4/latest'
        }
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache:
            return False
        
        entry_time = self.cache[cache_key]['timestamp']
        return (datetime.now() - entry_time).seconds < self.cache_duration
    
    def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached result if valid"""
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        return None
    
    def _cache_result(self, cache_key: str, data: Any):
        """Cache result with timestamp"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def search_web(self, query: str, max_results: int = 10) -> List[WebResult]:
        """Perform intelligent web search with multiple sources"""
        cache_key = f"web_search_{query}_{max_results}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached
        
        results = []
        
        try:
            # Try multiple search methods
            results.extend(self._search_duckduckgo(query, max_results // 2))
            results.extend(self._search_bing(query, max_results // 2))
            
            # Sort by relevance and deduplicate
            results = self._deduplicate_results(results)
            results = sorted(results, key=lambda x: x.relevance_score, reverse=True)
            
            # Cache results
            self._cache_result(cache_key, results[:max_results])
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[WebResult]:
        """Search using DuckDuckGo"""
        try:
            # DuckDuckGo instant answer API
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(
                'https://api.duckduckgo.com/',
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Process related topics
                for topic in data.get('RelatedTopics', []):
                    if isinstance(topic, dict) and 'Text' in topic:
                        result = WebResult(
                            title=topic.get('Text', '')[:100],
                            url=topic.get('FirstURL', ''),
                            snippet=topic.get('Text', ''),
                            timestamp=datetime.now(),
                            source='DuckDuckGo',
                            relevance_score=0.7
                        )
                        results.append(result)
                
                return results[:max_results]
                
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def _search_bing(self, query: str, max_results: int) -> List[WebResult]:
        """Search using Bing (requires API key)"""
        # This would require a Bing API key - returning empty for now
        # In a real implementation, you'd use the Bing Search API
        return []
    
    def _deduplicate_results(self, results: List[WebResult]) -> List[WebResult]:
        """Remove duplicate results based on URL and title similarity"""
        seen_urls = set()
        deduplicated = []
        
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                deduplicated.append(result)
        
        return deduplicated
    
    def get_real_time_news(self, category: str = "general", max_articles: int = 10) -> List[NewsArticle]:
        """Get real-time news from multiple sources"""
        cache_key = f"news_{category}_{max_articles}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached
        
        articles = []
        
        try:
            # Fetch from RSS feeds
            for feed_url in self.news_sources['rss_feeds']:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:max_articles // len(self.news_sources['rss_feeds'])]:
                        article = NewsArticle(
                            title=entry.get('title', ''),
                            url=entry.get('link', ''),
                            summary=entry.get('summary', ''),
                            published=datetime.now(),  # Would parse actual date
                            source=feed.feed.get('title', 'Unknown'),
                            category=category
                        )
                        articles.append(article)
                except Exception as e:
                    logger.error(f"RSS feed error: {e}")
                    continue
            
            # Cache results
            self._cache_result(cache_key, articles[:max_articles])
            return articles[:max_articles]
            
        except Exception as e:
            logger.error(f"News fetch error: {e}")
            return []
    
    def get_weather_data(self, location: str) -> Dict[str, Any]:
        """Get current weather data"""
        cache_key = f"weather_{location}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached
        
        try:
            # Using OpenWeatherMap API (would need API key)
            # For now, returning mock data
            weather_data = {
                'location': location,
                'temperature': 22.5,
                'humidity': 65,
                'conditions': 'Partly cloudy',
                'wind_speed': 8.5,
                'timestamp': datetime.now().isoformat()
            }
            
            self._cache_result(cache_key, weather_data)
            return weather_data
            
        except Exception as e:
            logger.error(f"Weather data error: {e}")
            return {}
    
    def get_market_data(self, symbols: List[str]) -> List[MarketData]:
        """Get real-time market data"""
        cache_key = f"market_{'_'.join(symbols)}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached
        
        market_data = []
        
        try:
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    hist = ticker.history(period="1d")
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        prev_close = info.get('previousClose', current_price)
                        change = current_price - prev_close
                        change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
                        
                        data = MarketData(
                            symbol=symbol,
                            price=current_price,
                            change=change,
                            change_percent=change_percent,
                            volume=int(hist['Volume'].iloc[-1]),
                            market_cap=info.get('marketCap'),
                            timestamp=datetime.now()
                        )
                        market_data.append(data)
                        
                except Exception as e:
                    logger.error(f"Market data error for {symbol}: {e}")
                    continue
            
            self._cache_result(cache_key, market_data)
            return market_data
            
        except Exception as e:
            logger.error(f"Market data fetch error: {e}")
            return []
    
    def get_crypto_prices(self, crypto_ids: List[str]) -> Dict[str, float]:
        """Get cryptocurrency prices"""
        cache_key = f"crypto_{'_'.join(crypto_ids)}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached
        
        try:
            # CoinGecko API
            ids = ','.join(crypto_ids)
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                prices = {crypto_id: data.get(crypto_id, {}).get('usd', 0) for crypto_id in crypto_ids}
                
                self._cache_result(cache_key, prices)
                return prices
                
        except Exception as e:
            logger.error(f"Crypto prices error: {e}")
            return {}
    
    def scrape_webpage(self, url: str) -> Dict[str, Any]:
        """Intelligently scrape and extract content from a webpage"""
        cache_key = f"webpage_{url}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract key information
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title"
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract main content
            main_content = ""
            for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                main_content += tag.get_text().strip() + "\n"
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ""
            
            webpage_data = {
                'url': url,
                'title': title_text,
                'description': description,
                'content': main_content[:2000],  # Limit content length
                'timestamp': datetime.now().isoformat(),
                'word_count': len(main_content.split()),
                'domain': urlparse(url).netloc
            }
            
            self._cache_result(cache_key, webpage_data)
            return webpage_data
            
        except Exception as e:
            logger.error(f"Webpage scraping error: {e}")
            return {}
    
    def get_trending_topics(self) -> List[str]:
        """Get current trending topics from various sources"""
        cache_key = "trending_topics"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached
        
        trending = []
        
        try:
            # You could integrate with Twitter API, Google Trends, etc.
            # For now, return some sample trending topics
            trending = [
                "Artificial Intelligence",
                "Climate Change",
                "Cryptocurrency",
                "Space Exploration",
                "Renewable Energy",
                "Quantum Computing",
                "Virtual Reality",
                "Biotechnology"
            ]
            
            self._cache_result(cache_key, trending)
            return trending
            
        except Exception as e:
            logger.error(f"Trending topics error: {e}")
            return []
    
    def enhance_query_with_context(self, query: str, user_location: str = None) -> str:
        """Enhance user query with real-time context"""
        try:
            enhanced_query = query
            
            # Add current date/time context
            current_time = datetime.now()
            enhanced_query += f"\n\nCurrent date/time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Add location context if provided
            if user_location:
                enhanced_query += f"\nUser location: {user_location}"
            
            # Check if query needs real-time data
            if any(keyword in query.lower() for keyword in ['current', 'latest', 'recent', 'now', 'today']):
                # Get trending topics
                trending = self.get_trending_topics()
                if trending:
                    enhanced_query += f"\nCurrent trending topics: {', '.join(trending[:5])}"
            
            # Check if query needs market data
            if any(keyword in query.lower() for keyword in ['stock', 'market', 'price', 'trading']):
                # Get market snapshot
                market_data = self.get_market_data(['SPY', 'QQQ', 'DIA'])
                if market_data:
                    market_summary = "Current market: "
                    for data in market_data:
                        market_summary += f"{data.symbol}: ${data.price:.2f} ({data.change_percent:+.1f}%) "
                    enhanced_query += f"\n{market_summary}"
            
            return enhanced_query
            
        except Exception as e:
            logger.error(f"Query enhancement error: {e}")
            return query
    
    def get_comprehensive_context(self, query: str) -> Dict[str, Any]:
        """Get comprehensive real-time context for a query"""
        context = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'web_results': [],
            'news': [],
            'market_data': [],
            'weather': {},
            'trending': []
        }
        
        try:
            # Parallel execution for faster results
            futures = []
            
            # Web search
            futures.append(self.executor.submit(self.search_web, query, 5))
            
            # News
            futures.append(self.executor.submit(self.get_real_time_news, "general", 5))
            
            # Trending topics
            futures.append(self.executor.submit(self.get_trending_topics))
            
            # Market data (if relevant)
            if any(keyword in query.lower() for keyword in ['stock', 'market', 'finance', 'economy']):
                futures.append(self.executor.submit(self.get_market_data, ['SPY', 'QQQ', 'BTC-USD']))
            
            # Collect results
            for future in as_completed(futures, timeout=30):
                try:
                    result = future.result()
                    if isinstance(result, list):
                        if result and isinstance(result[0], WebResult):
                            context['web_results'] = result
                        elif result and isinstance(result[0], NewsArticle):
                            context['news'] = result
                        elif result and isinstance(result[0], MarketData):
                            context['market_data'] = result
                        elif result and isinstance(result[0], str):
                            context['trending'] = result
                except Exception as e:
                    logger.error(f"Context gathering error: {e}")
                    continue
            
            return context
            
        except Exception as e:
            logger.error(f"Comprehensive context error: {e}")
            return context
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.session.close()
            self.executor.shutdown(wait=True)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# Singleton instance
web_intelligence = AdvancedWebIntelligence()

def get_web_intelligence():
    """Get the web intelligence singleton"""
    return web_intelligence
