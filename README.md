# SixthSense

## Overview
SixthSense is a full‑stack app that searches the web (Google Custom Search), summarizes the top results, and compares two webpages using LLMs.

### Features
- Search with ranked results
- Query summary from the first 3 snippets (returned with results)
- Side‑by‑side website comparison (key points, features, structure, strengths, limitations)
- Structured server logging with request correlation (X‑Request‑ID)

### Tech Stack
- Client: React + TypeScript + Vite + TailwindCSS
- Server: Python + Flask
- LLMs: Groq (via LangChain)
- Search: Google Custom Search API (CSE)

## Project Structure
client/ (React app)
  src/
    components/
    utils/
    App.tsx
server/ (Flask API)
  controller.py  (routes, logging, request correlation)
  services.py    (LLM-based summary/compare)
  search.py      (Google CSE calls with timeouts/retries)
  prompts.py     (prompt templates)
  settings.py    (CSE config)
myenv/ (Windows Python venv)

## Prerequisites
- Node.js 18+
- Python 3.13
- Groq API key
- Google CSE API key and search engine id (cx)

## Configuration
1) Create environment file for server:
server/.env
GROQ_API_KEY=your_groq_api_key_here

2) Set Google CSE credentials in server/settings.py:
SEARCH_KEY = "<google_api_key>"
SEARCH_ID  = "<cse_cx>"
COUNTRY    = "india"   # or your target country code

## Run Locally (Windows PowerShell)
1) Server
From repository root:
cd server
../myenv/Scripts/Activate.ps1
pip install -r requirements.txt
python controller.py
Server runs at http://127.0.0.1:5000

2) Client
From repository root:
cd client
npm install
npm run dev
Client runs at Vite dev URL (e.g., http://127.0.0.1:5173)

## API
Base URL: http://127.0.0.1:5000

- POST /search
  - Body: { "query": string }
  - Response: { "results": [ { link, rank, snippet, title } ], "summary_result": [string] }
  - Notes: Summary is computed from the first three snippets of the returned results.

- GET /query-summary?q=...
  - Response: { "summary_result": [string] }
  - Returns [] when snippets are unavailable. Prefer POST /search for consistent results+summary.

- POST /compare
  - Body: { "url1": string, "url2": string, "title1"?: string, "title2"?: string }
  - Response: { "websites": [ { url, title, keyPoints, uniqueFeatures, contentStructure, advantages, limitations }, { ... } ] }

## Behavior & Flow
1) Client sends POST /search with the user query.
2) Server queries Google CSE, builds summary from the first 3 snippets, and returns results + summary_result together.
3) Client renders the summary first, then the result list.
4) For comparison, client sends POST /compare with two URLs (and optional titles); server fetches, cleans, summarizes and returns structured comparison.

## Logging & Error Handling
- Request correlation: X‑Request‑ID is generated/propagated and returned in responses.
- External calls: timeouts + basic retries for Google CSE; LLM calls have timeouts.
- Endpoints validate input and return structured JSON errors; fallback to empty arrays where applicable to avoid 500s.

## Troubleshooting
- Empty or inconsistent summaries: Use POST /search (returns results + summary in one call).
- No results: Ensure SEARCH_KEY and SEARCH_ID are valid in server/settings.py.
- LLM issues/timeouts: Check GROQ_API_KEY; see server logs with request IDs.
- Module import warnings in editor: Activate the Python venv (myenv).

## Security Notes
- Do not commit secrets. Use environment variables for keys in production.
- Consider adding authentication and rate limiting before public deployment.

## License
Provided as‑is without warranty. Add your preferred license text here.
