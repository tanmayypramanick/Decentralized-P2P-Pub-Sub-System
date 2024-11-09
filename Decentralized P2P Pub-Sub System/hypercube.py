import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_neighbors(node_id):
    """Calculate and log the neighbors of a given node in a hypercube topology."""
    neighbors = []
    node_binary = int(node_id, 2)
    for i in range(len(node_id)):
        # Flip each bit to find neighbors
        neighbor = node_binary ^ (1 << i)
        neighbor_id = format(neighbor, '03b')
        neighbors.append(neighbor_id)
    logging.info(f"[Hypercube] Neighbors of node '{node_id}': {neighbors}")
    return neighbors

def route_to_target(current_node, target_node):
    """Determine the routing path from current_node to target_node in a hypercube."""
    path = []
    current = int(current_node, 2)
    target = int(target_node, 2)
    while current != target:
        diff = current ^ target
        next_step = current ^ (1 << (diff.bit_length() - 1))
        path.append(format(next_step, '03b'))
        current = next_step
    logging.info(f"[Hypercube] Routing path from '{current_node}' to '{target_node}': {path}")
    return path
