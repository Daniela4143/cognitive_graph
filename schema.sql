-- Cognitive Graph System — database schema
-- Run this in the Supabase SQL Editor to recreate the tables.

CREATE TABLE nodes (
    id SERIAL PRIMARY KEY,
    label TEXT NOT NULL,
    domain TEXT,
    status TEXT,
    activation_count INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT now(),
    last_activated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE entries (
    id SERIAL PRIMARY KEY,
    raw_text TEXT NOT NULL,
    forward_question TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE edges (
    id SERIAL PRIMARY KEY,
    source_node_id INTEGER REFERENCES nodes(id),
    target_node_id INTEGER REFERENCES nodes(id),
    weight REAL,
    reason TEXT,
    similarity REAL,
    status TEXT DEFAULT 'forming',
    activation_count INTEGER DEFAULT 1,
    origin TEXT DEFAULT 'ai_extracted',
    created_at TIMESTAMPTZ DEFAULT now(),
    last_activated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE gaps (
    id SERIAL PRIMARY KEY,
    node_id INTEGER REFERENCES nodes(id),
    entry_id INTEGER REFERENCES entries(id),
    unfinished TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- RLS is enabled on these tables. The app connects using the service_role
-- key, which bypasses RLS policies entirely — but table-level privileges
-- still need to be granted explicitly, or every query fails with
-- "permission denied for table ...".
GRANT SELECT, INSERT, UPDATE, DELETE ON public.entries, public.nodes, public.edges, public.gaps TO service_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO service_role;