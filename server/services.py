from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json
import os
import logging
from prompts import *
from dotenv import load_dotenv
from urllib.parse import urlparse
import asyncio
import aiohttp
from bs4 import BeautifulSoup

load_dotenv()

# Ensure API key exists; do not override existing env unintentionally
if not os.getenv("GROQ_API_KEY"):
    pass # Let it fail if accessed or expect it set in env

# Initialize the LLM
logger = logging.getLogger("services")

llm_8b = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=60,
    max_retries=2,
)

llm_70b = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=60,
    max_retries=2,
)

def _is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False

async def _fetch_url_text(url: str) -> str:
    if not _is_valid_url(url):
        return None
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=15) as response:
                response.raise_for_status()
                html = await response.text()
                # Basic text extraction
                soup = BeautifulSoup(html, 'html.parser')
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                return soup.get_text()
    except Exception as e:
        logger.warning(f"Failed to fetch/parse {url}: {e}")
        return None

async def clean_webpage_content(url):
    """First get and summarize webpage content to reduce tokens"""
    raw_text = await _fetch_url_text(url)
    if not raw_text:
        logger.info(f"No content loaded for url: {url}")
        return None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=20000,
        chunk_overlap=0,
        length_function=len
    )
    chunks = text_splitter.split_text(raw_text)
    if not chunks:
        logger.info(f"No chunks produced for url: {url}")
        return None

    try:
        prompt = PromptTemplate(input_variables=["content"], template=cleaning_prompt)
        summary_chain = prompt | llm_70b
        # Async invoke
        result = await summary_chain.ainvoke({"content": chunks[0]})
        return getattr(result, 'content', None)
    except Exception as e:
        logger.exception(f"Error processing {url}: {str(e)}")
        return None

async def compare_websites(url1, url2):
    """Compare two websites using their summarized content"""
    if not _is_valid_url(url1) or not _is_valid_url(url2):
        logger.warning("compare_websites received invalid urls")
        return None

    logger.info("Summarizing websites in parallel...")
    summary1, summary2 = await asyncio.gather(
        clean_webpage_content(url1), 
        clean_webpage_content(url2)
    )
    
    if not summary1 or not summary2:
        logger.info("One or both summaries are empty; cannot compare")
        return None
    
    prompt = PromptTemplate(input_variables=["doc1", "doc2"], template=comparator_prompt)
    result = prompt | llm_70b
    response = await result.ainvoke({"doc1": summary1, "doc2": summary2})
    
    try:
        json_str = getattr(response, 'content', '') or ''
        start_idx = json_str.find('{')
        end_idx = json_str.rindex('}') + 1
        if start_idx == -1 or end_idx <= 0:
            logger.info("No JSON object found in model response")
            return None
        json_data = json.loads(json_str[start_idx:end_idx])
        return json_data
    except Exception as e:
        logger.exception(f"Error parsing JSON: {e}")
        return None

async def get_summary(url):
    raw_text = await _fetch_url_text(url)
    if not raw_text:
        return None
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=20000,
        chunk_overlap=0,
        length_function=len
    )
    chunks = text_splitter.split_text(raw_text)
    if not chunks:
        return None

    try:
        prompt = PromptTemplate(input_variables=["content"], template=cleaning_prompt)
        clean_chain = prompt | llm_70b
        cleaned = await clean_chain.ainvoke({"content": chunks[0]})
        cleaned_text = getattr(cleaned, 'content', '')
        if not cleaned_text:
            return None

        prompt = PromptTemplate(input_variables=["content"], template=summary_template)
        summary_chain = prompt | llm_70b
        final = await summary_chain.ainvoke({"content": cleaned_text})
        return getattr(final, 'content', None)
    except Exception:
        logger.exception("Error in get_summary")
        return None

async def get_summerized_results(snippets):
    if not snippets or not isinstance(snippets, str):
        return None
    try:
        prompt = PromptTemplate(input_variables=["paragraph"], template=summarized_template)
        summary_chain = prompt | llm_70b
        res = await summary_chain.ainvoke({"paragraph": snippets})
        return getattr(res, 'content', None)
    except Exception:
        logger.exception("Error in get_summerized_results")
        return None
