import wikipediaapi


def search_wikipedia(query: str, lang: str = "en") -> dict:
    """
    Search Wikipedia for information.
    Returns article summary and URL.
    """
    try:
        wiki = wikipediaapi.Wikipedia(
            user_agent="MultiSearchChatbot/1.0 (contact@example.com)",
            language=lang
        )
        
        page = wiki.page(query)
        
        if page.exists():
            summary = page.summary[:1000] + "..." if len(page.summary) > 1000 else page.summary
            return {
                "title": page.title,
                "summary": summary,
                "url": page.fullurl,
                "exists": True
            }
        else:
            return {
                "exists": False,
                "message": f"No Wikipedia article found for '{query}'"
            }
    except Exception as e:
        return {"error": f"Wikipedia search failed: {str(e)}"}
