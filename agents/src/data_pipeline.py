"""
Data Collection and Validation Pipeline
Orchestrates: Collection → Validation → Storage (RDS + S3)
"""

from typing import Dict, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import json

from collectors.news import BrowserNewsCollector
from collectors.weather import BrowserWeatherCollector
from collectors.flight import BrowserFlightCollector
from collectors.trends import BrowserTrendCollector
from validators.fake_news_validator import IValidator, MockValidator
from storage.rds_storage import RDSStorage
from storage.knowledge_base_sync import KnowledgeBaseSync


class DataPipeline:
    """Orchestrates data collection, validation, and storage"""

    def __init__(
        self,
        validator: IValidator,
        rds_storage: Optional[RDSStorage] = None,
        kb_sync: Optional[KnowledgeBaseSync] = None,
        region: str = "us-west-2",
    ):
        """
        Initialize pipeline with dependencies

        Args:
            validator: Content validator (SageMaker or Mock)
            rds_storage: Optional RDS storage service
            kb_sync: Optional Knowledge Base sync service
            region: AWS region
        """
        self.validator = validator
        self.rds_storage = rds_storage
        self.kb_sync = kb_sync
        self.region = region

        # Initialize collectors
        self.news_collector = BrowserNewsCollector(region=region)
        self.weather_collector = BrowserWeatherCollector(region=region)
        self.flight_collector = BrowserFlightCollector(region=region)
        self.sns_collector = BrowserTrendCollector(region=region)

    def collect_and_validate_news(
        self, country_code: str, max_results: int = 10
    ) -> List[Dict]:
        """
        Collect news and validate with fake news detection

        Returns:
            Validated news articles
        """
        print(f"\n📰 Collecting and validating news for {country_code}...")

        # Collect news
        articles = self.news_collector.get_top_headlines(
            country_code=country_code, max_results=max_results
        )

        # Validate articles
        validated = []
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}"
            validation = self.validator.validate(text)

            if validation["is_valid"]:
                article["validation"] = validation
                validated.append(article)
            else:
                print(f"🚫 Filtered: {article.get('title', '')[:50]}...")

        print(f"✅ Validated {len(validated)}/{len(articles)} articles")
        return validated

    def collect_travel_data(
        self,
        country_code: str,
        origin_airport: Optional[str] = None,
        departure_date: Optional[str] = None,
        include_flights: bool = True,
        include_sns: bool = True,
    ) -> Dict:
        """
        Collect comprehensive travel data for a country

        Args:
            country_code: 2-letter country code
            origin_airport: Origin airport for flight search
            departure_date: Departure date for flights
            include_flights: Include flight data
            include_sns: Include SNS trends

        Returns:
            Comprehensive travel data dictionary
        """
        print(f"\n🌍 Collecting travel data for {country_code}...")

        data = {
            "country_code": country_code.upper(),
            "timestamp": datetime.now().isoformat(),
        }

        # Parallel collection
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}

            # News (with validation)
            futures["news"] = executor.submit(
                self.collect_and_validate_news, country_code
            )

            # Weather
            futures["weather"] = executor.submit(
                self.weather_collector.get_weather, country_code
            )

            # Flights (if requested)
            if include_flights and origin_airport and departure_date:
                # Get destination airport from country
                dest_airports = {
                    "jp": "NRT",
                    "us": "JFK",
                    "uk": "LHR",
                    "fr": "CDG",
                    "de": "FRA",
                    "cn": "PEK",
                }
                dest = dest_airports.get(country_code.lower(), "JFK")

                futures["flights"] = executor.submit(
                    self.flight_collector.search_flights,
                    origin_airport,
                    dest,
                    departure_date,
                )

            # SNS trends (if requested)
            if include_sns:
                futures["sns_trends"] = executor.submit(
                    self.sns_collector.get_trending_topics, country_code
                )

            # Collect results
            for key, future in futures.items():
                try:
                    data[key] = future.result(timeout=60)
                except Exception as e:
                    print(f"⚠️  {key} collection failed: {e}")
                    data[key] = []

        return data

    def store_data(self, data: Dict, country_code: str):
        """
        Store data in RDS and S3/Knowledge Base

        Args:
            data: Collected and validated data
            country_code: Country code
        """
        print(f"\n💾 Storing data for {country_code}...")

        # Store in RDS
        if self.rds_storage:
            try:
                # Store news articles
                if "news" in data:
                    for article in data["news"]:
                        self.rds_storage.store_article(
                            country_code=country_code, article=article
                        )

                # Store weather
                if "weather" in data:
                    self.rds_storage.store_weather(
                        country_code=country_code, weather=data["weather"]
                    )

                # Store flights
                if "flights" in data:
                    for flight in data["flights"]:
                        self.rds_storage.store_flight(
                            country_code=country_code, flight=flight
                        )

                # Store SNS trends
                if "sns_trends" in data:
                    for trend in data["sns_trends"]:
                        self.rds_storage.store_sns_trend(
                            country_code=country_code, trend=trend
                        )

                print("✅ Data stored in RDS")
            except Exception as e:
                print(f"⚠️  RDS storage failed: {e}")

        # Store in S3 for Knowledge Base
        if self.kb_sync:
            try:
                # Create structured document for KB
                doc_content = self._format_for_kb(data, country_code)

                # Upload to S3 with prefix strategy
                prefix = f"travel_data/{country_code.lower()}/{datetime.now().strftime('%Y-%m-%d')}"
                self.kb_sync.upload_document(
                    content=doc_content,
                    prefix=prefix,
                    filename=f"{country_code}_travel_data.json",
                )

                print("✅ Data stored in S3/Knowledge Base")
            except Exception as e:
                print(f"⚠️  S3/KB storage failed: {e}")

    def _format_for_kb(self, data: Dict, country_code: str) -> str:
        """Format data for Knowledge Base ingestion"""
        doc = {
            "country": country_code.upper(),
            "timestamp": datetime.now().isoformat(),
            "summary": f"Travel data for {country_code.upper()}",
            "news_summary": self._summarize_news(data.get("news", [])),
            "weather_summary": self._summarize_weather(data.get("weather", {})),
            "flight_summary": self._summarize_flights(data.get("flights", [])),
            "sns_summary": self._summarize_sns(data.get("sns_trends", [])),
            "raw_data": data,
        }
        return json.dumps(doc, indent=2)

    def _summarize_news(self, articles: List[Dict]) -> str:
        """Create news summary for KB"""
        if not articles:
            return "No news available"

        validated_count = sum(
            1 for a in articles if a.get("validation", {}).get("is_valid")
        )
        avg_sentiment = sum(a.get("sentiment", 0) for a in articles) / len(articles)

        return (
            f"{validated_count} validated articles, avg sentiment: {avg_sentiment:.2f}"
        )

    def _summarize_weather(self, weather: Dict) -> str:
        """Create weather summary for KB"""
        if not weather:
            return "No weather data"

        return f"{weather.get('description', 'Unknown')}, {weather.get('temp', 0)}°C, mood impact: {weather.get('mood_impact', 0):.2f}"

    def _summarize_flights(self, flights: List[Dict]) -> str:
        """Create flight summary for KB"""
        if not flights:
            return "No flight data"

        avg_price = sum(f.get("price", 0) for f in flights) / len(flights)
        return f"{len(flights)} flights available, avg price: ${avg_price:.0f}"

    def _summarize_sns(self, trends: List[Dict]) -> str:
        """Create SNS summary for KB"""
        if not trends:
            return "No SNS trends"

        top_topics = [t.get("topic", "") for t in trends[:3]]
        return f"Trending: {', '.join(top_topics)}"

    def run_full_pipeline(
        self,
        country_code: str,
        origin_airport: Optional[str] = None,
        departure_date: Optional[str] = None,
        store_results: bool = True,
    ) -> Dict:
        """
        Run complete pipeline: collect → validate → store

        Returns:
            Processed data dictionary
        """
        # Collect and validate
        data = self.collect_travel_data(
            country_code=country_code,
            origin_airport=origin_airport,
            departure_date=departure_date,
        )

        # Store if requested
        if store_results:
            self.store_data(data, country_code)

        return data
