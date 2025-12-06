import requests


def get_definition(word: str) -> dict:
    """
    Get word definition from Free Dictionary API.
    No API key required.
    """
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            return {"message": f"No definition found for '{word}'"}
        
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return {"message": f"No definition found for '{word}'"}
        
        entry = data[0]
        meanings = []
        
        for meaning in entry.get("meanings", [])[:3]:
            definitions = []
            for defn in meaning.get("definitions", [])[:2]:
                definitions.append({
                    "definition": defn.get("definition", ""),
                    "example": defn.get("example", "")
                })
            meanings.append({
                "part_of_speech": meaning.get("partOfSpeech", ""),
                "definitions": definitions
            })
        
        phonetics = []
        for p in entry.get("phonetics", []):
            if p.get("text"):
                phonetics.append(p.get("text"))
        
        return {
            "word": entry.get("word", word),
            "phonetics": phonetics[:2] if phonetics else [],
            "meanings": meanings,
            "source": "Free Dictionary API"
        }
    except Exception as e:
        return {"error": f"Dictionary lookup failed: {str(e)}"}
