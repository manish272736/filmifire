import requests
from config import Config

def search_tmdb_movie(query, year=None):
    """
    Searches TMDB for a movie and returns high-res poster and metadata.
    """
    api_key = getattr(Config, "TMDB_API_KEY", None)
    if not api_key or not query:
        return None

    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": api_key,
        "query": query.strip(),
        "include_adult": False
    }
    
    if year:
        params["year"] = year

    try:
        response = requests.get(url, params=params, timeout=6)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                top = results[0]
                poster_path = top.get("poster_path")
                
                # Convert language code to readable name
                lang_map = {
                    "hi": "Hindi",
                    "te": "Telugu",
                    "ta": "Tamil",
                    "kn": "Kannada",
                    "ml": "Malayalam",
                    "en": "English",
                    "pa": "Punjabi",
                    "mr": "Marathi",
                    "bn": "Bengali"
                }
                raw_lang = top.get("original_language", "hi").lower()
                lang_display = lang_map.get(raw_lang, raw_lang.upper())

                return {
                    "title": top.get("title"),
                    "poster_url": f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "",
                    "backdrop_url": f"https://image.tmdb.org/t/p/original{top.get('backdrop_path')}" if top.get("backdrop_path") else "",
                    "release_date": top.get("release_date", ""),
                    "language": lang_display,
                    "overview": top.get("overview", "")
                }
    except Exception as e:
        print(f"TMDB Fetch Error: {e}")

    return None