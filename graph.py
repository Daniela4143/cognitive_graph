import networkx as nx
from database import get_all_nodes, get_all_edges
from pyvis.network import Network

def get_node_style(node):
    """Return size and color based on node status and activation count."""
    size = 10 + (node["activation_count"] * 5)

    if node["status"] == "active":
        color = "green"
    elif node["status"] == "recurring":
        color = "blue"
    else:
        color = "gray"

    return size, color

def get_edge_style(edge):
    """Return color and dashes based on edge origin and status."""
    if edge["origin"] == "ai_extracted":
        color = "orange"
    else:
        color = "gray"

    dashes = edge["status"] == "forming"

    return color, dashes

def build_graph(nodes=None, edges=None):
    """Build the cognitive graph. If nodes/edges are provided (e.g. demo-mode
    session data), use those directly instead of querying the database."""
    cognitive_graph = nx.DiGraph()

    if nodes is None:
        nodes = get_all_nodes()
    if edges is None:
        edges = get_all_edges()

    for node in nodes:
        size, color = get_node_style(node)
        # to avoid cluttering the graph, we can shorten the label if it's too long
        full_label = node["label"]
        short_label = full_label[:8] + "..." if len(full_label) > 8 else full_label

        cognitive_graph.add_node(
            node["id"], 
            label=short_label,  # show short label on the node
            title=full_label,   # show full label when mouse hovers over the node
            status=node["status"], 
            size=size, 
            color=color
        )

    for edge in edges:
        color, dashes = get_edge_style(edge)
        cognitive_graph.add_edge(edge["source_node_id"], edge["target_node_id"], weight=edge["weight"], reason=edge["reason"], color=color, dashes=dashes)

    return cognitive_graph

def render_graph(graph):
    """Render the graph to an interactive HTML using PyVis."""
    net = Network(
        height="800px",
        width="100%",
        directed=True,
        notebook=False, # set to False for Streamlit, true for Jupyter Notebook
        bgcolor="black",
        font_color="white"
    )

    net.from_nx(graph)
    net.repulsion(node_distance=150,    # avoid node overlap
                  spring_length=150)    # avoid edge overlap
    net.save_graph("cognitive_graph.html")

    return "cognitive_graph.html"