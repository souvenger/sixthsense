import aiohttp
import pandas as pd
import logging
from settings import SERPAPI_KEY

logger = logging.getLogger("search")

async def search_api(query, max_results=10):
    if not query:
        return pd.DataFrame()
    
    if not SERPAPI_KEY:
        logger.error("SERPAPI_KEY is missing in settings")
        return pd.DataFrame(columns=["link", "rank", "snippet", "title"])

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": max_results,
        "gl": "in", # India
        "hl": "en"  # English
    }
    
    url = "https://serpapi.com/search.json"
    
    results = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                
                # SerpApi puts organic results in 'organic_results'
                organic_results = data.get("organic_results", [])
                for result in organic_results:
                    results.append({
                        "link": result.get("link"),
                        "title": result.get("title"),
                        "snippet": result.get("snippet") or result.get("description", ""),
                        "rank": result.get("position")
                    })
    except Exception as e:
        logger.warning(f"SerpApi search failed: {e}")
        return pd.DataFrame(columns=["link", "rank", "snippet", "title"])

    if not results:
        return pd.DataFrame(columns=["link", "rank", "snippet", "title"])
        
    res_df = pd.DataFrame(results)
    
    # Ensure rank is sequential if position is missing or inconsistent
    if "rank" not in res_df.columns or res_df["rank"].isnull().any():
        res_df["rank"] = list(range(1, res_df.shape[0] + 1))
    
    # Ensure all required columns exist
    for col in ["link", "rank", "snippet", "title"]:
        if col not in res_df.columns:
            res_df[col] = "" 
            
    res_df = res_df[["link", "rank", "snippet", "title"]]
    
    return res_df

async def search(query):
    return await search_api(query)