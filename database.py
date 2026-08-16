import sqlite3
import os

DB_PATH = "cognitive_graph.db"

def init_db():
    """Initialize the SQLite database and create the necessary tables."""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create tables
        cursor.executescript(
        '''
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                domain TEXT,
                status TEXT,
                activation_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
                             
            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_node_id INTEGER,
                target_node_id INTEGER,
                weight REAL,
                reason TEXT,
                similarity REAL,   
                status TEXT DEFAULT 'forming',
                activation_count INTEGER DEFAULT 1,
                origin TEXT DEFAULT 'ai_extracted',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_node_id) REFERENCES nodes(id),
                FOREIGN KEY (target_node_id) REFERENCES nodes(id)
            );  
                             
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_text TEXT NOT NULL,
                forward_question TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );     

            CREATE TABLE IF NOT EXISTS gaps (    
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id INTEGER,
                entry_id INTEGER,
                unfinished TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (node_id) REFERENCES nodes(id),
                FOREIGN KEY (entry_id) REFERENCES entries(id)
            );      

        '''
        )
        
        conn.commit()
        conn.close()

def save_entry(raw_text, forward_question=None):
    """Save a new entry to the entries table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO entries (raw_text, forward_question) VALUES (?, ?)", 
        (raw_text, forward_question)
    )
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entry_id

def save_node(label, status, domain=None):
    """Save a new node to the nodes table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO nodes (label, status, domain) VALUES (?, ?, ?)", 
        (label, status, domain)
    )
    node_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return node_id

def save_edge(source_id, target_id, weight, reason):
    """Save a new edge to the edges table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO edges (source_node_id, target_node_id, weight, reason) VALUES (?, ?, ?, ?)", 
        (source_id, target_id, weight, reason)
    )
    conn.commit()
    conn.close()

def save_gap(node_id, entry_id, unfinished):
    """Save a new gap to the gaps table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO gaps (node_id, entry_id, unfinished) VALUES (?, ?, ?)", 
        (node_id, entry_id, unfinished)
    )
    conn.commit()
    conn.close()

def get_all_nodes():
    """Retrieve all nodes from the nodes table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nodes")
    column_names = [description[0] for description in cursor.description]
    # fetch all rows and convert to list of dictionaries
    rows = cursor.fetchall()
    # map each row to a dictionary using column names
    nodes = [dict(zip(column_names, row)) for row in rows]
    conn.close()
    return nodes

def get_all_edges():
    """Retrieve all edges from the edges table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM edges")
    column_names = [description[0] for description in cursor.description]
    # fetch all rows and convert to list of dictionaries
    rows = cursor.fetchall()
    # map each row to a dictionary using column names
    edges = [dict(zip(column_names, row)) for row in rows]
    conn.close()
    return edges

def get_recent_nodes():
    """Retrieve recent 20 active nodes to compare with the new extracted nodes."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nodes ORDER BY last_activated_at DESC LIMIT 20")
    column_names = [description[0] for description in cursor.description]
    # fetch all rows and convert to list of dictionaries
    rows = cursor.fetchall()
    # map each row to a dictionary using column names
    nodes = [dict(zip(column_names, row)) for row in rows]
    conn.close()
    return nodes

def migrate_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE edges ADD COLUMN similarity REAL")
        print("Added 'similarity' column to edges table.")
    except sqlite3.OperationalError as e:
        print("similarity column already exists, skipping migration.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    # init_db()
    # print("Database initialized and tables created.")
    migrate_db()

