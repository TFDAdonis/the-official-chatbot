from ddgs import DDGS


def search_duckduckgo(query: str, max_results: int = 5) -> list:
    """
    Search DuckDuckGo for web results.
    Returns a list of search results.
    """
    try:
        ddgs = DDGS()
        results = []
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "body": r.get("body", ""),
                "url": r.get("href", "")
            })
        return results if results else [{"message": "No web results found"}]
    except Exception as e:
        return [{"error": f"DuckDuckGo search failed: {str(e)}"}]


def get_instant_answer(query: str) -> dict:
    """
    Get instant answer from DuckDuckGo.
    """
    try:
        ddgs = DDGS()
        results = ddgs.answers(query)
        if results:
            return {
                "answer": results[0].get("text", ""),
                "source": results[0].get("url", "")
            }
        return {"answer": None, "source": None}
    except Exception as e:
        return {"error": f"DuckDuckGo instant answer failed: {str(e)}"}


def search_news(query: str, max_results: int = 5) -> list:
    """
    Search DuckDuckGo for news results.
    """
    try:
        ddgs = DDGS()
        results = []
        for r in ddgs.news(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "body": r.get("body", ""),
                "url": r.get("url", ""),
                "source": r.get("source", ""),
                "date": r.get("date", "")
            })
        return results if results else [{"message": "No news found"}]
    except Exception as e:
        return [{"error": f"DuckDuckGo news search failed: {str(e)}"}]
