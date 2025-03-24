"""Hierarchical Clustering Module."""

import numpy as np
import networkx as nx


def hierarchical_clustering(components, feature_vectors):
    """
    Implements the mathematical hierarchical clustering algorithm.

    Parameters
    ----------
    components : list of dict
        A list of dictionaries representing the components, each containing:
            - 'id': int, the component id
            - 'bounding_box': (x_min, y_min, x_max, y_max), the bounding box
            - additional component information
    feature_vectors : list of dict
        A list of dictionaries representing the feature vectors, each containing:
            - 'id': int, the component id
            - additional feature information

    Returns
    -------
    tree : dict
        A tree structure representing the containment relationships
    G : networkx.DiGraph
        The directed graph of containment relationships
    T : networkx.DiGraph
        The transitive reduction of G, representing the direct containment relationships
    """
    n = len(components)

    # Calculate containment matrix
    containment_matrix = np.zeros((n, n), dtype=bool)
    containment_scores = np.zeros((n, n))

    for i in range(n):
        bb_i = components[i]["bounding_box"]
        x_min_i, y_min_i, x_max_i, y_max_i = bb_i
        area_i = (x_max_i - x_min_i + 1) * (y_max_i - y_min_i + 1)

        for j in range(n):
            if i == j:
                continue

            bb_j = components[j]["bounding_box"]
            x_min_j, y_min_j, x_max_j, y_max_j = bb_j

            # Check if bb_i contains bb_j
            if (
                x_min_i < x_min_j
                and y_min_i < y_min_j
                and x_max_i > x_max_j
                and y_max_i > y_max_j
            ):
                containment_matrix[i, j] = True

                # Calculate containment score based on area ratio
                area_j = (x_max_j - x_min_j + 1) * (y_max_j - y_min_j + 1)
                containment_scores[i, j] = area_j / area_i

    # Create a directed graph from the containment matrix
    G = nx.DiGraph()

    # Add nodes
    for i in range(n):
        G.add_node(i, component=components[i], features=feature_vectors[i])

    # Add edges for containment relationships
    for i in range(n):
        for j in range(n):
            if containment_matrix[i, j]:
                G.add_edge(i, j, score=containment_scores[i, j])

    # Perform transitive reduction to get the direct containment relationships
    T = nx.transitive_reduction(G)

    # Convert to a tree structure
    tree = {}
    root_nodes = [n for n in T.nodes() if T.in_degree(n) == 0]

    def build_tree(node):
        children = list(T.successors(node))
        return {
            "id": node,
            "component": components[node],
            "children": [build_tree(child) for child in children],
        }

    # Build tree from each root node
    forest = [build_tree(root) for root in root_nodes]

    # If we have multiple trees, create a virtual root
    if len(forest) > 1:
        tree = {"id": "root", "component": None, "children": forest}
    else:
        tree = forest[0]

    return tree, G, T
