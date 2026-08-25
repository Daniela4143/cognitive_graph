import sqlite3
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def save_entry(raw_text, forward_question=None):
    """Save a new entry to the entries table. Returns the new entry's id."""
    response = (
        supabase.table("entries")
        .insert({"raw_text": raw_text, "forward_question": forward_question})
        .execute()
    )
    return response.data[0]["id"]

def save_node(label, status, domain=None, embedding=None):
    """Save a new node to the nodes table. Returns the new node's id."""
    response = (
        supabase.table("nodes")
        .insert({"label": label, "status": status, "domain": domain, "embedding": embedding})
        .execute()
    )
    return response.data[0]["id"]

def save_edge(source_id, target_id, weight, reason):
    """Save a new edge to the edges table."""
    supabase.table("edges").insert({
        "source_node_id": source_id, 
        "target_node_id": target_id, 
        "weight": weight, 
        "reason": reason
    }).execute()
    

def save_gap(node_id, entry_id, unfinished):
    """Save a new gap to the gaps table."""
    supabase.table("gaps").insert({
        "node_id": node_id, 
        "entry_id": entry_id, 
        "unfinished": unfinished
    }).execute()
    
def get_all_nodes():
    """Retrieve all nodes from the nodes table."""
    response = supabase.table("nodes").select("*").execute()
    return response.data

def get_all_edges():
    """Retrieve all edges from the edges table."""
    response = supabase.table("edges").select("*").execute()
    return response.data

def match_similar_nodes(embedding, match_count=5):
    """Call the match_nodes SQL function to find the most semantically
    similar existing nodes to the given embedding (pgvector cosine similarity)."""
    response = supabase.rpc("match_nodes", {
        "query_embedding": embedding,
        "match_count": match_count
    }).execute()
    return response.data

def get_recent_nodes():
    """Retrieve recent 20 active nodes to compare with the new extracted nodes."""
    response = (supabase.table("nodes")
                .select("*")
                .order("last_activated_at", desc=True)
                .limit(20)
                .execute()
                )
    return response.data

if __name__ == "__main__":
    from extract import get_embedding
    real_embedding = get_embedding("拖延與逃避行為")
    results = match_similar_nodes(real_embedding, match_count=3)
    print("Most similar nodes:", results)
