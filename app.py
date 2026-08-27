import streamlit as st
import os
from extract import extract_cognitive_graph, get_embedding, compare_cognitive_nodes
from database import save_extraction_transaction, match_similar_nodes, save_semantic_edge
from graph import build_graph, render_graph

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

def save_extraction_result(user_input, result):
    if DEMO_MODE:
        # data only stored in server memory for demo purposes, close the browser or refresh the page will lose the data
        st.session_state.setdefault("demo_nodes", [])
        st.session_state.setdefault("demo_edges", [])
        st.session_state.setdefault("demo_next_id", 1)

        node_id_map = {}
        for node in result.get("nodes", []):
            local_id = st.session_state.demo_next_id
            st.session_state.demo_next_id += 1
            st.session_state.demo_nodes.append({
                "id": local_id,
                "label": node["label"],
                "domain": None,
                "status": node["status"],
                "activation_count": 1,
            })
            node_id_map[node["id"]] = local_id

        for edge in result.get("edges", []):
            source_id = node_id_map.get(edge["from"])
            target_id = node_id_map.get(edge["to"])
            if source_id and target_id:
                st.session_state.demo_edges.append({
                    "source_node_id": source_id,
                    "target_node_id": target_id,
                    "weight": edge["weight"],
                    "reason": edge["reason"],
                    "origin": "ai_extracted",
                    "status": "forming",
                })
        return node_id_map

    # Step 1: Calculate all new node embeddings, make up a payload for the transaction
    nodes_payload = []
    embeddings_by_temp_id = {}

    # test error handling: transaction should fail if any node has an invalid embedding
    # nodes_payload.append({
    #     "temp_id": "FAKE_BROKEN",
    #     "label": "測試用故意壞掉的節點",
    #     "status": "active",
    #     "embedding": "not_a_valid_vector"   # 故意塞一個不合法的向量格式
    # })
    
    for node in result.get("nodes", []):
        embedding = get_embedding(node["label"])
        embeddings_by_temp_id[node["id"]] = embedding
        nodes_payload.append({
            "temp_id": node["id"],
            "label": node["label"],
            "status": node["status"],
            "embedding": embedding
        })

    edges_payload = [
        {
            "from": e["from"],
            "to": e["to"],
            "weight": e["weight"], 
            "reason": e["reason"]
        } 
        for e in result.get("edges", [])
    ]

    gaps_payload = [
        {
            "node": g["node"],
            "unfinished": g["unfinished"]
        }
        for g in result.get("gaps", [])
    ]

    # Step 2: save the entry + nodes + edges + gaps as a single atomic transaction
    tx_result = save_extraction_transaction(
        user_input,
        result.get("forward_question"),
        nodes_payload,
        edges_payload,
        gaps_payload
    )

    node_id_map = tx_result.get("node_id_map", {})
    new_node_ids = set(node_id_map.values())

    # Step 3: do semantic matching(two-step filtering) after transaction
    for node in result.get("nodes", []):
        my_db_id = node_id_map.get(node["id"])
        embedding = embeddings_by_temp_id.get(node["id"])   # save the time to call embedding API again
        candidates = match_similar_nodes(embedding, match_count=2)

        for candidate in candidates:
            if candidate["id"] in new_node_ids or candidate["similarity"] < 0.8:
                continue
            comparison = compare_cognitive_nodes(node["label"], candidate["label"])
            if comparison.get("similar"):
                save_semantic_edge(
                    source_id=my_db_id,
                    target_id=candidate["id"],
                    similarity=comparison.get("similarity", 0),
                    reason=comparison.get("reason", "Semantic similarity detected")
                )

    return node_id_map

def display_graph():
    # Build the cognitive graph
    st.subheader("Cognitive Graph Visualization")

    if DEMO_MODE:
        cognitive_graph = build_graph(st.session_state.get("demo_nodes", []), st.session_state.get("demo_edges", []))
    else:
        cognitive_graph = build_graph()

    graph_html_path = render_graph(cognitive_graph)

    with open(graph_html_path, 'r', encoding='utf-8') as f:
        graph_html = f.read()

    # display the graph using components.html
    st.iframe(graph_html, height=600)

st.title("Cognitive Graph System")
# markdown for instructions
st.markdown("Enter your conversation text below and click 'Extract and Update Cognitive Graph', our system will extract cognitive nodes and connections automatically and save them to the database.")

if DEMO_MODE:
    st.info("This is for demo purposes only. Your input will only show during this session and will not be saved to the database.")

# set height to 200 for better user experience
user_input = st.text_area("What's on your mind?", height=200)

# click button first then deal with the logic of action
if st.button("Extract and Update Cognitive Graph"):
    # add strip() to avoid blank input
    if user_input.strip() == "":
        st.warning("Please enter some text first.")
    else:
        # add a spinner to indicate processing
        try:
            with st.spinner("Extracting cognitive graph..."):
                result = extract_cognitive_graph(user_input)
        except Exception as e:
            st.error(f"Error during extraction: {str(e)}")
            st.stop()

        node_id_map = save_extraction_result(user_input, result)
        
        st.success("Cognitive graph extracted and updated.")

        display_graph()

        # add a subheader to display the result in a structured format
        st.subheader("Extraction Result")
        st.json(result)

        # display the forward question if it exists
        if result.get("forward_question"):
            st.subheader(" Question worth exploring")
            # use st.info to display the forward question in a highlighted box
            st.info(result.get("forward_question"))
