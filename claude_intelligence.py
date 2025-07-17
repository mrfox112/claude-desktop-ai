import requests
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
import urllib.parse
from bs4 import BeautifulSoup
import logging
import os
from dataclasses import dataclass
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Structure for search results"""
    title: str
    url: str
    snippet: str
    source: str
    timestamp: datetime

@dataclass
class WeatherData:
    """Structure for weather information"""
    location: str
    temperature: float
    condition: str
    humidity: int
    wind_speed: float
    timestamp: datetime

@dataclass
class NewsItem:
    """Structure for news items"""
    title: str
    summary: str
    url: str
    source: str
    published: datetime
    category: str

class InternetConnector:
    """Handles internet connectivity and web searches"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def search_duckduckgo(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search using DuckDuckGo API"""
        try:
            # Use DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            
            # Get instant answer if available
            if data.get('AbstractText'):
                results.append(SearchResult(
                    title=data.get('Heading', 'Instant Answer'),
                    url=data.get('AbstractURL', ''),
                    snippet=data.get('AbstractText', ''),
                    source='DuckDuckGo',
                    timestamp=datetime.now()
                ))
            
            # Get related topics
            for topic in data.get('RelatedTopics', [])[:max_results]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append(SearchResult(
                        title=topic.get('Text', '').split(' - ')[0],
                        url=topic.get('FirstURL', ''),
                        snippet=topic.get('Text', ''),
                        source='DuckDuckGo',
                        timestamp=datetime.now()
                    ))
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def get_weather(self, location: str) -> Optional[WeatherData]:
        """Get weather information for a location"""
        try:
            # Using OpenWeatherMap API (you'd need to get a free API key)
            # For demo purposes, using a mock weather service
            
            # Mock weather data - in real implementation, use actual weather API
            mock_weather = {
                'temperature': 22.5,
                'condition': 'Partly cloudy',
                'humidity': 65,
                'wind_speed': 12.5
            }
            
            return WeatherData(
                location=location,
                temperature=mock_weather['temperature'],
                condition=mock_weather['condition'],
                humidity=mock_weather['humidity'],
                wind_speed=mock_weather['wind_speed'],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return None
    
    def get_news(self, topic: str = "technology", max_results: int = 5) -> List[NewsItem]:
        """Get latest news on a topic"""
        try:
            # Using NewsAPI (you'd need to get a free API key)
            # For demo purposes, using mock news data
            
            mock_news = [
                {
                    'title': f'Latest developments in {topic}',
                    'summary': f'Recent advancements in {topic} showing promising results...',
                    'url': f'https://example.com/news/{topic}',
                    'source': 'Tech News',
                    'published': datetime.now() - timedelta(hours=2),
                    'category': topic
                },
                {
                    'title': f'{topic.title()} trends for 2024',
                    'summary': f'Industry experts predict major changes in {topic} sector...',
                    'url': f'https://example.com/trends/{topic}',
                    'source': 'Industry Report',
                    'published': datetime.now() - timedelta(hours=6),
                    'category': topic
                }
            ]
            
            return [NewsItem(**item) for item in mock_news[:max_results]]
            
        except Exception as e:
            logger.error(f"News API error: {e}")
            return []
    
    def get_webpage_content(self, url: str) -> Optional[str]:
        """Extract text content from a webpage"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:5000]  # Limit to 5000 characters
            
        except Exception as e:
            logger.error(f"Web scraping error: {e}")
            return None

class KnowledgeEnhancer:
    """Enhances Claude's knowledge with real-time information"""
    
    def __init__(self):
        self.internet = InternetConnector()
        self.knowledge_cache = {}
        self.cache_expiry = timedelta(hours=1)
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine what additional information might be needed"""
        analysis = {
            'needs_current_info': False,
            'needs_weather': False,
            'needs_news': False,
            'needs_search': False,
            'search_terms': [],
            'location': None,
            'news_topic': None
        }
        
        # Check for current information needs
        current_indicators = ['today', 'now', 'current', 'latest', 'recent', 'what\'s happening']
        if any(indicator in query.lower() for indicator in current_indicators):
            analysis['needs_current_info'] = True
        
        # Check for weather requests
        weather_keywords = ['weather', 'temperature', 'forecast', 'climate', 'rain', 'sunny']
        if any(keyword in query.lower() for keyword in weather_keywords):
            analysis['needs_weather'] = True
            # Try to extract location
            location_match = re.search(r'in\s+([A-Za-z\s]+)', query, re.IGNORECASE)
            if location_match:
                analysis['location'] = location_match.group(1).strip()
        
        # Check for news requests
        news_keywords = ['news', 'headlines', 'breaking', 'reports', 'updates']
        if any(keyword in query.lower() for keyword in news_keywords):
            analysis['needs_news'] = True
            # Try to extract topic
            topic_match = re.search(r'about\s+([A-Za-z\s]+)', query, re.IGNORECASE)
            if topic_match:
                analysis['news_topic'] = topic_match.group(1).strip()
        
        # Check if general search would be helpful
        question_words = ['what', 'who', 'when', 'where', 'why', 'how']
        if any(word in query.lower() for word in question_words):
            analysis['needs_search'] = True
            # Extract key terms for search
            words = query.lower().split()
            search_terms = [word for word in words if len(word) > 3 and word not in ['what', 'who', 'when', 'where', 'why', 'how', 'the', 'and', 'or', 'but']]
            analysis['search_terms'] = search_terms[:3]  # Limit to 3 terms
        
        return analysis
    
    def gather_enhanced_context(self, query: str) -> Dict[str, Any]:
        """Gather additional context to enhance Claude's response"""
        analysis = self.analyze_query(query)
        context = {
            'timestamp': datetime.now().isoformat(),
            'search_results': [],
            'weather_data': None,
            'news_items': [],
            'additional_info': {}
        }
        
        # Gather search results
        if analysis['needs_search'] and analysis['search_terms']:
            search_query = ' '.join(analysis['search_terms'])
            context['search_results'] = self.internet.search_duckduckgo(search_query)
        
        # Gather weather information
        if analysis['needs_weather']:
            location = analysis['location'] or 'New York'  # Default location
            context['weather_data'] = self.internet.get_weather(location)
        
        # Gather news information
        if analysis['needs_news']:
            topic = analysis['news_topic'] or 'technology'  # Default topic
            context['news_items'] = self.internet.get_news(topic)
        
        # Add current time context
        if analysis['needs_current_info']:
            context['additional_info']['current_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            context['additional_info']['day_of_week'] = datetime.now().strftime('%A')
        
        return context
    
    def format_context_for_claude(self, context: Dict[str, Any]) -> str:
        """Format gathered context into a string that Claude can use"""
        formatted_context = []
        
        # Add timestamp
        formatted_context.append(f"Current time: {context['timestamp']}")
        
        # Add search results
        if context['search_results']:
            formatted_context.append("\n📊 SEARCH RESULTS:")
            for i, result in enumerate(context['search_results'], 1):
                formatted_context.append(f"{i}. {result.title}")
                formatted_context.append(f"   {result.snippet}")
                if result.url:
                    formatted_context.append(f"   Source: {result.url}")
                formatted_context.append("")
        
        # Add weather data
        if context['weather_data']:
            weather = context['weather_data']
            formatted_context.append(f"\n🌤️ WEATHER INFO for {weather.location}:")
            formatted_context.append(f"Temperature: {weather.temperature}°C")
            formatted_context.append(f"Condition: {weather.condition}")
            formatted_context.append(f"Humidity: {weather.humidity}%")
            formatted_context.append(f"Wind: {weather.wind_speed} km/h")
            formatted_context.append("")
        
        # Add news items
        if context['news_items']:
            formatted_context.append("\n📰 RECENT NEWS:")
            for i, news in enumerate(context['news_items'], 1):
                formatted_context.append(f"{i}. {news.title}")
                formatted_context.append(f"   {news.summary}")
                formatted_context.append(f"   Source: {news.source}")
                formatted_context.append("")
        
        # Add additional info
        if context['additional_info']:
            formatted_context.append("\n🕐 CURRENT INFO:")
            for key, value in context['additional_info'].items():
                formatted_context.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return '\n'.join(formatted_context)

class SmartClaudeProcessor:
    """Main processor that enhances Claude's capabilities"""
    
    def __init__(self):
        self.knowledge_enhancer = KnowledgeEnhancer()
        self.conversation_memory = []
        self.user_preferences = {}
    
    def process_user_query(self, query: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Process user query and enhance it with additional context"""
        
        # Gather enhanced context
        enhanced_context = self.knowledge_enhancer.gather_enhanced_context(query)
        
        # Format context for Claude
        formatted_context = self.knowledge_enhancer.format_context_for_claude(enhanced_context)
        
        # Create enhanced prompt
        enhanced_prompt = self._create_enhanced_prompt(query, formatted_context, conversation_history)
        
        # Store in conversation memory
        self.conversation_memory.append({
            'original_query': query,
            'enhanced_context': enhanced_context,
            'timestamp': datetime.now()
        })
        
        return {
            'enhanced_prompt': enhanced_prompt,
            'context': enhanced_context,
            'original_query': query,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_enhanced_prompt(self, query: str, context: str, conversation_history: List[Dict] = None) -> str:
        """Create an enhanced prompt with additional context"""
        
        prompt_parts = []
        
        # Add system enhancement
        prompt_parts.append("You are Claude, an AI assistant with access to real-time information and enhanced capabilities.")
        prompt_parts.append("Use the following current information to provide accurate, up-to-date responses:")
        prompt_parts.append("")
        
        # Add context
        if context.strip():
            prompt_parts.append("=== REAL-TIME CONTEXT ===")
            prompt_parts.append(context)
            prompt_parts.append("=== END CONTEXT ===")
            prompt_parts.append("")
        
        # Add conversation history context
        if conversation_history:
            prompt_parts.append("Recent conversation context:")
            for msg in conversation_history[-3:]:  # Last 3 messages
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:200]  # Truncate if too long
                prompt_parts.append(f"{role}: {content}")
            prompt_parts.append("")
        
        # Add enhanced instructions
        prompt_parts.append("Instructions:")
        prompt_parts.append("- Use the provided real-time information when relevant")
        prompt_parts.append("- Cite sources when using external information")
        prompt_parts.append("- Be more specific and accurate with current events")
        prompt_parts.append("- Provide actionable insights when possible")
        prompt_parts.append("")
        
        # Add the actual user query
        prompt_parts.append(f"User query: {query}")
        
        return '\n'.join(prompt_parts)
    
    def enhance_message(self, message: str) -> str:
        """Enhance a user message with real-time context and information"""
        try:
            # Process the query to get enhanced context
            result = self.process_user_query(message)
            
            # Return the enhanced prompt
            return result['enhanced_prompt']
            
        except Exception as e:
            logger.error(f"Error enhancing message: {e}")
            # Return original message if enhancement fails
            return message
    
    def get_intelligence_stats(self) -> Dict[str, Any]:
        """Get statistics about the intelligence enhancements"""
        return {
            'total_queries_processed': len(self.conversation_memory),
            'recent_queries': [
                {
                    'query': mem['original_query'][:50] + '...' if len(mem['original_query']) > 50 else mem['original_query'],
                    'timestamp': mem['timestamp'].isoformat(),
                    'had_context': bool(mem['enhanced_context']['search_results'] or 
                                      mem['enhanced_context']['weather_data'] or 
                                      mem['enhanced_context']['news_items'])
                }
                for mem in self.conversation_memory[-5:]
            ],
            'capabilities': [
                'Real-time web search',
                'Weather information',
                'Latest news updates',
                'Current time awareness',
                'Context-aware responses'
            ]
        }

# Example usage and testing
def test_intelligence_system():
    """Test the intelligence enhancement system"""
    processor = SmartClaudeProcessor()
    
    # Test queries
    test_queries = [
        "What's the weather like today?",
        "What's the latest news about AI?",
        "How does photosynthesis work?",
        "What's happening in the tech world right now?"
    ]
    
    print("🧠 Testing Claude Intelligence Enhancement System")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        result = processor.process_user_query(query)
        print(f"✅ Enhanced with context: {bool(result['context']['search_results'] or result['context']['weather_data'] or result['context']['news_items'])}")
        
        # Show context summary
        context = result['context']
        if context['search_results']:
            print(f"🔍 Found {len(context['search_results'])} search results")
        if context['weather_data']:
            print(f"🌤️ Weather data for {context['weather_data'].location}")
        if context['news_items']:
            print(f"📰 Found {len(context['news_items'])} news items")
    
    # Show stats
    stats = processor.get_intelligence_stats()
    print(f"\n📊 Intelligence Stats:")
    print(f"Total queries processed: {stats['total_queries_processed']}")
    print(f"Capabilities: {', '.join(stats['capabilities'])}")

if __name__ == "__main__":
    test_intelligence_system()
