"""Flight collector using Amadeus API only"""

import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class BrowserFlightCollector:
    """Collect flight information using Amadeus API only"""

    MAX_TOKENS = 2000
    AMADEUS_BASE_URL = "https://test.api.amadeus.com"

    def __init__(self, region: str = "us-west-2"):
        self.region = region
        self.amadeus_client_id = os.getenv("AMADEUS_API_KEY")
        self.amadeus_client_secret = os.getenv("AMADEUS_API_SECRET")
        self._amadeus_token = None
        self._token_expiry = None

    def search_flights(
        self,
        origin: str,
        destination: str,
        start_date: str,
        end_date: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
        num_results: int = 10,
    ) -> List[Dict]:
        """Search flights using Amadeus API with mock fallback"""

        print(f"✈️  Searching Flight Info...")

        # Validate dates - adjust if in the past
        today = datetime.now().date()
        try:
            dep_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if dep_date < today:
                start_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")
                print(f"⚠️  Adjusted departure date to {start_date}")
        except ValueError:
            pass

        if end_date:
            try:
                ret_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                if ret_date < today:
                    end_date = (today + timedelta(days=14)).strftime("%Y-%m-%d")
                    print(f"⚠️  Adjusted return date to {end_date}")
            except ValueError:
                pass

        # Try Amadeus API
        if self.amadeus_client_id and self.amadeus_client_secret:
            try:
                flights = self._search_amadeus(
                    origin, destination, start_date, end_date, preferences, num_results
                )
                if flights:
                    print(f"✅ Found {len(flights)} flights via Amadeus API")
                    return flights
            except Exception as e:
                print(f"⚠️  Amadeus API failed: {e}")

        # Immediate mock fallback
        print("⚠️  Using mock flight data")
        return self._get_fallback_flights(origin, destination, start_date)

    def _search_amadeus(
        self,
        origin: str,
        destination: str,
        start_date: str,
        end_date: Optional[str],
        preferences: Optional[Dict[str, Any]],
        num_results: int,
    ) -> List[Dict]:
        """Search flights using Amadeus API
        
        Args:
            origin: IATA airport code for departure (e.g., "LAX", "NRT")
            destination: IATA airport code for arrival (e.g., "JFK", "HND")
            start_date: Departure date in YYYY-MM-DD format (e.g., "2025-03-15")
            end_date: Return date in YYYY-MM-DD format for round-trip (optional)
            preferences: Search filters (optional). Supported keys:
                - max_price (int): Maximum price in USD (e.g., 1000)
                - stops (int): Number of stops, 0 for non-stop only
                - cabin (str): Cabin class - "economy", "premium", "business", "first"
                - airlines (List[str]): Include only these airline codes (e.g., ["AA", "UA", "DL"])
                - exclude_airlines (List[str]): Exclude these airline codes (e.g., ["NK", "F9"])
                - max_duration (int): Maximum flight duration in hours (e.g., 10)
            num_results: Maximum number of flight offers to return (default: 10)
            
        Returns:
            List of flight dictionaries with keys: airline, price, currency, 
            departure_time, arrival_time, duration, stops, origin, destination, departure_date
            
        Example:
            preferences = {
                "max_price": 1000,
                "cabin": "economy",
                "airlines": ["AA", "UA"],
                "stops": 0,
                "max_duration": 8
            }
        """
        token = self._get_amadeus_token()
        if not token:
            return []

        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": start_date,
            "adults": 1,
            "currencyCode": "USD",
            "max": num_results,
        }

        if end_date:
            params["returnDate"] = end_date
        
        if preferences:
            if "max_price" in preferences:
                params["maxPrice"] = preferences["max_price"]
            if "stops" in preferences and preferences["stops"] == 0:
                params["nonStop"] = "true"
            if "cabin" in preferences:
                cabin_map = {"economy": "ECONOMY", "premium": "PREMIUM_ECONOMY", "business": "BUSINESS", "first": "FIRST"}
                params["travelClass"] = cabin_map.get(preferences["cabin"].lower(), "ECONOMY")
            if "airlines" in preferences:
                params["includedAirlineCodes"] = ",".join(preferences["airlines"])
            if "exclude_airlines" in preferences:
                params["excludedAirlineCodes"] = ",".join(preferences["exclude_airlines"])
            if "max_duration" in preferences:
                params["maxDuration"] = preferences["max_duration"]

        response = requests.get(
            f"{self.AMADEUS_BASE_URL}/v2/shopping/flight-offers",
            headers=headers,
            params=params,
            timeout=10,
        )
        
        if response.status_code != 200:
            print(f"⚠️  Amadeus API error {response.status_code}: {response.text[:200]}")
        
        response.raise_for_status()

        data = response.json()
        return self._transform_amadeus_response(data, origin, destination, start_date)

    def _get_amadeus_token(self) -> Optional[str]:
        """Get Amadeus OAuth token with caching"""
        if (
            self._amadeus_token
            and self._token_expiry
            and datetime.now() < self._token_expiry
        ):
            return self._amadeus_token

        response = requests.post(
            f"{self.AMADEUS_BASE_URL}/v1/security/oauth2/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"grant_type=client_credentials&client_id={self.amadeus_client_id}&client_secret={self.amadeus_client_secret}",
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        self._amadeus_token = data["access_token"]
        self._token_expiry = datetime.now() + timedelta(seconds=data["expires_in"] - 60)
        return self._amadeus_token

    def _transform_amadeus_response(
        self, data: Dict, origin: str, destination: str, start_date: str
    ) -> List[Dict]:
        """Transform Amadeus response to standard format"""
        flights = []
        for offer in data.get("data", []):
            itinerary = offer["itineraries"][0]
            segment = itinerary["segments"][0]
            
            dep_time = segment["departure"]["at"].split("T")[1][:5]
            arr_time = segment["arrival"]["at"].split("T")[1][:5]
            duration = itinerary["duration"].replace("PT", "").replace("H", "h ").replace("M", "m").lower()
            
            flights.append(
                {
                    "airline": segment["carrierCode"],
                    "price": float(offer["price"]["total"]),
                    "currency": offer["price"]["currency"],
                    "departure_time": dep_time,
                    "arrival_time": arr_time,
                    "duration": duration,
                    "stops": len(itinerary["segments"]) - 1,
                    "origin": origin,
                    "destination": destination,
                    "departure_date": start_date,
                }
            )
        return flights

    def _get_fallback_flights(self, origin: str, dest: str, date: str) -> List[Dict]:
        """Fallback mock data"""
        return [
            {
                "airline": "Mock",
                "price": 450,
                "currency": "USD",
                "departure_time": "10:00",
                "arrival_time": "14:00",
                "duration": "4h",
                "stops": 0,
                "origin": origin,
                "destination": dest,
                "departure_date": date,
            }
        ]

    def collect(
        self,
        origin: str,
        destination: str,
        start_date: str,
        num_results: int = 10,
        **kwargs,
    ) -> List[Dict]:
        """Alias for search_flights"""
        return self.search_flights(
            origin, destination, start_date, num_results=num_results
        )
