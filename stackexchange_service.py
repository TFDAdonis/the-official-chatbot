import requests


def search_stackoverflow(query: str, limit: int = 5) -> list:
    """
    Search Stack Overflow questions.
    No API key required for basic searches.
    """
    try:
        url = "https://api.stackexchange.com/2.3/search/advanced"
        params = {
            "q": query,
            "order": "desc",
            "sort": "relevance",
            "site": "stackoverflow",
            "pagesize": limit,
            "filter": "!nNPvSNVZJS"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            return [{"message": f"No Stack Overflow questions found for '{query}'"}]
        
        questions = []
        for q in items[:limit]:
            questions.append({
                "title": q.get("title", "Unknown"),
                "score": q.get("score", 0),
                "answer_count": q.get("answer_count", 0),
                "is_answered": q.get("is_answered", False),
                "tags": q.get("tags", [])[:5],
                "url": q.get("link", ""),
                "view_count": q.get("view_count", 0)
            })
        
        return questions
    except Exception as e:
        return [{"error": f"Stack Overflow search failed: {str(e)}"}]
