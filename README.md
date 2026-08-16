# Cognitive Graph System

A personal cognitive-reflection tool that turns free-form journal/conversation text into a structured graph of recurring thought patterns.

## What it does

You write down whatever's on your mind. An LLM (Gemini) extracts:
- **Nodes** — recurring cognitive patterns or concepts, each tagged as `active` (current focus), `pending` (noted but not explored yet), or `recurring` (echoes a known pattern)
- **Edges** — relationships between nodes, with a strength/weight and a reason
- **Gaps** — threads you started but didn't finish saying
- **A forward question** — one question worth exploring next

The result is saved to a database and rendered as an interactive graph, so patterns across multiple entries become visible over time instead of staying scattered across separate journal entries.

## Tech stack

- **Frontend/App**: Streamlit
- **LLM**: Google Gemini API
- **Database**: Supabase (Postgres)
- **Graph**: networkx + pyvis

## Project structure

```
extract.py    — extraction prompt + LLM calls (extraction, node comparison)
database.py   — Supabase read/write functions
graph.py      — builds and renders the graph visualization
app.py        — Streamlit UI and app flow
```

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
3. Set up the database tables in your Supabase project (see `schema.sql` — or run the table-creation SQL in the Supabase SQL Editor).
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Status

Work in progress — personal project and portfolio piece.