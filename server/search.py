from settings import *
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
import pandas as pd
from urllib.parse import quote_plus
import logging
from time import sleep
# from summerizer import get_summary

logger = logging.getLogger("search")


def _http_get_json(url: str, retries: int = 2, backoff_seconds: float = 0.5):
    last_error = None
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except (Timeout, HTTPError, RequestException) as e:
            last_error = e
            if attempt < retries:
                sleep(backoff_seconds * (2 ** attempt))
            else:
                break
    raise last_error


def search_api(query, pages=int(RESULT_COUNT/10)):
    if not query:
        return pd.DataFrame()
    results = []
    for i in range(0, pages):
        start = i*10+1
        url = SEARCH_URL.format(
            key=SEARCH_KEY,
            cx=SEARCH_ID,
            query=quote_plus(query),
            start=start
        )
        try:
            data = _http_get_json(url)
            if isinstance(data, dict) and "items" in data:
                results += data["items"]
        except Exception as e:
            logger.warning(f"search_api page {i+1} failed: {e}")
            continue
    if not results:
        return pd.DataFrame(columns=["link", "rank", "snippet", "title"])
    res_df = pd.DataFrame.from_dict(results)
    if res_df.empty:
        return pd.DataFrame(columns=["link", "rank", "snippet", "title"])
    res_df["rank"] = list(range(1, res_df.shape[0] + 1))
    # Only keep expected columns if present
    keep_cols = [c for c in ["link", "rank", "snippet", "title"] if c in res_df.columns]
    res_df = res_df[keep_cols]
    return res_df

def scrape_page(links):
    html = []
    for link in links:
        try:
            data = requests.get(link, timeout=5)
            data.raise_for_status()
            html.append(data.text)
        except RequestException:
            html.append("")
    return html

# def process_results(df):
#     # Define a function to apply to each row
#     def apply_summary(row):
#         if row['rank'] <= 5:
#             return get_summary(row['link'])
#         else:
#             return row['snippet']
    
#     # Apply the function to the DataFrame and create a new 'summary' column
#     df['summary'] = df.apply(apply_summary, axis=1)
#     return df

def search(query):
    columns = ["query", "rank", "link", "title", "snippet", "summary", "created"]
    # storage = DBStorage()

    # stored_results = storage.query_results(query)
    # if stored_results.shape[0] > 0:
    #     stored_results["created"] = pd.to_datetime(stored_results["created"])
    #     return stored_results[columns]

    # print("No results in database.  Using the API.")
    results = search_api(query)
    # results=process_results(results)
    # results["query"] = query
    # results["created"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    # results = results[columns]
    # print(results)
    # results.apply(lambda x: storage.insert_row(x), axis=1)
    # print(f"Inserted {results.shape[0]} records.")
    return results