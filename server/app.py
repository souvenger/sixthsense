from flask import Flask, request, jsonify, g
from services import compare_websites, get_summary, get_summerized_results
from search import search
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pandas as pd
import json
import os
import logging
import time
import uuid
import asyncio
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Security: Load allowed origins from env
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS").split(",")

CORS(
    app,
    resources={r"/*": {"origins": ALLOWED_ORIGINS}},
    supports_credentials=False,
    max_age=3600
)

# Rate Limiting (In-memory for now)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Configure logging once for the server
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(name)s] [%(request_id)s] %(message)s'
)
logger = logging.getLogger("server")

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        try:
            record.request_id = getattr(g, 'request_id', '-')
        except Exception:
            record.request_id = '-'
        return True

for handler in logging.getLogger().handlers:
    handler.addFilter(RequestIdFilter())

@app.before_request
def add_request_context():
    g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    g.start_time = time.time()
    logger.info(
        "Incoming request",
        extra={"request_id": g.request_id}
    )

@app.after_request
def add_response_headers(response):
    response.headers['X-Request-ID'] = getattr(g, 'request_id', '-')
    try:
        duration_ms = int((time.time() - getattr(g, 'start_time', time.time())) * 1000)
        logger.info(
            f"Handled {request.method} {request.path} in {duration_ms}ms with {response.status_code}",
            extra={"request_id": getattr(g, 'request_id', '-')}
        )
    except Exception:
        pass
    return response

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    logger.exception("Unhandled server error", extra={"request_id": getattr(g, 'request_id', '-')})
    return jsonify({
        "error": "Internal server error",
        "request_id": getattr(g, 'request_id', '-')
    }), 500

@app.route('/')
def home():
    return "Welcome"

@app.route("/search", methods=['POST'])
@limiter.limit("10 per minute")
async def search_form():
    body = request.get_json(silent=True) or {}
    query = (body.get('query') or '').strip()
    if not query:
        return jsonify({"error": "Missing or empty 'query' in request body", "request_id": getattr(g, 'request_id', '-') }), 400
    
    # Async Search
    results = await search(query)
    
    # Calculate snippets for summary
    top_snippets = results['snippet'].head(3).fillna('') if not results.empty else []
    snippets_text = '. '.join(top_snippets) if len(top_snippets) > 0 else ''

    # Generate summary directly
    sentences = []
    try:
        if snippets_text:
            summary_result = await get_summerized_results(snippets_text)
            if summary_result:
                # Basic parsing validity check logic from original code
                # Note: original logic assumed specific format with brackets and pipes
                # We attempt to parse it, but fallback gracefully
                start_idx, end_idx = summary_result.find('['), summary_result.to_str().rfind(']') if hasattr(summary_result, 'to_str') else summary_result.rfind(']')
                # If cannot find brackets, just split by pipe or return full text if no pipe
                if start_idx != -1 and end_idx != -1:
                    sentences = summary_result[start_idx + 1:end_idx].split('|')
                else:
                     # Fallback: if model didn't output brackets
                    sentences = summary_result.split('|')
                
                # Clean up whitespace
                sentences = [s.strip() for s in sentences if s.strip()]
                
    except Exception:
        logger.exception("Failed to generate summary in /search", extra={"request_id": getattr(g, 'request_id', '-')})
        sentences = []

    return jsonify({'results': results.to_dict(orient='records'), 'summary_result': sentences})


@app.route('/compare-results', methods=['GET', 'POST'])
@limiter.limit("5 per minute") 
async def compare_webpages():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        url1 = data.get('url1')
        url2 = data.get('url2')
        title1 = data.get('title1')
        title2 = data.get('title2')
    else:  # GET request
        url1 = request.args.get('url1')
        url2 = request.args.get('url2')
        title1 = request.args.get('title1')
        title2 = request.args.get('title2')

    if not url1 or not url2:
        return jsonify({"error": "Missing 'url1' or 'url2'", "request_id": getattr(g, 'request_id', '-') }), 400
    
    try:
        comparison_result = await compare_websites(url1, url2)
        final_comparison_data = convert_into_compare_format(comparison_result, url1, url2, title1, title2)
        
        if not final_comparison_data:
            return jsonify({"error": "Failed to compare the webpages", "request_id": getattr(g, 'request_id', '-') }), 500
        return jsonify({"websites": final_comparison_data}), 200
    except Exception as e:
        logger.exception("Error in /compare", extra={"request_id": getattr(g, 'request_id', '-')})
        return jsonify({"error": str(e), "request_id": getattr(g, 'request_id', '-') }), 500

def convert_into_compare_format(original_data, url1, url2, title1, title2):
    if not original_data or not isinstance(original_data, dict):
        return None
    try:
        key_info = original_data.get("key_information", {})
        unique = original_data.get("unique_features", {})
        structure = original_data.get("content_structure", {})
        strengths = original_data.get("strengths", {})
        limits = original_data.get("limitations", {})
        website_keys = list(key_info.keys())
        # If model returned "web1", "web2" explicitly as keys as per prompt
        if "web1" in website_keys and "web2" in website_keys:
             keys_to_use = ["web1", "web2"]
        elif len(website_keys) >= 2:
            keys_to_use = website_keys[:2]
        else:
            # Fallback if model messed up keys
            return None

        temp = []
        for url, title, web_key in zip([url1, url2], [title1, title2], keys_to_use):
            website_entry = {
                "url": url,
                "title": title,
                "keyPoints": key_info.get(web_key, []),
                "uniqueFeatures": unique.get(web_key, []),
                "contentStructure": structure.get(web_key, {}),
                "advantages": strengths.get(web_key, []),
                "limitations": limits.get(web_key, [])
            }
            temp.append(website_entry)
        return temp
    except Exception:
        return None

@app.route('/summary', methods=['POST'])
@limiter.limit("10 per minute")
async def get_summary_api():
    data = request.get_json(silent=True) or {}
    url = data.get('url') if data else None

    if not url:
        return jsonify({"error": "Missing 'url' in request body", "request_id": getattr(g, 'request_id', '-') }), 400

    try:
        summary = await get_summary(url)
        if not summary:
            return jsonify({"error": "Failed to process the webpage", "request_id": getattr(g, 'request_id', '-') }), 500
        return jsonify({"summary": summary}), 200
    except Exception as e:
        logger.exception("Error in /summary", extra={"request_id": getattr(g, 'request_id', '-')})
        return jsonify({"error": str(e), "request_id": getattr(g, 'request_id', '-') }), 500

@app.route('/query-summary', methods=['GET'])
@limiter.limit("10 per minute")
async def query_summary():
    """
    Stateless /query-summary. Requires 'q' param to perform search + summarize.
    """
    try:
        q = (request.args.get('q') or '').strip()
        if not q:
            # Stateless: we cannot summarize nothing.
            return jsonify({"summary_result": [], "error": "Query 'q' parameter is required for stateless summary"}), 400
            
        # Perform search to get content to summarize
        results = await search(q)
        top_snippets = results['snippet'].head(3).fillna('') if not results.empty else []
        snippets_text = '. '.join(top_snippets) if len(top_snippets) > 0 else ''

        if not snippets_text:
            return jsonify({"summary_result": []}), 200
            
        summary_result = await get_summerized_results(snippets_text)
        
        if not summary_result:
            return jsonify({"summary_result": []}), 200

        # Parsing logic (similar to search_form)
        start_idx, end_idx = summary_result.find('['), summary_result.rfind(']')
        if start_idx != -1 and end_idx != -1:
             sentences = summary_result[start_idx + 1:end_idx].split('|')
        else:
             sentences = summary_result.split('|')

        sentences = [s.strip() for s in sentences if s.strip()]
        return jsonify({"summary_result": sentences}), 200
    except Exception as e:
        logger.exception("Error in /query-summary", extra={"request_id": getattr(g, 'request_id', '-')})
        return jsonify({"error": str(e), "request_id": getattr(g, 'request_id', '-') }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)