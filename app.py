import streamlit as st
import os
from extract import extract_cognitive_graph
from graph import build_graph, render_graph
from services import process_extraction

"""
RUN CMD: streamlit run app.py
"""

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
    return process_extraction(user_input, result)

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
