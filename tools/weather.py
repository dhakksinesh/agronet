import requests
from typing import Dict, Any
from utils import logger
from crewai.tools.base_tool import tool
from config import WEATHER_API_BASE

COORDINATES_MAP = {
    "Coimbatore": (11.00555, 76.96612),
    "Chennai": (13.08268, 80.27071),
    "Madurai": (9.92520, 78.11977),
    "Trichy": (10.79048, 78.70467),
    "Salem": (11.66432, 78.14601),
    "Bangalore": (12.97159, 77.59456),
    "Mysore": (12.29581, 76.63938),
    "Hubli": (15.36470, 75.12395),
    "Mangalore": (12.91414, 74.85595),
    "Belgaum": (15.84966, 74.49755),
    "Mumbai": (19.07609, 72.87770),
    "Pune": (18.52043, 73.85674),
    "Nagpur": (21.14580, 79.08815),
    "Nashik": (19.99757, 73.78980),
    "Aurangabad": (19.87616, 75.34331),
    "Amritsar": (31.63397, 74.87226),
    "Ludhiana": (30.90096, 75.85727),
    "Jalandhar": (31.32601, 75.57618),
    "Patiala": (30.33978, 76.38687),
    "Bathinda": (30.21099, 74.94547),
    "Lucknow": (26.84669, 80.94616),
    "Kanpur": (26.44992, 80.33187),
    "Varanasi": (25.31764, 82.97391),
    "Agra": (27.17667, 78.00807),
    "Allahabad": (25.43580, 81.84631),
}

def _safe_get(daily: dict, key: str, default: float = 0) -> float:
    vals = daily.get(key, [default])
    return vals[0] if vals else default

@tool("Get weather forecast data for a location")
def get_weather_data(latitude: float, longitude: float, days: int = 7) -> Dict[str, Any]:
    """Fetch weather forecast from Open-Meteo API."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "forecast_days": days,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "hourly": "relativehumidity_2m"
    }
    response = requests.get(WEATHER_API_BASE, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    daily = data.get("daily", {})
    humidity_values = data.get("hourly", {}).get("relativehumidity_2m", [50])
    humidity_avg = sum(humidity_values) / max(len(humidity_values), 1)
    logger.debug(f"Weather data retrieved for lat={latitude}, lon={longitude}")
    return {
        "temperature_max": _safe_get(daily, "temperature_2m_max"),
        "temperature_min": _safe_get(daily, "temperature_2m_min"),
        "rainfall": _safe_get(daily, "precipitation_sum"),
        "wind_speed": _safe_get(daily, "windspeed_10m_max"),
        "humidity_avg": humidity_avg,
    }

def get_coordinates(district: str, state: str) -> tuple:
    district_clean = district.strip().title()
    if district_clean in COORDINATES_MAP:
        return COORDINATES_MAP[district_clean]
    try:
        logger.info(f"Querying Open-Meteo Geocoding API for {district}, {state}")
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": district, "count": 1, "language": "en", "format": "json"}
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        results = data.get("results")
        if results:
            lat = results[0]["latitude"]
            lon = results[0]["longitude"]
            logger.debug(f"Geocoding API found coordinates for {district}: {lat}, {lon}")
            return lat, lon
    except Exception as e:
        logger.error(f"Geocoding API failed for {district}: {e}")
    raise ValueError(f"Could not retrieve coordinates for {district}, {state}")
