-- pgvector extension, required for the nodes.embedding column below.
-- Must be enabled before the nodes table is created (or before this column is added).
CREATE EXTENSION IF NOT EXISTS vector;

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
    embedding vector(768)  -- gemini-embedding-001, 768 dims, for semantic pre-filtering
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

-- Semantic pre-filtering: given a node's embedding, return the top N
-- most similar existing nodes (by cosine similarity) for LLM comparison.
-- Added 2026-08-25.
CREATE OR REPLACE FUNCTION match_nodes(
    query_embedding vector(768),
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id int,
    label text,
    status text,
    similarity float
)
LANGUAGE sql
AS $$
    SELECT
        id,
        label,
        status,
        1 - (embedding <=> query_embedding) AS similarity
    FROM nodes
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;

-- Atomic transaction helpers: save an entry + its nodes/edges/gaps in a
-- single Postgres function call, so a failure partway through rolls back
-- everything instead of leaving partial data. Added 2026-08-27.

CREATE OR REPLACE FUNCTION insert_node(p_label text, p_status text, p_embedding vector)
RETURNS int
LANGUAGE plpgsql
AS $$
DECLARE
    v_id int;
BEGIN
    INSERT INTO nodes (label, status, embedding)
    VALUES (p_label, p_status, p_embedding)
    RETURNING id INTO v_id;
    RETURN v_id;
END;
$$;

CREATE OR REPLACE FUNCTION insert_edge(p_source_id int, p_target_id int, p_weight real, p_reason text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO edges (source_node_id, target_node_id, weight, reason)
    VALUES (p_source_id, p_target_id, p_weight, p_reason);
END;
$$;

CREATE OR REPLACE FUNCTION insert_gap(p_node_id int, p_entry_id int, p_unfinished text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO gaps (node_id, entry_id, unfinished)
    VALUES (p_node_id, p_entry_id, p_unfinished);
END;
$$;

CREATE OR REPLACE FUNCTION save_extraction_result(
    p_raw_text text,
    p_forward_question text,
    p_nodes jsonb,
    p_edges jsonb,
    p_gaps jsonb
)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
    v_entry_id int;
    v_node jsonb;
    v_edge jsonb;
    v_gap jsonb;
    v_new_id int;
    v_id_map jsonb := '{}'::jsonb;
BEGIN
    INSERT INTO entries (raw_text, forward_question)
    VALUES (p_raw_text, p_forward_question)
    RETURNING id INTO v_entry_id;

    FOR v_node IN SELECT * FROM jsonb_array_elements(p_nodes)
    LOOP
        v_new_id := insert_node(
            v_node->>'label',
            v_node->>'status',
            (v_node->>'embedding')::vector
        );
        v_id_map := v_id_map || jsonb_build_object(v_node->>'temp_id', v_new_id);
    END LOOP;

    FOR v_edge IN SELECT * FROM jsonb_array_elements(p_edges)
    LOOP
        PERFORM insert_edge(
            (v_id_map->>(v_edge->>'from'))::int,
            (v_id_map->>(v_edge->>'to'))::int,
            (v_edge->>'weight')::real,
            v_edge->>'reason'
        );
    END LOOP;

    FOR v_gap IN SELECT * FROM jsonb_array_elements(p_gaps)
    LOOP
        PERFORM insert_gap(
            (v_id_map->>(v_gap->>'node'))::int,
            v_entry_id,
            v_gap->>'unfinished'
        );
    END LOOP;

    RETURN jsonb_build_object('entry_id', v_entry_id, 'node_id_map', v_id_map);
END;
$$;