# Cognitive Graph System

A personal cognitive-reflection tool that turns free-form journal/conversation text into a structured graph of recurring thought patterns — usable from a web app or directly from any webpage via a browser extension.

## What it does

You write down (or select) whatever's on your mind. An LLM (Gemini) extracts:
- **Nodes** — recurring cognitive patterns or concepts, each tagged as `active` (current focus), `pending` (noted but not explored yet), or `recurring` (echoes a known pattern)
- **Edges** — relationships between nodes, with a strength/weight and a reason
- **Gaps** — threads you started but didn't finish saying
- **A forward question** — one question worth exploring next

The result is saved to a database and rendered as an interactive graph, so patterns across multiple entries become visible over time instead of staying scattered across separate journal entries.

On top of exact-match extraction, new nodes are also compared against existing ones using embeddings + an LLM similarity check, so semantically related patterns get linked even when worded differently.

## Two ways to use it

1. **Web app** (Streamlit) — paste text directly, see the graph update in the browser.
2. **Browser extension** (Chrome/Edge, Manifest V3) — select text on any webpage, extract it via the popup without leaving the page.

Both paths go through the same backend logic (`services.py`), so behavior is consistent regardless of entry point.

## Tech stack

- **Web app**: Streamlit
- **API backend**: FastAPI (serves the browser extension)
- **LLM**: Google Gemini API (`gemini-3.5-flash` for extraction/comparison, `gemini-embedding-001` for embeddings)
- **Database**: Supabase (Postgres + pgvector)
- **Graph visualization**: networkx + pyvis
- **Browser extension**: JavaScript, Chrome Extension Manifest V3

## Project structure

```
cognitive_graph/
├── app.py              — Streamlit UI
├── api.py              — FastAPI backend (serves the browser extension)
├── services.py         — shared core logic (process_extraction), used by both app.py and api.py
├── extract.py          — Gemini API calls (extraction, embedding, semantic comparison, usage logging)
├── database.py         — Supabase reads/writes, pgvector pre-filtering, transaction calls
├── graph.py            — networkx + pyvis visualization
├── schema.sql           — database schema (tables, RLS grants, SQL functions)
├── requirements.txt
└── extension/            — Chrome/Edge browser extension
    ├── manifest.json
    ├── popup.html
    ├── popup.js
    └── content.js
```

## How data is saved

Each extraction (entry + its nodes/edges/gaps) is saved as a single atomic transaction via a Postgres function (`save_extraction_result` in `schema.sql`) — if any part fails, the whole entry is rolled back rather than leaving partial data. Semantic matching against existing nodes (embedding similarity → LLM comparison) runs as a separate step after the transaction succeeds.

## Setup

1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the project root with:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_service_role_key
   ```
3. Set up the database in your Supabase project by running `schema.sql` in the Supabase SQL Editor (creates tables, grants, and the pgvector matching/transaction functions).
4. Run the web app:
   ```bash
   streamlit run app.py
   ```

### Running the API + browser extension (optional)

The browser extension talks to a local FastAPI server, so this needs to be running separately from the Streamlit app.

1. Start the API server:
   ```bash
   uvicorn api:app --reload
   ```
   By default it runs at `http://127.0.0.1:8000`.
2. Load the extension in Chrome/Edge:
   - Go to `chrome://extensions` (or `edge://extensions`)
   - Enable **Developer mode**
   - Click **Load unpacked** and select the `extension/` folder
3. Select any text on a webpage, click the extension icon, and click **Extract**. The selected text is auto-filled into the popup; extraction results are saved through the same backend logic as the web app.

> Note: the extension currently points to `127.0.0.1:8000`, so the API server must be running locally for it to work.

## Demo mode

The hosted Streamlit demo runs with `DEMO_MODE=true`, which keeps all extracted data in server session memory only (nothing is written to the database, and it's cleared on refresh) — so visitors can try it without affecting real data.

## Status

Work in progress — personal project and portfolio piece.

Core pipeline (extraction → embedding → atomic transaction save → semantic matching → graph rendering) is built and has been tested across varied inputs (long-form transcripts, forum posts, multilingual text). The FastAPI backend and browser extension are functional locally; deployment for public use is the next step.