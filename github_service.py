import requests


def search_github_repos(query: str, limit: int = 5) -> list:
    """
    Search GitHub repositories.
    No API key required for basic searches.
    """
    try:
        url = "https://api.github.com/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": limit
        }
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "MultiSearchChatbot/1.0"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            return [{"message": f"No GitHub repositories found for '{query}'"}]
        
        repos = []
        for repo in items[:limit]:
            repos.append({
                "name": repo.get("full_name", "Unknown"),
                "description": repo.get("description", "No description")[:200] if repo.get("description") else "No description",
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "language": repo.get("language", "N/A"),
                "url": repo.get("html_url", ""),
                "topics": repo.get("topics", [])[:5]
            })
        
        return repos
    except Exception as e:
        return [{"error": f"GitHub search failed: {str(e)}"}]
