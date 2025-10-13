"""Unified data collection service"""

from typing import Dict, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from .news import BrowserNewsCollector
from .weather import BrowserWeatherCollector


class BrowserDataCollectionService:
    """Unified service for data collection"""

    def __init__(self, region: str = "us-west-2", max_workers: int = 2):
        self.region = region
        self.max_workers = max_workers

    def collect_country_data(
        self,
        country_code: str,
        max_news: int = 10,
        city: Optional[str] = None,
        parallel: bool = True,
        validate: bool = False,
        threshold: float = 0.7,
    ) -> Dict:
        """Collect all data for a country"""
        print(f"\n🔍 Collecting data for {country_code.upper()}...")

        if parallel:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                news_future = executor.submit(
                    BrowserNewsCollector(self.region).get_top_headlines,
                    country_code,
                    max_news,
                    validate,
                    threshold,
                )
                weather_future = executor.submit(
                    BrowserWeatherCollector(self.region).collect, country_code, city
                )
                news, weather = news_future.result(timeout=30), weather_future.result(
                    timeout=15
                )
        else:
            news = BrowserNewsCollector(self.region).get_top_headlines(
                country_code, max_news, validate, threshold
            )
            weather = BrowserWeatherCollector(self.region).collect(country_code, city)

        avg_sentiment = (
            sum(a.get("sentiment", 0) for a in news) / len(news) if news else 0.0
        )

        return {
            "country_code": country_code.upper(),
            "news": news,
            "weather": weather,
            "statistics": {
                "news_count": len(news),
                "avg_news_sentiment": round(avg_sentiment, 2),
                "weather_mood_impact": weather.get("mood_impact", 0.0),
                "collection_method": "browser",
                "collection_timestamp": datetime.now().isoformat(),
            },
        }


def collect_data_with_browser(
    country_code: str,
    region: str = "us-west-2",
    validate: bool = False,
    threshold: float = 0.7,
    **kwargs,
) -> Dict:
    """Convenience function"""
    return BrowserDataCollectionService(region=region).collect_country_data(
        country_code, validate=validate, threshold=threshold, **kwargs
    )
