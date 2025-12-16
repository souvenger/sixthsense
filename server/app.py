from flask import Flask, request, jsonify, g
from services import compare_websites, get_summary, get_summerized_results
from search import search
from flask_cors import CORS
import pandas as pd
import json
import os
import logging
import time
import uuid

app = Flask(__name__)
# Allow requests from the deployed frontend. Avoid using wildcard with credentials.
CORS(
    app,
    resources={r"/*": {"origins": [
        "https://sixthsense-nu.vercel.app"
    ]}},
    supports_credentials=False,
    max_age=3600
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
    # Add correlation id to response
    response.headers['X-Request-ID'] = getattr(g, 'request_id', '-')
    # Basic access log
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

# Simple in-memory storage to replace global variables
search_data = {
    'query': '',
    'results': pd.DataFrame(),
    'snippets': ''
}

@app.route('/')
def home():
    return "Welcome"

@app.route("/search", methods=['POST'])
def search_form():
    body = request.get_json(silent=True) or {}
    query = (body.get('query') or '').strip()
    if not query:
        return jsonify({"error": "Missing or empty 'query' in request body", "request_id": getattr(g, 'request_id', '-') }), 400
    results = search(query)
    
    # Update search data
    search_data['query'] = query
    search_data['results'] = results
    
    # Use only the top 3 results for summary input and join with separators
    top_snippets = results['snippet'].head(3).fillna('') if not results.empty else []
    search_data['snippets'] = '. '.join(top_snippets) if len(top_snippets) > 0 else ''

    # Generate summary directly here to keep it consistent with current results
    sentences: list[str] = []
    try:
        if search_data['snippets']:
            summary_result = get_summerized_results(search_data['snippets'])
            if summary_result:
                start_idx, end_idx = summary_result.find('['), summary_result.find(']')
                sentences = summary_result[start_idx + 1:end_idx].split('|') if start_idx != -1 and end_idx != -1 else []
    except Exception:
        logger.exception("Failed to generate summary in /search", extra={"request_id": getattr(g, 'request_id', '-')})
        sentences = []

    return jsonify({'results': results.to_dict(orient='records'), 'summary_result': sentences})

@app.route('/compare-results', methods=['GET', 'POST'])
def compare_webpages():
    """
    API to compare two webpages.
    For POST, Request Body (JSON):
        - url1: The URL of the first webpage.
        - url2: The URL of the second webpage.
    For GET, Query Parameters:
        - url1, url2, title1, title2
    """
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
        return jsonify({"error": "Missing 'url1' or 'url2' in request body", "request_id": getattr(g, 'request_id', '-') }), 400
    
    try:
        comparison_result = compare_websites(url1, url2)
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
        if len(website_keys) < 2:
            return None
        temp = []
        for url, title, web in zip([url1, url2], [title1, title2], website_keys[:2]):
            website_entry = {
                "url": url,
                "title": title,
                "keyPoints": key_info.get(web, []),
                "uniqueFeatures": unique.get(web, []),
                "contentStructure": structure.get(web, {}),
                "advantages": strengths.get(web, []),
                "limitations": limits.get(web, [])
            }
            temp.append(website_entry)
        return temp
    except Exception:
        return None

@app.route('/summary', methods=['POST'])
def get_summary_api():
    """
    API to get a cleaned and summarized result of a webpage.
    Request Body (JSON):
        - url: The URL of the webpage.
    """
    data = request.get_json(silent=True) or {}
    url = data.get('url') if data else None

    if not url:
        return jsonify({"error": "Missing 'url' in request body", "request_id": getattr(g, 'request_id', '-') }), 400

    try:
        summary = get_summary(url)
        if not summary:
            return jsonify({"error": "Failed to process the webpage", "request_id": getattr(g, 'request_id', '-') }), 500
        return jsonify({"summary": summary}), 200
    except Exception as e:
        logger.exception("Error in /summary", extra={"request_id": getattr(g, 'request_id', '-')})
        return jsonify({"error": str(e), "request_id": getattr(g, 'request_id', '-') }), 500

@app.route('/query-summary', methods=['GET'])
def query_summary():
    """
    API to get summarized results for a query.
    """
    try:
        # If snippets are empty, try to build them from provided query param
        if not search_data['snippets']:
            q = (request.args.get('q') or '').strip()
            if q:
                results = search(q)
                search_data['results'] = results
                top_snippets = results['snippet'].head(3).fillna('') if not results.empty else []
                search_data['snippets'] = '. '.join(top_snippets) if len(top_snippets) > 0 else ''

        if not search_data['snippets']:
            # No snippets to summarize; return empty list gracefully
            return jsonify({"summary_result": []}), 200

        summary_result = get_summerized_results(search_data['snippets'])
        # print(summary_result)
        
        if not summary_result:
            return jsonify({"summary_result": []}), 200

        # Extract sentences directly from the summary result
        start_idx, end_idx = summary_result.find('['), summary_result.find(']')
        sentences = summary_result[start_idx + 1:end_idx].split('|') if start_idx != -1 and end_idx != -1 else []

        return jsonify({"summary_result": sentences}), 200
    except Exception as e:
        logger.exception("Error in /query-summary", extra={"request_id": getattr(g, 'request_id', '-')})
        return jsonify({"error": str(e), "request_id": getattr(g, 'request_id', '-') }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render gives PORT
    app.run(host="0.0.0.0", port=port, debug=True)