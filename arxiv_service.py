import arxiv


def search_arxiv(query: str, max_results: int = 5) -> list:
    """
    Search ArXiv for scientific papers.
    Returns a list of paper summaries.
    """
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for paper in client.results(search):
            results.append({
                "title": paper.title,
                "authors": [author.name for author in paper.authors[:3]],
                "summary": paper.summary[:500] + "..." if len(paper.summary) > 500 else paper.summary,
                "published": paper.published.strftime("%Y-%m-%d") if paper.published else "N/A",
                "url": paper.entry_id,
                "categories": paper.categories[:3] if paper.categories else []
            })
        
        return results
    except Exception as e:
        return [{"error": f"ArXiv search failed: {str(e)}"}]
