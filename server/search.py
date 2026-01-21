from duckduckgo_search import DDGS
import pandas as pd
import logging
import asyncio

logger = logging.getLogger("search")

def _search_sync(query, max_results):
    results = []
    try:
        with DDGS() as ddgs:
            # DDGS().text is a generator in some versions, or returns list
            # We iterate to be safe
            ddg_gen = ddgs.text(query, max_results=max_results, region="in-en")
            if ddg_gen:
                for r in ddg_gen:
                    results.append(r)
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}")
        return []
    return results

async def search_api(query, max_results=30):
    if not query:
        return pd.DataFrame()
    
    # Run synchronous search in a separate thread to avoid blocking main loop
    results = await asyncio.to_thread(_search_sync, query, max_results)

    if not results:
        return pd.DataFrame(columns=["link", "rank", "snippet", "title"])
        
    # DuckDuckGo returns keys: 'href', 'title', 'body'
    res_df = pd.DataFrame(results)
    
    rename_map = {
        'href': 'link',
        'body': 'snippet'
    }
    res_df = res_df.rename(columns=rename_map)
    
    res_df["rank"] = list(range(1, res_df.shape[0] + 1))
    
    for col in ["link", "rank", "snippet", "title"]:
        if col not in res_df.columns:
            res_df[col] = "" 
            
    res_df = res_df[["link", "rank", "snippet", "title"]]
    
    return res_df

async def search(query):
    return await search_api(query)