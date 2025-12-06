import requests


def search_country(query: str) -> dict:
    """
    Search for country information using REST Countries API.
    No API key required.
    """
    try:
        url = f"https://restcountries.com/v3.1/name/{query}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            return {"message": f"No country found matching '{query}'"}
        
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return {"message": f"No country found matching '{query}'"}
        
        country = data[0]
        
        currencies = []
        if country.get("currencies"):
            for code, info in country.get("currencies", {}).items():
                currencies.append(f"{info.get('name', '')} ({code})")
        
        languages = []
        if country.get("languages"):
            languages = list(country.get("languages", {}).values())
        
        return {
            "name": country.get("name", {}).get("common", "Unknown"),
            "official_name": country.get("name", {}).get("official", "Unknown"),
            "capital": country.get("capital", ["N/A"])[0] if country.get("capital") else "N/A",
            "region": country.get("region", "N/A"),
            "subregion": country.get("subregion", "N/A"),
            "population": country.get("population", "N/A"),
            "area_km2": country.get("area", "N/A"),
            "currencies": currencies,
            "languages": languages[:5],
            "flag_emoji": country.get("flag", ""),
            "map_url": country.get("maps", {}).get("googleMaps", ""),
            "source": "REST Countries API"
        }
    except Exception as e:
        return {"error": f"Country search failed: {str(e)}"}
