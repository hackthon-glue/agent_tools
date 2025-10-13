"""Weather collector using wttr.in API"""

from typing import Dict, Optional
from datetime import datetime
import requests
from .base import BaseBrowserCollector


class BrowserWeatherCollector(BaseBrowserCollector):
    """Collect weather using AgentCore Browser"""

    MAX_TOKENS = 1500

    PROMPT_TEMPLATE = """### OBJECTIVE
Your task is to act as a weather data extractor. Navigate to the provided weather API URL and extract current weather information precisely according to the specified schema.

### CONTEXT OF THIS SEARCH
The user is collecting current weather data for the city: {city}

### INSTRUCTIONS
1. Go to the URL: https://wttr.in/{city}?format=j1
2. The page displays weather data in JSON format.
3. Extract the current weather conditions from the "current_condition" section.
4. Return the data as a single, valid JSON object. Do not include any other text or explanations in your response.

### OUTPUT SCHEMA
Return a JSON object with current weather data. If no data is available, return an empty object `{{}}`.
The object must conform to this schema:
```json
{{
  "temp": "number (temperature in Celsius)",
  "feels_like": "number (feels like temperature in Celsius)",
  "description": "string (weather description)",
  "humidity": "number (humidity percentage)",
  "wind_speed": "number (wind speed in km/h)"
}}
```"""

    DEFAULT_CITIES = {
        "jp": "Tokyo",
        "us": "Washington",
        "uk": "London",
        "fr": "Paris",
        "de": "Berlin",
        "cn": "Beijing",
        "kr": "Seoul",
        "in": "New Delhi",
        "br": "Brasilia",
        "au": "Canberra",
    }

    def collect(self, country_code: str, city: Optional[str] = None, **kwargs) -> Dict:
        """Alias for get_weather"""
        return self.get_weather(country_code, city)

    def get_weather(self, country_code: str, city: Optional[str] = None) -> Dict:
        city = city or self.DEFAULT_CITIES.get(country_code.lower(), "London")
        print(f"🌐 Collecting weather for {city}...")

        try:
            data = self._fetch_weather_direct(city)
            if data and "temp" in data:
                return self._process_weather(data, city, country_code)
        except Exception as e:
            print(f"⚠️  Direct API failed: {str(e)[:100]}")
            try:
                print(f"🔄 Trying browser scraping...")
                data = self._fetch_weather_with_browser(city)
                if data and "temp" in data:
                    return self._process_weather(data, city, country_code)
            except Exception as e:
                print(f"⚠️  Browser scraping failed: {str(e)[:100]}")

        return self._process_weather(
            self._get_fallback_weather(country_code), city, country_code
        )

    def _fetch_weather_direct(self, city: str) -> Dict:
        """Fetch from wttr.in API"""
        response = requests.get(
            f"https://wttr.in/{city}?format=j1",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5,
        )
        response.raise_for_status()
        current = response.json()["current_condition"][0]

        return {
            "temp": float(current["temp_C"]),
            "feels_like": float(current["FeelsLikeC"]),
            "description": current["weatherDesc"][0]["value"],
            "humidity": int(current["humidity"]),
            "wind_speed": float(current["windspeedKmph"]),
        }

    def _process_weather(self, data: Dict, city: str, country: str) -> Dict:
        """Add metadata and mood impact"""
        data.update(
            {
                "city": city,
                "country": country.upper(),
                "timestamp": datetime.now().isoformat(),
                "mood_impact": self._estimate_mood(
                    data.get("temp", 20), data.get("description", "")
                ),
            }
        )
        return data

    def _estimate_mood(self, temp: float, desc: str) -> float:
        """Estimate mood impact"""
        score = 0.3 if 18 <= temp <= 25 else (-0.3 if temp < 5 or temp > 35 else 0.0)
        desc_lower = desc.lower()
        if any(w in desc_lower for w in ["clear", "sunny"]):
            score += 0.3
        elif any(w in desc_lower for w in ["rain", "storm"]):
            score -= 0.2
        return max(-1.0, min(1.0, score))

    def _fetch_weather_with_browser(self, city: str) -> Dict:
        """Fetch weather using browser scraping"""
        prompt = self.PROMPT_TEMPLATE.format(city=city)
        results = self._scrape_with_browser(prompt)
        return results[0] if results else {}

    def _get_fallback_weather(self, country_code: str) -> Dict:
        """Generate fallback weather"""
        month = datetime.now().month
        temp = 28.0 if 6 <= month <= 8 else (15.0 if 3 <= month <= 5 else 5.0)
        return {
            "temp": temp,
            "feels_like": temp - 1,
            "description": "MOCK",
            "humidity": 60,
            "wind_speed": 10.0,
        }
