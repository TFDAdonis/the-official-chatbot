import requests


def geocode_location(query: str) -> dict:
    """
    Geocode a location using OSM Nominatim (free).
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        headers = {
            "User-Agent": "MultiSearchChatbot/1.0 (contact@example.com)"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            return {"error": f"Location '{query}' not found"}
        
        result = data[0]
        address = result.get("address", {})
        
        return {
            "display_name": result.get("display_name", "Unknown"),
            "latitude": float(result.get("lat", 0)),
            "longitude": float(result.get("lon", 0)),
            "type": result.get("type", "Unknown"),
            "country": address.get("country", "N/A"),
            "state": address.get("state", "N/A"),
            "city": address.get("city") or address.get("town") or address.get("village", "N/A"),
            "osm_url": f"https://www.openstreetmap.org/?mlat={result.get('lat')}&mlon={result.get('lon')}&zoom=15"
        }
    except Exception as e:
        return {"error": f"Geocoding failed: {str(e)}"}


def reverse_geocode(latitude: float, longitude: float) -> dict:
    """
    Reverse geocode coordinates to address.
    """
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "addressdetails": 1
        }
        headers = {
            "User-Agent": "MultiSearchChatbot/1.0 (contact@example.com)"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        address = data.get("address", {})
        
        return {
            "display_name": data.get("display_name", "Unknown"),
            "country": address.get("country", "N/A"),
            "state": address.get("state", "N/A"),
            "city": address.get("city") or address.get("town") or address.get("village", "N/A"),
            "road": address.get("road", "N/A"),
            "postcode": address.get("postcode", "N/A")
        }
    except Exception as e:
        return {"error": f"Reverse geocoding failed: {str(e)}"}
