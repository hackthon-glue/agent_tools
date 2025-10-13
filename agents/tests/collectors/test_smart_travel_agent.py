"""
Test: Smart Travel Agent - Discovers destinations from user preferences
Agent infers optimal countries based on latent user needs, not pre-selected options
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'src'))

from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel
from collectors.news import BrowserNewsCollector
from collectors.weather import BrowserWeatherCollector
from collectors.flight import BrowserFlightCollector
from collectors.trends import BrowserTrendCollector

load_dotenv()


def collect_news_tool(country_code: str, max_results: int = 5):
    """Collect top news headlines for a country.
    
    Args:
        country_code: Two-letter country code (e.g., 'JP', 'FR', 'AU')
        max_results: Maximum number of news articles to return
    
    Returns:
        List of news articles with title, summary, sentiment
    """
    collector = BrowserNewsCollector(region=os.getenv('AWS_REGION', 'us-west-2'))
    return collector.get_top_headlines(country_code, max_results, validate=False)


def collect_weather_tool(country_code: str, city: str = None):
    """Get current weather information for a country or city.
    
    Args:
        country_code: Two-letter country code (e.g., 'JP', 'FR', 'AU')
        city: Optional city name for specific location
    
    Returns:
        Weather data including temperature, conditions, mood impact
    """
    collector = BrowserWeatherCollector(region=os.getenv('AWS_REGION', 'us-west-2'))
    return collector.get_weather(country_code, city)


def collect_flights_tool(origin: str, destination: str, start_date: str, num_results: int = 5):
    """Search for flights between two airports.
    
    Args:
        origin: Origin airport code (e.g., 'LAX', 'JFK')
        destination: Destination airport code (e.g., 'NRT', 'CDG')
        start_date: Departure date in YYYY-MM-DD format
        num_results: Maximum number of flight options to return
    
    Returns:
        List of flight options with price, duration, airline
    """
    collector = BrowserFlightCollector(region=os.getenv('AWS_REGION', 'us-west-2'))
    return collector.search_flights(origin, destination, start_date, num_results=num_results)


def collect_trends_tool(country_code: str, num_results: int = 5):
    """Get trending topics and discussions for a country.
    
    Args:
        country_code: Two-letter country code (e.g., 'JP', 'FR', 'AU')
        num_results: Maximum number of trending topics to return
    
    Returns:
        List of trending topics with engagement metrics
    """
    collector = BrowserTrendCollector(region=os.getenv('AWS_REGION', 'us-west-2'))
    return collector.get_trending_topics(country_code, hours=168, num_results=num_results)


def test_discover_from_preferences():
    """Test discovering destination from user preferences"""
    print("\n" + "="*60)
    print("TEST 1: Discover Destination from Preferences")
    print("="*60)
    
    agent = Agent(
        tools=[collect_news_tool, collect_weather_tool, collect_flights_tool, collect_trends_tool],
        model=BedrockModel(
            model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
            temperature=0.7,
            max_tokens=4000,
        ),
        system_prompt="""You are an intelligent travel discovery agent. Your job is to:

1. ANALYZE user preferences to identify 3-5 candidate countries
2. USE TOOLS to collect data for each candidate:
   - News sentiment
   - Weather conditions
   - Trending topics
   - Flight options
3. SCORE each destination (0-100) based on user needs
4. RECOMMEND top 2 destinations with detailed reasoning

Available countries: JP (Japan), FR (France), AU (Australia), UK (Britain), 
DE (Germany), KR (South Korea), IN (India), BR (Brazil), US (United States)

Major airports: NRT (Tokyo), CDG (Paris), SYD (Sydney), LHR (London), 
FRA (Frankfurt), ICN (Seoul), DEL (Delhi), GRU (Sao Paulo), JFK (New York)"""
    )
    
    query = """
I love traditional architecture and historical sites.
I want to experience authentic local cuisine.
I prefer mild weather (not too hot, not too cold).
My budget is around $4000 including flights.
I'm departing from LAX in late February 2025.

What destination would you recommend?
"""
    
    print(f"\n📝 User Query:\n{query}")
    print("\n🤖 Agent discovering destinations...")
    
    response = agent(query)
    
    print(f"\n✅ Agent Discovery:")
    print(response)
    
    return response


def test_discover_from_mood():
    """Test discovering destination from user mood/feeling"""
    print("\n" + "="*60)
    print("TEST 2: Discover from Mood & Feeling")
    print("="*60)
    
    agent = Agent(
        tools=[collect_news_tool, collect_weather_tool, collect_flights_tool, collect_trends_tool],
        model=BedrockModel(
            model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
            temperature=0.7,
            max_tokens=4000,
        ),
        system_prompt="""You are an empathetic travel advisor. Interpret user emotions and needs:

1. UNDERSTAND the user's emotional state and desires
2. IDENTIFY 3-4 countries that match their mood
3. COLLECT real-time data (news, weather, trends, flights)
4. RECOMMEND destinations that fulfill their emotional needs

Consider: relaxation, adventure, culture, nature, food, social atmosphere"""
    )
    
    query = """
I'm feeling stressed from work and need to disconnect.
I want somewhere peaceful with beautiful nature.
I enjoy hiking and outdoor activities.
Budget: $3500, departing from LAX in March 2025.

Where should I go to recharge?
"""
    
    print(f"\n📝 User Query:\n{query}")
    print("\n🤖 Agent analyzing mood...")
    
    response = agent(query)
    
    print(f"\n✅ Agent Recommendation:")
    print(response)
    
    return response


def test_discover_from_activities():
    """Test discovering destination from desired activities"""
    print("\n" + "="*60)
    print("TEST 3: Discover from Activities")
    print("="*60)
    
    agent = Agent(
        tools=[collect_news_tool, collect_weather_tool, collect_flights_tool, collect_trends_tool],
        model=BedrockModel(
            model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
            temperature=0.7,
            max_tokens=4000,
        ),
        system_prompt="""You are an activity-focused travel planner. Match activities to destinations:

1. PARSE user's desired activities
2. IDENTIFY countries known for those activities
3. VERIFY current conditions (weather, trends, events)
4. CHECK flight availability and cost
5. RECOMMEND best match with activity details"""
    )
    
    query = """
I want to:
- Attend a major cultural festival or event
- Try street food and local markets
- Take photography of urban landscapes
- Experience nightlife and entertainment

Budget: $5000, flexible dates in February-March 2025, from LAX.

What's the best destination for these activities?
"""
    
    print(f"\n📝 User Query:\n{query}")
    print("\n🤖 Agent matching activities...")
    
    response = agent(query)
    
    print(f"\n✅ Agent Match:")
    print(response)
    
    return response


def test_discover_from_constraints():
    """Test discovering destination with multiple constraints"""
    print("\n" + "="*60)
    print("TEST 4: Discover from Constraints")
    print("="*60)
    
    agent = Agent(
        tools=[collect_news_tool, collect_weather_tool, collect_flights_tool, collect_trends_tool],
        model=BedrockModel(
            model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
            temperature=0.7,
            max_tokens=4000,
        ),
        system_prompt="""You are a constraint-aware travel optimizer. Find destinations that satisfy ALL constraints:

1. FILTER countries by hard constraints (budget, weather, safety)
2. RANK by soft preferences (culture, food, activities)
3. VALIDATE with real-time data
4. PRESENT top options with trade-offs"""
    )
    
    query = """
Constraints:
- Maximum $2500 budget (including flights)
- Must have warm weather (>20°C)
- Safe for solo female traveler
- English-friendly or easy to navigate
- Departing LAX, February 15-22, 2025

Preferences:
- Beach and ocean activities
- Local food scene
- Photography opportunities

Find me the perfect destination!
"""
    
    print(f"\n📝 User Query:\n{query}")
    print("\n🤖 Agent optimizing...")
    
    response = agent(query)
    
    print(f"\n✅ Agent Optimization:")
    print(response)
    
    return response


def main():
    """Run all smart discovery tests"""
    print("\n" + "="*60)
    print("SMART TRAVEL DISCOVERY AGENT TEST SUITE")
    print("="*60)
    
    try:
        # Test 1: Discover from preferences
        print("\n[1/4] Testing preference-based discovery...")
        test_discover_from_preferences()
        
        # Test 2: Discover from mood
        print("\n[2/4] Testing mood-based discovery...")
        test_discover_from_mood()
        
        # Test 3: Discover from activities
        print("\n[3/4] Testing activity-based discovery...")
        test_discover_from_activities()
        
        # Test 4: Discover from constraints
        print("\n[4/4] Testing constraint-based discovery...")
        test_discover_from_constraints()
        
        print("\n" + "="*60)
        print("✅ ALL DISCOVERY TESTS COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
