import requests


def get_air_quality(city: str) -> dict:
    """
    Get air quality data from OpenAQ API (free, no API key required for basic usage).
    """
    try:
        url = "https://api.openaq.org/v2/latest"
        params = {
            "city": city,
            "limit": 10,
            "order_by": "lastUpdated"
        }
        headers = {
            "Accept": "application/json"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return {
                "city": city,
                "message": f"No air quality data found for '{city}'",
                "data": []
            }
        
        measurements = []
        for result in results[:5]:
            location_data = {
                "location": result.get("location", "Unknown"),
                "city": result.get("city", city),
                "country": result.get("country", "N/A"),
                "measurements": []
            }
            
            for m in result.get("measurements", []):
                location_data["measurements"].append({
                    "parameter": m.get("parameter", "N/A"),
                    "value": m.get("value", "N/A"),
                    "unit": m.get("unit", "N/A"),
                    "last_updated": m.get("lastUpdated", "N/A")
                })
            
            measurements.append(location_data)
        
        return {
            "city": city,
            "data": measurements,
            "source": "OpenAQ"
        }
    except Exception as e:
        return {"error": f"OpenAQ fetch failed: {str(e)}"}
