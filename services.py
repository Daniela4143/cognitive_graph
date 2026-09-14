from extract import get_embedding, compare_cognitive_nodes
from database import match_similar_nodes, save_extraction_transaction, save_semantic_edge

def process_extraction(user_input, result):
    """
    save the extraction result into database, and do semantic matching after transaction
    Used in api.py, app.py
    """

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