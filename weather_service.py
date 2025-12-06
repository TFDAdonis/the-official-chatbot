import requests


def get_weather_wttr(location: str) -> dict:
    """
    Get weather from wttr.in (free, no API key).
    """
    try:
        url = f"https://wttr.in/{location}?format=j1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        current = data.get("current_condition", [{}])[0]
        
        return {
            "location": location,
            "temperature_c": current.get("temp_C", "N/A"),
            "temperature_f": current.get("temp_F", "N/A"),
            "condition": current.get("weatherDesc", [{}])[0].get("value", "N/A"),
            "humidity": current.get("humidity", "N/A"),
            "wind_speed_kmph": current.get("windspeedKmph", "N/A"),
            "feels_like_c": current.get("FeelsLikeC", "N/A"),
            "visibility": current.get("visibility", "N/A"),
            "source": "wttr.in"
        }
    except Exception as e:
        return {"error": f"Weather fetch failed: {str(e)}"}


def get_weather_open_meteo(latitude: float, longitude: float) -> dict:
    """
    Get weather from Open-Meteo (free, no API key).
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "relative_humidity_2m", "weather_code", "wind_speed_10m"],
            "timezone": "auto"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        current = data.get("current", {})
        
        weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            95: "Thunderstorm"
        }
        
        return {
            "latitude": latitude,
            "longitude": longitude,
            "temperature_c": current.get("temperature_2m", "N/A"),
            "humidity": current.get("relative_humidity_2m", "N/A"),
            "condition": weather_codes.get(current.get("weather_code", -1), "Unknown"),
            "wind_speed_kmph": current.get("wind_speed_10m", "N/A"),
            "source": "Open-Meteo"
        }
    except Exception as e:
        return {"error": f"Open-Meteo fetch failed: {str(e)}"}
