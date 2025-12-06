import requests


def search_books(query: str, limit: int = 5) -> list:
    """
    Search OpenLibrary for books.
    """
    try:
        url = "https://openlibrary.org/search.json"
        params = {
            "q": query,
            "limit": limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        books = []
        
        for doc in data.get("docs", []):
            book = {
                "title": doc.get("title", "Unknown"),
                "authors": doc.get("author_name", ["Unknown"]),
                "first_publish_year": doc.get("first_publish_year", "N/A"),
                "isbn": doc.get("isbn", ["N/A"])[0] if doc.get("isbn") else "N/A",
                "subjects": doc.get("subject", [])[:5] if doc.get("subject") else [],
                "url": f"https://openlibrary.org{doc.get('key', '')}" if doc.get("key") else None
            }
            books.append(book)
        
        return books
    except Exception as e:
        return [{"error": f"OpenLibrary search failed: {str(e)}"}]


def get_book_by_isbn(isbn: str) -> dict:
    """
    Get book details by ISBN.
    """
    try:
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        key = f"ISBN:{isbn}"
        
        if key in data:
            book = data[key]
            return {
                "title": book.get("title", "Unknown"),
                "authors": [a.get("name", "") for a in book.get("authors", [])],
                "publishers": [p.get("name", "") for p in book.get("publishers", [])],
                "publish_date": book.get("publish_date", "N/A"),
                "pages": book.get("number_of_pages", "N/A"),
                "subjects": [s.get("name", "") for s in book.get("subjects", [])[:5]],
                "url": book.get("url", "")
            }
        else:
            return {"error": f"No book found with ISBN: {isbn}"}
    except Exception as e:
        return {"error": f"OpenLibrary ISBN lookup failed: {str(e)}"}
