from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
import os
import logging
from prompts import *
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# Ensure API key exists; do not override existing env unintentionally
if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("GROQ_API_KEY is not set in environment")



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

deepseek_70b = ChatGroq(
    model="DeepSeek-R1-Distill-Llama-70b",
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


def clean_webpage_content(url):
    """First get and summarize webpage content to reduce tokens"""
    if not url or not isinstance(url, str) or not _is_valid_url(url):
        logger.warning(f"clean_webpage_content called with invalid url: {url}")
        return None
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        if not docs or not getattr(docs[0], 'page_content', ''):
            logger.info(f"No content loaded for url: {url}")
            return None

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=20000,
            chunk_overlap=0,
            length_function=len
        )
        chunks = text_splitter.split_text(docs[0].page_content)
        if not chunks:
            logger.info(f"No chunks produced for url: {url}")
            return None

        prompt = PromptTemplate(input_variables=["content"], template=cleaning_prompt)
        summary_chain = prompt | llm_70b
        result = summary_chain.invoke({"content": chunks[0]})
        return getattr(result, 'content', None)
    except Exception as e:
        logger.exception(f"Error processing {url}: {str(e)}")
        return None




def compare_websites(url1, url2):
    """Compare two websites using their summarized content"""
    if not _is_valid_url(url1) or not _is_valid_url(url2):
        logger.warning("compare_websites received invalid urls")
        return None

    logger.info("Summarizing website 1...")
    summary1 = clean_webpage_content(url1)
    logger.info("Summarizing website 2...")
    summary2 = clean_webpage_content(url2)
    
    if not summary1 or not summary2:
        logger.info("One or both summaries are empty; cannot compare")
        return None
    
    prompt = PromptTemplate(input_variables=["doc1", "doc2"], template=comparator_prompt)
    result = prompt | llm_70b
    response = result.invoke({"doc1": summary1, "doc2": summary2})
    
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

def get_summary(url):
    if not _is_valid_url(url):
        logger.warning(f"get_summary called with invalid url: {url}")
        return None
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        if not docs or not getattr(docs[0], 'page_content', ''):
            return None
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=20000,
            chunk_overlap=0,
            length_function=len
        )
        chunks = text_splitter.split_text(docs[0].page_content)
        if not chunks:
            return None
        prompt = PromptTemplate(input_variables=["content"], template=cleaning_prompt)
        clean_chain = prompt | llm_70b
        cleaned = clean_chain.invoke({"content": chunks[0]})
        cleaned_text = getattr(cleaned, 'content', '')
        if not cleaned_text:
            return None

        prompt = PromptTemplate(input_variables=["content"], template=summary_template)
        summary_chain = prompt | llm_70b
        final = summary_chain.invoke({"content": cleaned_text})
        return getattr(final, 'content', None)
    except Exception:
        logger.exception("Error in get_summary")
        return None

def get_summerized_results(snippets):
    if not snippets or not isinstance(snippets, str):
        return None
    try:
        prompt = PromptTemplate(input_variables=["paragraph"], template=summarized_template)
        summary_chain = prompt | llm_70b
        res = summary_chain.invoke({"paragraph": snippets})
        return getattr(res, 'content', None)
    except Exception:
        logger.exception("Error in get_summerized_results")
        return None


