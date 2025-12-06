import requests


def search_wikidata(query: str, limit: int = 5) -> list:
    """
    Search Wikidata for structured knowledge.
    """
    try:
        url = "https://www.wikidata.org/w/api.php"
        params = {
            "action": "wbsearchentities",
            "search": query,
            "language": "en",
            "limit": limit,
            "format": "json"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get("search", []):
            results.append({
                "id": item.get("id", ""),
                "label": item.get("label", ""),
                "description": item.get("description", ""),
                "url": item.get("concepturi", "")
            })
        
        return results
    except Exception as e:
        return [{"error": f"Wikidata search failed: {str(e)}"}]


def get_wikidata_entity(entity_id: str) -> dict:
    """
    Get detailed information about a Wikidata entity.
    """
    try:
        url = "https://www.wikidata.org/w/api.php"
        params = {
            "action": "wbgetentities",
            "ids": entity_id,
            "languages": "en",
            "format": "json"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        entity = data.get("entities", {}).get(entity_id, {})
        
        labels = entity.get("labels", {}).get("en", {})
        descriptions = entity.get("descriptions", {}).get("en", {})
        
        return {
            "id": entity_id,
            "label": labels.get("value", "Unknown"),
            "description": descriptions.get("value", "No description"),
            "url": f"https://www.wikidata.org/wiki/{entity_id}"
        }
    except Exception as e:
        return {"error": f"Wikidata entity fetch failed: {str(e)}"}
