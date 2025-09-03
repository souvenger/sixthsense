import logging
from typing import Optional, List
import requests
from urllib.parse import urlparse
import time
from requests.exceptions import RequestException, Timeout, ConnectionError

# Configure logging
logger = logging.getLogger(__name__)

def get_summary(url: str, max_retries: int = 3, timeout: int = 30) -> Optional[str]:
    """
    Enhanced method to get summary from a website with better error handling and fallback strategies.
    
    Args:
        url: The URL to summarize
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
    
    Returns:
        Summary string or None if failed
    """
    
    # Validate URL
    if not _is_valid_url(url):
        logger.error(f"Invalid URL provided: {url}")
        return None
    
    # Try multiple strategies to get content
    docs = None
    strategies = [
        lambda: _load_with_webbaseloader(url, timeout),
        lambda: _load_with_requests(url, timeout),
        lambda: _load_with_alternative_headers(url, timeout)
    ]
    
    for i, strategy in enumerate(strategies):
        try:
            logger.info(f"Attempting strategy {i+1} for URL: {url}")
            docs = strategy()
            if docs and len(docs) > 0 and docs[0].page_content.strip():
                logger.info(f"Successfully loaded content using strategy {i+1}")
                break
        except Exception as e:
            logger.warning(f"Strategy {i+1} failed: {str(e)}")
            continue
    
    if not docs or not docs[0].page_content.strip():
        logger.error(f"Failed to load content from URL: {url}")
        return None
    
    try:
        return _process_content(docs[0].page_content, max_retries)
    except Exception as e:
        logger.error(f"Failed to process content: {str(e)}")
        return None

def _is_valid_url(url: str) -> bool:
    """Validate if the URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def _load_with_webbaseloader(url: str, timeout: int):
    """Load content using WebBaseLoader with timeout"""
    try:
        loader = WebBaseLoader(url)
        # Set timeout if WebBaseLoader supports it
        if hasattr(loader, 'requests_kwargs'):
            loader.requests_kwargs = {'timeout': timeout}
        return loader.load()
    except Exception as e:
        logger.warning(f"WebBaseLoader failed: {str(e)}")
        raise

def _load_with_requests(url: str, timeout: int):
    """Fallback method using requests with better headers"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    response.raise_for_status()
    
    # Create a mock document object similar to WebBaseLoader
    class MockDoc:
        def __init__(self, content):
            self.page_content = _extract_text_from_html(content)
    
    return [MockDoc(response.text)]

def _load_with_alternative_headers(url: str, timeout: int):
    """Another fallback with different headers"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
    }
    
    response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    response.raise_for_status()
    
    class MockDoc:
        def __init__(self, content):
            self.page_content = _extract_text_from_html(content)
    
    return [MockDoc(response.text)]

def _extract_text_from_html(html_content: str) -> str:
    """Extract clean text from HTML content"""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except ImportError:
        logger.warning("BeautifulSoup not available, using basic text extraction")
        # Basic HTML tag removal
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', html_content)

def _process_content(content: str, max_retries: int) -> Optional[str]:
    """Process the content through cleaning and summarization with retries"""
    
    # Check if content is substantial enough
    if len(content.strip()) < 100:
        logger.warning("Content too short to summarize")
        return None
    
    # Split into chunks if content is too large
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=20000,
        chunk_overlap=200,  # Added overlap for better context
        length_function=len
    )
    chunks = text_splitter.split_text(content)
    
    if not chunks:
        logger.error("No chunks created from content")
        return None
    
    # Try to get the most relevant chunk (not always the first one)
    best_chunk = _select_best_chunk(chunks)
    
    # Clean the content with retries
    cleaned_text = _retry_llm_call(
        lambda: _clean_content(best_chunk),
        max_retries,
        "cleaning"
    )
    
    if not cleaned_text:
        logger.error("Failed to clean content")
        return None
    
    # Summarize the cleaned content with retries
    summary = _retry_llm_call(
        lambda: _summarize_content(cleaned_text),
        max_retries,
        "summarization"
    )
    
    return summary

def _select_best_chunk(chunks: List[str]) -> str:
    """Select the chunk most likely to contain main content"""
    if len(chunks) == 1:
        return chunks[0]
    
    # Score chunks based on content indicators
    def score_chunk(chunk):
        score = 0
        words = chunk.lower().split()
        
        # Prefer chunks with more substantial content
        score += len(words) * 0.1
        
        # Prefer chunks with common content indicators
        content_indicators = ['article', 'content', 'main', 'text', 'paragraph', 'section']
        score += sum(1 for word in words if word in content_indicators)
        
        # Penalize chunks with navigation/menu indicators
        nav_indicators = ['menu', 'navigation', 'sidebar', 'footer', 'header', 'cookie']
        score -= sum(2 for word in words if word in nav_indicators)
        
        return score
    
    # Return the highest scoring chunk
    return max(chunks, key=score_chunk)

def _retry_llm_call(func, max_retries: int, operation_name: str):
    """Retry LLM calls with exponential backoff"""
    for attempt in range(max_retries):
        try:
            result = func()
            if result and result.content.strip():
                return result.content.strip()
        except Exception as e:
            logger.warning(f"{operation_name} attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            continue
    
    logger.error(f"All {max_retries} {operation_name} attempts failed")
    return None

def _clean_content(content: str):
    """Clean the content using the LLM"""
    prompt = PromptTemplate(input_variables=["content"], template=cleaning_prompt)
    clean_chain = prompt | deepseek_70b
    return clean_chain.invoke({"content": content})

def _summarize_content(content: str):
    """Summarize the content using the LLM"""
    prompt = PromptTemplate(input_variables=["content"], template=summary_template)
    summary_chain = prompt | deepseek_70b
    return summary_chain.invoke({"content": content})

# Alternative version with async support (if needed)
async def get_summary_async(url: str, max_retries: int = 3, timeout: int = 30) -> Optional[str]:
    """Async version of get_summary for better performance in web applications"""
    import asyncio
    import aiohttp
    
    # Validate URL
    if not _is_valid_url(url):
        logger.error(f"Invalid URL provided: {url}")
        return None
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
        try:
            # Try to get content with different headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html_content = await response.text()
                    text_content = _extract_text_from_html(html_content)
                    
                    if text_content.strip():
                        return _process_content(text_content, max_retries)
                    
        except Exception as e:
            logger.error(f"Async loading failed: {str(e)}")
    
    return None