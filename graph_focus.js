network.on("click", function (params) {
    if (params.nodes.length > 0) {
    // clicked on a node, focus on it and its connected nodes
        var selectedId = params.nodes[0];
        var connectedIds = network.getConnectedNodes(selectedId);
        var focusSet = new Set(connectedIds);
        focusSet.add(selectedId); // include the clicked node itself

        var nodeUpdates = nodes.get().map(function (node) {
            if (focusSet.has(node.id)) {    // enlarge focused nodes
                return {id: node.id, color: node.original_color, size: node.original_size * 1.5, label: node.full_label}; 
            } else {    // dim non-focused nodes
                return {id: node.id, color: "rgba(200, 200, 200, 0.3)", size: node.original_size * 0.5}; 
            }
        });
        nodes.update(nodeUpdates);

        network.focus(selectedId, {
            scale: 1.2,
            animation: {
                duration: 500,
                easingFunction: "easeInOutQuad" 
            }
        });

        var edgeUpdates = edges.get().map(function (edge) {
            if (focusSet.has(edge.from) && focusSet.has(edge.to)) {    // highlight focused edges
                return {id: edge.id, color: edge.original_color, dashes: edge.dashes}; 
            } else {    // dim non-focused edges
                return {id: edge.id, color: "rgba(200, 200, 200, 0.15)", dashes: edge.dashes}; 
            }
        });
        edges.update(edgeUpdates);
    } else {    
    // clicked on empty space, reset all nodes and edges to original state
        var nodeReset = nodes.get().map(function (node) {
            return {id: node.id, color: node.original_color, size: node.original_size, label: node.original_label}; 
        });
        nodes.update(nodeReset);

        var edgeReset = edges.get().map(function (edge) {
            return {id: edge.id, color: edge.original_color, dashes: edge.dashes}; 
        });
        edges.update(edgeReset);
    }
});