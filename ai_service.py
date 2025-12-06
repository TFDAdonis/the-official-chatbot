import os
import json
from openai import OpenAI

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def is_configured() -> bool:
    """Check if OpenAI is configured."""
    return OPENAI_API_KEY is not None


def classify_query(query: str) -> dict:
    """
    Classify the user query to determine which APIs to use.
    Returns a dict with categories and keywords.
    """
    if not client:
        return fallback_classify(query)
    
    try:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": """You are a query classifier. Analyze the user's query and determine which data sources would be most helpful.
                    
Available sources:
- arxiv: Scientific papers, research, academic studies
- duckduckgo: General web search, current events, general information
- wikipedia: Encyclopedia knowledge, definitions, historical facts
- weather: Weather conditions, forecasts, climate data
- air_quality: Air pollution, environmental data
- wikidata: Structured facts, entity data
- books: Book information, literature, authors
- pubmed: Medical research, health studies, biology
- geocoding: Location information, addresses, maps

Respond with JSON:
{
    "sources": ["source1", "source2"],
    "location": "city or place name if weather/air quality/geocoding needed",
    "search_terms": "optimized search query"
}"""
                },
                {"role": "user", "content": query}
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=500
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        return fallback_classify(query)


def fallback_classify(query: str) -> dict:
    """Fallback classification when AI is unavailable."""
    query_lower = query.lower()
    sources = []
    location = None
    
    weather_keywords = ["weather", "temperature", "forecast", "rain", "snow", "sunny", "cloudy", "climate"]
    science_keywords = ["research", "study", "paper", "scientific", "experiment", "theory", "physics", "chemistry", "biology", "math"]
    medical_keywords = ["health", "medical", "disease", "treatment", "medicine", "doctor", "hospital", "symptom", "drug", "therapy"]
    book_keywords = ["book", "author", "novel", "literature", "read", "publish", "isbn"]
    location_keywords = ["where is", "location", "address", "map", "coordinates", "find place"]
    air_keywords = ["air quality", "pollution", "aqi", "smog", "pm2.5"]
    
    if any(kw in query_lower for kw in weather_keywords):
        sources.append("weather")
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() in ["in", "at", "for"]:
                if i + 1 < len(words):
                    location = " ".join(words[i+1:]).strip("?.,!")
                    break
    
    if any(kw in query_lower for kw in science_keywords):
        sources.append("arxiv")
    
    if any(kw in query_lower for kw in medical_keywords):
        sources.append("pubmed")
    
    if any(kw in query_lower for kw in book_keywords):
        sources.append("books")
    
    if any(kw in query_lower for kw in location_keywords):
        sources.append("geocoding")
    
    if any(kw in query_lower for kw in air_keywords):
        sources.append("air_quality")
    
    sources.append("wikipedia")
    sources.append("duckduckgo")
    
    return {
        "sources": sources[:4],
        "location": location,
        "search_terms": query
    }


def synthesize_response(query: str, search_results: dict) -> str:
    """
    Synthesize a natural language response from search results.
    """
    if not client:
        return format_results_simple(search_results)
    
    try:
        results_text = json.dumps(search_results, indent=2, default=str)
        
        if len(results_text) > 15000:
            results_text = results_text[:15000] + "\n... (truncated)"
        
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful AI assistant that synthesizes information from multiple search sources.
                    
Your task is to:
1. Analyze the search results provided
2. Extract the most relevant and accurate information
3. Present a clear, comprehensive response to the user's query
4. Cite sources when providing specific facts
5. If there are conflicting information, acknowledge it
6. Be concise but thorough

Format your response in a readable way with sections if needed."""
                },
                {
                    "role": "user",
                    "content": f"User query: {query}\n\nSearch results from various sources:\n{results_text}"
                }
            ],
            max_completion_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error synthesizing response: {str(e)}\n\n{format_results_simple(search_results)}"


def format_results_simple(results: dict) -> str:
    """Simple formatting when AI is unavailable."""
    output = []
    
    for source, data in results.items():
        output.append(f"\n**{source.upper()}**\n")
        
        if isinstance(data, list):
            for item in data[:3]:
                if isinstance(item, dict):
                    if "error" in item:
                        output.append(f"- Error: {item['error']}")
                    elif "title" in item:
                        output.append(f"- **{item.get('title', 'N/A')}**")
                        if "summary" in item:
                            output.append(f"  {item['summary'][:200]}...")
                        if "url" in item:
                            output.append(f"  Link: {item['url']}")
                    else:
                        output.append(f"- {json.dumps(item, default=str)[:200]}")
        elif isinstance(data, dict):
            if "error" in data:
                output.append(f"Error: {data['error']}")
            else:
                for key, value in list(data.items())[:5]:
                    output.append(f"- {key}: {value}")
    
    return "\n".join(output)
