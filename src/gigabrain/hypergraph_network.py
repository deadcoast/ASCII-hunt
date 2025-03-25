import numpy as np
import tensorflow as tf
import torch
from scipy import optimize
from sklearn.manifold import TSNE
import networkx as nx
import sympy as sp
import jax
import jax.numpy as jnp
from typing import Dict, List, Tuple, Set, Any, Optional, Union, Callable
import math
from collections import defaultdict
import re
import ast
import os
import sys
import time
import random
import hashlib
from dataclasses import dataclass, field
from functools import partial, lru_cache
import multiprocessing
from concurrent.futures import ThreadPoolExecutor


class HypergraphImportNetwork:
    """Represents imports as a hypergraph for advanced structural analysis."""

    def __init__(self):
        self.nodes = {}  # id -> node attributes
        self.hyperedges = {}  # id -> hyperedge attributes
        self.node_to_hyperedges = defaultdict(set)  # node id -> set of hyperedge ids

    def add_node(self, node_id, attributes=None):
        """Add a node to the hypergraph."""
        self.nodes[node_id] = attributes or {}

    def add_hyperedge(self, edge_id, node_ids, attributes=None):
        """Add a hyperedge connecting multiple nodes."""
        self.hyperedges[edge_id] = {
            "nodes": set(node_ids),
            "attributes": attributes or {},
        }

        for node_id in node_ids:
            self.node_to_hyperedges[node_id].add(edge_id)

    def get_node_hyperedges(self, node_id):
        """Get all hyperedges containing a node."""
        return self.node_to_hyperedges.get(node_id, set())

    def get_connected_nodes(self, node_id):
        """Get all nodes connected to the given node via any hyperedge."""
        connected = set()

        for edge_id in self.node_to_hyperedges.get(node_id, set()):
            connected.update(self.hyperedges[edge_id]["nodes"])

        # Remove the original node
        if node_id in connected:
            connected.remove(node_id)

        return connected

    def compute_s_centrality(self, node_id):
        """Compute s-centrality (hypergraph generalization of betweenness)."""
        # Count how many hyperedges this node participates in
        direct_edges = len(self.node_to_hyperedges.get(node_id, set()))

        # Compute the node's role in connecting different parts of the hypergraph
        all_nodes = set(self.nodes.keys())
        reachable_nodes = {node_id}

        # Find all nodes reachable from this node
        frontier = {node_id}
        visited_edges = set()

        while frontier:
            new_frontier = set()

            for current in frontier:
                for edge_id in self.node_to_hyperedges.get(current, set()):
                    if edge_id not in visited_edges:
                        visited_edges.add(edge_id)
                        new_frontier.update(self.hyperedges[edge_id]["nodes"])

            reachable_nodes.update(new_frontier)
            frontier = new_frontier - reachable_nodes

        # Calculate centrality based on reachability and edge participation
        reach_ratio = len(reachable_nodes) / max(1, len(all_nodes))

        # s-centrality combines direct connections and overall reach
        return 0.7 * direct_edges + 0.3 * reach_ratio

    def compute_eigen_centrality(self, max_iter=100, tol=1e-6):
        """Compute eigenvector centrality adapted for hypergraphs."""
        n_nodes = len(self.nodes)

        if n_nodes == 0:
            return {}

        # Initialize centrality vector
        centrality = {node_id: 1.0 for node_id in self.nodes}

        # Power iteration to find the dominant eigenvector
        for _ in range(max_iter):
            next_centrality = {node_id: 0.0 for node_id in self.nodes}

            # For each hyperedge, distribute centrality among connected nodes
            for edge_id, edge_data in self.hyperedges.items():
                edge_nodes = edge_data["nodes"]

                if not edge_nodes:
                    continue

                # Sum the centrality of nodes in this hyperedge
                edge_centrality = sum(
                    centrality[n] for n in edge_nodes if n in centrality
                )

                # Distribute back to nodes
                for node_id in edge_nodes:
                    if node_id in next_centrality:
                        next_centrality[node_id] += edge_centrality / len(edge_nodes)

            # Normalize
            norm = math.sqrt(sum(c * c for c in next_centrality.values()))

            if norm > 0:
                for node_id in next_centrality:
                    next_centrality[node_id] /= norm

            # Check convergence
            err = sum(abs(next_centrality[n] - centrality[n]) for n in centrality)

            if err < tol:
                return next_centrality

            centrality = next_centrality

        return centrality

    def extract_module_communities(self, resolution=1.0):
        """Extract module communities using hypergraph structure."""
        # Create a weighted projection graph for community detection
        import networkx as nx

        G = nx.Graph()

        # Add all nodes
        for node_id in self.nodes:
            G.add_node(node_id, **self.nodes[node_id])

        # Add weighted edges based on hyperedge co-occurrence
        edge_weights = defaultdict(float)

        for edge_id, edge_data in self.hyperedges.items():
            edge_nodes = list(edge_data["nodes"])

            for i, node1 in enumerate(edge_nodes):
                for node2 in edge_nodes[i + 1 :]:
                    key = tuple(sorted([node1, node2]))

                    # Weight is inversely proportional to hyperedge size
                    # (smaller hyperedges create stronger connections)
                    weight = 1.0 / max(1, len(edge_nodes) - 1)
                    edge_weights[key] += weight

        # Add the weighted edges to the graph
        for (node1, node2), weight in edge_weights.items():
            G.add_edge(node1, node2, weight=weight)

        # Detect communities using Louvain algorithm
        from community import community_louvain

        partition = community_louvain.best_partition(G, resolution=resolution)

        # Group nodes by community
        communities = defaultdict(list)
        for node_id, community_id in partition.items():
            communities[community_id].append(node_id)

        return communities
