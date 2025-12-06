import requests


def search_quotes(query: str, limit: int = 5) -> list:
    """
    Search for quotes using Quotable API.
    No API key required.
    """
    try:
        url = "https://api.quotable.io/search/quotes"
        params = {
            "query": query,
            "limit": limit
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return get_random_quotes(limit)
        
        quotes = []
        for quote in results[:limit]:
            quotes.append({
                "content": quote.get("content", ""),
                "author": quote.get("author", "Unknown"),
                "tags": quote.get("tags", [])
            })
        
        return quotes if quotes else [{"message": "No quotes found"}]
    except Exception as e:
        return get_random_quotes(limit)


def get_random_quotes(limit: int = 3) -> list:
    """
    Get random quotes as fallback.
    """
    try:
        url = f"https://api.quotable.io/quotes/random?limit={limit}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        quotes = []
        
        for quote in data:
            quotes.append({
                "content": quote.get("content", ""),
                "author": quote.get("author", "Unknown"),
                "tags": quote.get("tags", [])
            })
        
        return quotes if quotes else [{"message": "No quotes available"}]
    except Exception as e:
        return [{"error": f"Quotes fetch failed: {str(e)}"}]
