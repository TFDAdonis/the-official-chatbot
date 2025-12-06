import requests
import xml.etree.ElementTree as ET


def search_pubmed(query: str, max_results: int = 5) -> list:
    """
    Search PubMed for medical and life sciences research.
    """
    try:
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=10)
        search_response.raise_for_status()
        search_data = search_response.json()
        
        id_list = search_data.get("esearchresult", {}).get("idlist", [])
        
        if not id_list:
            return [{"message": f"No PubMed articles found for '{query}'"}]
        
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml"
        }
        
        fetch_response = requests.get(fetch_url, params=fetch_params, timeout=15)
        fetch_response.raise_for_status()
        
        root = ET.fromstring(fetch_response.content)
        articles = []
        
        for article in root.findall(".//PubmedArticle"):
            title_elem = article.find(".//ArticleTitle")
            abstract_elem = article.find(".//AbstractText")
            pmid_elem = article.find(".//PMID")
            
            authors = []
            for author in article.findall(".//Author")[:3]:
                last_name = author.find("LastName")
                fore_name = author.find("ForeName")
                if last_name is not None:
                    name = last_name.text
                    if fore_name is not None:
                        name = f"{fore_name.text} {name}"
                    authors.append(name)
            
            pub_date = article.find(".//PubDate")
            year = pub_date.find("Year").text if pub_date is not None and pub_date.find("Year") is not None else "N/A"
            
            abstract_text = abstract_elem.text if abstract_elem is not None else "No abstract available"
            if len(abstract_text) > 500:
                abstract_text = abstract_text[:500] + "..."
            
            articles.append({
                "title": title_elem.text if title_elem is not None else "Unknown",
                "authors": authors,
                "abstract": abstract_text,
                "year": year,
                "pmid": pmid_elem.text if pmid_elem is not None else "N/A",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid_elem.text}/" if pmid_elem is not None else None
            })
        
        return articles
    except Exception as e:
        return [{"error": f"PubMed search failed: {str(e)}"}]
