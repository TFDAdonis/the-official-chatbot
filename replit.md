# Multi-Source Search Assistant

## Overview
A Streamlit chatbot application that searches multiple free APIs simultaneously to answer user queries. No API keys required for the core functionality - all search APIs are free and public.

## Features
- **Parallel Search**: Searches all 16 sources simultaneously using concurrent processing
- **Chat Interface**: Message history with user/assistant conversation flow
- **Rich Results**: Formatted results with links, summaries, and raw data viewer
- **No API Keys Required**: All search APIs are free and don't require authentication

## Available Search Sources (16 total)
1. **DuckDuckGo Web** - Web search results
2. **DuckDuckGo Instant** - Quick answers
3. **DuckDuckGo News** - News articles
4. **Wikipedia** - Encyclopedia articles
5. **Wikidata** - Structured knowledge base
6. **ArXiv** - Scientific papers and research
7. **PubMed** - Medical and life sciences research
8. **OpenLibrary** - Book information
9. **Dictionary API** - Word definitions and phonetics
10. **REST Countries** - Country information
11. **Quotable** - Famous quotes
12. **GitHub** - Code repositories
13. **Stack Overflow** - Programming Q&A
14. **Nominatim (OSM)** - Geocoding and location data
15. **wttr.in** - Weather data
16. **OpenAQ** - Air quality data

## Project Structure
```
├── app.py                      # Main Streamlit application
├── services/
│   ├── __init__.py
│   ├── arxiv_service.py        # ArXiv API integration
│   ├── duckduckgo_service.py   # DuckDuckGo search + news
│   ├── wikipedia_service.py    # Wikipedia API
│   ├── weather_service.py      # wttr.in and Open-Meteo
│   ├── openaq_service.py       # Air quality data
│   ├── wikidata_service.py     # Wikidata queries
│   ├── openlibrary_service.py  # Book search
│   ├── pubmed_service.py       # Medical research
│   ├── nominatim_service.py    # Geocoding/maps
│   ├── dictionary_service.py   # Word definitions
│   ├── countries_service.py    # Country information
│   ├── quotes_service.py       # Famous quotes
│   ├── github_service.py       # GitHub repositories
│   └── stackexchange_service.py # Stack Overflow Q&A
└── .streamlit/
    └── config.toml             # Streamlit configuration
```

## How to Run
```bash
streamlit run app.py --server.port 5000
```

## Dependencies
- streamlit
- requests
- arxiv
- wikipedia-api
- ddgs (DuckDuckGo search)

## Recent Changes
- 2025-12-06: Initial implementation with all 10 search sources
- 2025-12-06: Removed OpenAI dependency - uses simple result formatting
- 2025-12-06: Implemented parallel search using ThreadPoolExecutor
- 2025-12-06: Updated DuckDuckGo from deprecated package to new 'ddgs' package
- 2025-12-06: Added 5 new search services: Dictionary, Countries, Quotes, GitHub, Stack Overflow
- 2025-12-06: Added news search functionality via DuckDuckGo
