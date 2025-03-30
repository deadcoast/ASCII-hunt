"""Quantum-Inspired Topological Import Analyzer."""

import logging
from collections import defaultdict
from typing import Any, cast

import gudhi as gd
import networkx as nx
import numpy as np
from gudhi.representations import Landscape
from sklearn.manifold import TSNE

# Setup logger
logger = logging.getLogger(__name__)

# Gudhi SimplexTree type is not directly importable/stubs incomplete
# Use Any and ignore specific attribute errors later
SimplexTreeType = Any

# Type alias for persistence results
PersistenceResult = list[tuple[int, tuple[float, float]]]


class QuantumStateVector:
    """Quantum state vector."""

    # Tolerances for floating point comparisons
    PROB_SUM_TOLERANCE = 1e-6
    ZERO_TOLERANCE = 1e-9

    def __init__(self, dimension: int) -> None:
        """Initialize a quantum state vector."""
        self.dimension = dimension
        self.amplitudes = np.zeros(dimension, dtype=complex)
        # Initialize RNG for measurement
        self.rng = np.random.default_rng()
        self.normalize()

    def set_basis_state(self, index: int) -> None:
        """Set the state to a specific basis state."""
        if not 0 <= index < self.dimension:
            msg = "Index out of bounds"
            raise IndexError(msg)
        self.amplitudes = np.zeros(self.dimension, dtype=complex)
        self.amplitudes[index] = 1.0

    def superposition(
        self, indices: list[int], weights: list[float] | None = None
    ) -> None:
        """Create a superposition of basis states."""
        self.amplitudes = np.zeros(self.dimension, dtype=complex)
        num_indices = len(indices)
        if num_indices == 0:
            self.normalize()  # Ensure zero vector is handled if needed
            return

        if weights is None:
            weight_val = 1.0 / np.sqrt(num_indices)
            for idx in indices:
                if 0 <= idx < self.dimension:
                    self.amplitudes[idx] = weight_val
        else:
            if len(weights) != num_indices:
                msg = "Number of weights must match number of indices"
                raise ValueError(msg)
            for idx, weight in zip(indices, weights, strict=True):
                if 0 <= idx < self.dimension:
                    self.amplitudes[idx] = complex(weight)  # Ensure complex type

        self.normalize()

    def apply_gate(self, matrix: np.ndarray) -> None:
        """Apply a quantum gate (unitary matrix)."""
        if matrix.shape != (self.dimension, self.dimension):
            msg = "Matrix dimensions must match state vector dimension"
            raise ValueError(msg)
        self.amplitudes = np.dot(matrix, self.amplitudes)
        self.normalize()

    def measure(self) -> int:
        """Perform a measurement, collapsing the state."""
        probabilities = np.abs(self.amplitudes) ** 2
        # Ensure probabilities sum to 1 for choice
        prob_sum = np.sum(probabilities)
        if abs(prob_sum - 1.0) > self.PROB_SUM_TOLERANCE:
            if prob_sum <= self.ZERO_TOLERANCE:
                logger.warning("Attempting to measure near-zero state vector.")
                # Return a default or raise error? For now, return random index.
                return self.rng.choice(self.dimension)

            # Explicitly cast to float before division to avoid type error
            probabilities = probabilities.astype(np.float64)
            probabilities /= prob_sum
        # Use updated RNG
        outcome = self.rng.choice(self.dimension, p=probabilities)
        self.set_basis_state(outcome)
        return outcome

    def normalize(self) -> None:
        """Normalize the state vector."""
        norm = np.linalg.norm(self.amplitudes)
        if norm > self.ZERO_TOLERANCE:
            self.amplitudes /= norm
        else:
            self.amplitudes = np.zeros(self.dimension, dtype=complex)

    def get_probabilities(self) -> np.ndarray:
        """Get the probability distribution."""
        return np.abs(self.amplitudes) ** 2


class TopologicalFeatureExtractor:
    """Topological feature extractor."""

    def __init__(self, max_dimension: int = 2) -> None:
        """Initialize a topological feature extractor."""
        self.max_dimension = max_dimension

    def build_simplicial_complex(self, distance_matrix: np.ndarray) -> SimplexTreeType:
        """Build a Vietoris-Rips complex from a distance matrix."""
        # Use Any for SimplexTree type
        rips_complex = gd.RipsComplex(distance_matrix=distance_matrix)  # type: ignore[attr-defined]
        return rips_complex.create_simplex_tree(max_dimension=self.max_dimension)

    def compute_persistence(self, simplex_tree: SimplexTreeType) -> PersistenceResult:
        """Compute persistent homology."""
        # Use Any for SimplexTree type
        simplex_tree.compute_persistence()  # type: ignore[attr-defined]
        persistence_result = simplex_tree.persistence()  # type: ignore[attr-defined]
        # Cast result to the expected list format
        persistence_typed: PersistenceResult = cast(
            "PersistenceResult", persistence_result
        )
        return persistence_typed

    def compute_landscape(
        self,
        persistence: PersistenceResult,
        num_landscapes: int = 5,
        resolution: int = 100,
    ) -> np.ndarray:
        """Compute persistence landscapes."""
        # Ensure persistence is a list of diagrams for fit_transform
        persistence_diagrams = [(d, (b, t)) for d, (b, t) in persistence if t > b]
        if not persistence_diagrams:
            # Handle case with no significant persistence features
            # Return an empty array or array of zeros matching expected shape
            return np.zeros((num_landscapes, resolution))

        landscape_computer = Landscape(
            num_landscapes=num_landscapes, resolution=resolution
        )
        # fit_transform expects a list of persistence diagrams
        return landscape_computer.fit_transform([persistence_diagrams])

    def extract_features(self, distance_matrix: np.ndarray) -> dict[str, Any]:
        """Extract topological features from data."""
        simplex_tree = self.build_simplicial_complex(distance_matrix)
        persistence = self.compute_persistence(simplex_tree)
        landscape_features = self.compute_landscape(persistence)

        betti_numbers = simplex_tree.betti_numbers()  # type: ignore[attr-defined]

        return {
            "landscape": landscape_features,
            "betti_numbers": betti_numbers,
            "persistence": persistence,
        }


class QITIA:
    """Quantum-Inspired Topological Import Analyzer."""

    # Define tolerance constants
    ZERO_TOLERANCE = 1e-9
    PROB_SUM_TOLERANCE = 1e-6
    # Define t-SNE default component target
    DEFAULT_TSNE_COMPONENTS = 2
    # K-Means constants
    KMEANS_RANDOM_CHOICE_THRESHOLD = 0.8
    KMEANS_CONVERGENCE_TOLERANCE = 1e-4
    # Import generation constants
    IMPORT_CONFIDENCE_THRESHOLD = 0.15

    def __init__(self, dimension: int = 1024) -> None:
        """Initialize the QITIA system."""
        self.dimension = dimension
        self.symbol_states: dict[str, QuantumStateVector] = {}
        self.module_states: dict[str, QuantumStateVector] = {}
        self.quantum_embeddings: dict[str, np.ndarray] = {}
        self.topological_extractor = TopologicalFeatureExtractor()
        self.import_graph = nx.DiGraph()
        self.module_to_index: dict[str, int] = {}
        self.symbol_to_index: dict[str, int] = {}
        self.index_to_module: dict[int, str] = {}
        self.index_to_symbol: dict[int, str] = {}
        self.symbol_providers: dict[str, list[str]] = defaultdict(list)
        self.distance_cache: dict[tuple[str, str], float] = {}
        # Initialize RNG
        self.rng = np.random.default_rng()

    def initialize(self, modules: list[str], symbols: list[str]) -> None:
        """Initialize the system with modules and symbols."""
        self.module_to_index = {module: i for i, module in enumerate(modules)}
        next_index = len(modules)
        self.symbol_to_index = {
            symbol: next_index + i for i, symbol in enumerate(symbols)
        }
        self.index_to_module = {v: k for k, v in self.module_to_index.items()}
        self.index_to_symbol = {v: k for k, v in self.symbol_to_index.items()}

        for module in self.module_to_index:
            state = QuantumStateVector(self.dimension)
            pattern = np.zeros(self.dimension, dtype=complex)
            module_hash = hash(module)
            start_idx = (module_hash >> 8) % self.dimension
            indices = np.arange(start_idx, start_idx + 16)
            phases = np.linspace(0, 2 * np.pi, 16)
            pattern[indices % self.dimension] = np.exp(1j * phases)
            state.amplitudes = pattern
            state.normalize()
            self.module_states[module] = state

        for symbol in self.symbol_to_index:
            state = QuantumStateVector(self.dimension)
            # Use new RNG
            real_part = self.rng.normal(0, 1, self.dimension)
            imag_part = self.rng.normal(0, 1, self.dimension)
            state.amplitudes = real_part + 1j * imag_part
            state.normalize()
            self.symbol_states[symbol] = state

        self.import_graph.add_nodes_from(modules, type="module")
        self.import_graph.add_nodes_from(symbols, type="symbol")

    def add_provider_relationship(self, module: str, symbol: str) -> bool:
        """Add a relationship that a module provides a symbol."""
        if module not in self.module_states or symbol not in self.symbol_states:
            logger.warning(
                f"Module {module} or Symbol {symbol} not found for relationship."
            )
            return False

        self.import_graph.add_edge(module, symbol, type="provides")

        entangle_op = np.eye(self.dimension, dtype=complex)
        try:
            module_idx = self.module_to_index[module]
            symbol_idx = self.symbol_to_index[symbol]
        except KeyError as e:
            logger.exception(f"Index lookup failed for {e}. Relationship not added.")
            return False

        theta = np.pi / 4
        half_dim = self.dimension // 2
        num_entangle_indices = min(16, self.dimension // 64)

        for i in range(num_entangle_indices):
            mod_hash_part = module_idx * 8 + i
            sym_hash_part = symbol_idx * 8 + i

            src_idx = mod_hash_part % half_dim
            tgt_idx = (sym_hash_part % half_dim) + half_dim

            if 0 <= src_idx < self.dimension and 0 <= tgt_idx < self.dimension:
                cos_t, sin_t = np.cos(theta), np.sin(theta)
                entangle_op[src_idx, src_idx] = cos_t
                entangle_op[src_idx, tgt_idx] = -sin_t
                entangle_op[tgt_idx, src_idx] = sin_t
                entangle_op[tgt_idx, tgt_idx] = cos_t
            else:
                logger.warning(
                    f"Calculated indices ({src_idx}, {tgt_idx}) out of bounds."
                )

        self.module_states[module].apply_gate(entangle_op)
        self.symbol_states[symbol].apply_gate(entangle_op)
        if module not in self.symbol_providers[symbol]:
            self.symbol_providers[symbol].append(module)
        return True

    def compute_quantum_similarity(
        self, state1: QuantumStateVector, state2: QuantumStateVector
    ) -> float:
        """Compute quantum similarity (fidelity) between two states."""
        # Ensure amplitudes are normalized before computing dot product
        overlap = np.dot(np.conj(state1.amplitudes), state2.amplitudes)
        # Fidelity is squared absolute value of overlap
        similarity = np.abs(overlap) ** 2
        return max(0.0, min(1.0, similarity))  # Clamp between 0 and 1

    def find_best_import_for_symbol(
        self, symbol: str, context: list[str] | None = None
    ) -> tuple[str, float] | None:
        """Find the best module to import a symbol from."""
        symbol_state = self.symbol_states.get(symbol)
        if not symbol_state:
            logger.warning(f"Symbol '{symbol}' not found during import search.")
            return None

        current_symbol_state = QuantumStateVector(self.dimension)
        current_symbol_state.amplitudes = symbol_state.amplitudes.copy()

        if context:
            context_operator = self._create_context_operator(context)
            current_symbol_state.apply_gate(context_operator)

        similarities: dict[str, float] = {}
        for module, module_state in self.module_states.items():
            similarity = self.compute_quantum_similarity(
                current_symbol_state, module_state
            )
            similarities[module] = similarity

        if not similarities:
            return None

        # Consider potential ties or very low similarities?
        best_module, best_similarity = max(
            similarities.items(), key=lambda item: item[1]
        )
        return best_module, best_similarity

    def _create_context_operator(self, context: list[str]) -> np.ndarray:
        """Create a quantum operator based on code context."""
        operator = np.eye(self.dimension, dtype=complex)
        if not context:
            return operator  # Return identity if context is empty

        total_context_hash = hash(" ".join(context))

        for i, word in enumerate(context):
            word_hash = hash(word)
            # Combine word hash with total context hash and position
            combined_hash = total_context_hash ^ (word_hash << (i % 4))
            phase = (combined_hash % 6283) / 1000.0  # Approx 0 to 2pi
            start_idx = (combined_hash >> 8) % self.dimension
            num_indices_to_affect = min(8, self.dimension)

            for offset in range(num_indices_to_affect):
                idx = (start_idx + offset) % self.dimension
                # Apply phase rotation
                operator[idx, idx] *= np.exp(1j * phase)

        # Optional: Ensure the operator is unitary (or close enough)
        # This simple phase shift diagonal operator is inherently unitary.
        return operator

    def _compute_distance_matrix(self, nodes: list[str]) -> np.ndarray:
        """Compute the distance matrix based on quantum state similarity."""
        n = len(nodes)
        distance_matrix = np.full((n, n), 1.0)
        np.fill_diagonal(distance_matrix, 0.0)

        node_map = {node: i for i, node in enumerate(nodes)}

        for i in range(n):
            for j in range(i + 1, n):
                node1 = nodes[i]
                node2 = nodes[j]

                # Ensure consistent order for cache key
                key_node1, key_node2 = (
                    (node1, node2) if node1 <= node2 else (node2, node1)
                )
                cache_key: tuple[str, str] = (key_node1, key_node2)

                if cache_key in self.distance_cache:
                    dist = self.distance_cache[cache_key]
                else:
                    state1 = self._get_state_for_node(node1)
                    state2 = self._get_state_for_node(node2)
                    if state1 and state2:
                        similarity = self.compute_quantum_similarity(state1, state2)
                        # Use Bures distance approximation: sqrt(1 - sqrt(Fidelity))
                        # Or simpler 1 - sqrt(similarity) as before
                        dist = max(0.0, 1.0 - np.sqrt(similarity))
                        self.distance_cache[cache_key] = dist
                    else:
                        dist = 1.0  # Default if states are missing

                idx1 = node_map[node1]
                idx2 = node_map[node2]
                distance_matrix[idx1, idx2] = distance_matrix[idx2, idx1] = dist
        return distance_matrix

    def _get_state_for_node(self, node: str) -> QuantumStateVector | None:
        """Get the quantum state for a module or symbol node."""
        # Prefer module state if node exists as both (unlikely)
        return self.module_states.get(node) or self.symbol_states.get(node)

    def compute_import_topology(self) -> dict[str, Any]:
        """Compute topological features and embedding of the import graph."""
        nodes = list(self.import_graph.nodes())
        if not nodes:
            # Return empty structure if graph is empty
            return {
                "embedding": {},
                "landscape": np.array([]),
                "betti_numbers": [],
                "persistence": [],
            }

        distance_matrix = self._compute_distance_matrix(nodes)

        # Extract topological features (handle potential errors in gudhi)
        features: dict[str, Any] = {
            "embedding": {},
            "landscape": np.array([]),
            "betti_numbers": [],
            "persistence": [],
        }
        try:
            topo_features = self.topological_extractor.extract_features(distance_matrix)
            features |= topo_features
        except Exception as e:
            logger.error(f"Error extracting topological features: {e}", exc_info=True)
            # Features remain with default empty values

        # Compute quantum embedding using t-SNE
        embedding = None
        if len(nodes) > 1 and distance_matrix.shape == (len(nodes), len(nodes)):
            try:
                # Ensure perplexity is valid
                perplexity_val = max(1.0, min(30.0, float(len(nodes) - 1)))
                # t-SNE requires n_samples > n_components
                # Use defined constant for target components
                n_components = (
                    min(self.DEFAULT_TSNE_COMPONENTS, len(nodes) - 1)
                    if len(nodes) > self.DEFAULT_TSNE_COMPONENTS
                    else 1
                )

                if n_components > 0:
                    tsne = TSNE(
                        n_components=n_components,
                        perplexity=perplexity_val,
                        metric="precomputed",
                        init="random",
                        learning_rate="auto",
                        random_state=42,  # For reproducibility
                    )
                    embedding = tsne.fit_transform(distance_matrix)
                    self.quantum_embeddings = {
                        nodes[i]: embedding[i] for i in range(len(nodes))
                    }
                    features["embedding"] = (
                        self.quantum_embeddings
                    )  # Store dict in features
                else:
                    logger.info(
                        "Skipping t-SNE: Not enough samples for chosen components."
                    )

            except ValueError as e:
                logger.exception(f"t-SNE failed: {e}. Skipping embedding.")
                self.quantum_embeddings = {}
                features["embedding"] = {}
        else:
            self.quantum_embeddings = {}
            features["embedding"] = {}

        return features

    def _get_module_embeddings_for_clustering(
        self,
    ) -> tuple[list[str], np.ndarray] | None:
        """Prepare module nodes and their embeddings for clustering."""
        if not self.quantum_embeddings:
            self.compute_import_topology()
        if not self.quantum_embeddings:
            logger.warning("Cannot compute clusters: No embeddings available.")
            return None

        module_nodes = [
            node
            for node, data in self.import_graph.nodes(data=True)
            if data.get("type") == "module"
        ]
        if not module_nodes:
            logger.warning("No module nodes found in the graph for clustering.")
            return None

        nodes_with_embeddings = [
            n for n in module_nodes if n in self.quantum_embeddings
        ]
        if not nodes_with_embeddings:
            logger.warning("No embeddings found for any module nodes.")
            return None

        embedding_list = [
            self.quantum_embeddings[node] for node in nodes_with_embeddings
        ]
        if not embedding_list:
            logger.warning("No embeddings data retrieved for clustering.")
            return None

        return nodes_with_embeddings, np.array(embedding_list)

    def identify_import_clusters(self, num_clusters: int = 5) -> list[list[str]]:
        """Identify clusters of related modules based on quantum embeddings."""
        embedding_data = self._get_module_embeddings_for_clustering()
        if embedding_data is None:
            return []

        nodes_with_embeddings, embedding = embedding_data

        # Adjust k based on available samples
        actual_k = min(num_clusters, embedding.shape[0])
        if actual_k < 1:
            logger.warning("Cannot cluster: Need at least 1 sample.")
            return []
        if actual_k == 1:
            return [nodes_with_embeddings]

        try:
            clusters_indices: list[list[int]] = self._quantum_kmeans(
                embedding, k=actual_k
            )
        except ValueError as e:  # Catch more specific error
            logger.exception(f"Clustering failed: {e}")  # Use logger.exception
            return []  # Return empty list on clustering error

        # Use list comprehension for filtering empty clusters
        return [
            [nodes_with_embeddings[i] for i in index_list]
            for index_list in clusters_indices
            if index_list  # Ensures inner list is non-empty
        ]

    def _create_kmeans_point_state(self, data_point: np.ndarray) -> QuantumStateVector:
        """Create a quantum state representation for a k-means data point."""
        point_state = QuantumStateVector(self.dimension)
        point_repr = tuple(np.round(data_point, 5))
        point_hash = hash(point_repr)
        start_idx = (point_hash >> 4) % self.dimension
        pattern = np.zeros(self.dimension, dtype=complex)
        num_pattern_indices = min(16, self.dimension)
        for l_idx in range(num_pattern_indices):
            idx = (start_idx + l_idx) % self.dimension
            pattern[idx] = np.exp(1j * l_idx * np.pi / (num_pattern_indices / 2))
        point_state.amplitudes = pattern
        point_state.normalize()
        return point_state

    def _update_kmeans_centroids_and_states(
        self,
        k: int,
        clusters: list[list[int]],
        data: np.ndarray,
        centroids: np.ndarray,
        cluster_states: list[QuantumStateVector],
    ) -> tuple[np.ndarray, list[QuantumStateVector], bool]:
        """Update centroids and quantum states for k-means iteration."""
        centroids_updated = False
        for i in range(k):
            if clusters[i]:
                new_centroid = np.mean(data[clusters[i]], axis=0)
                if not np.allclose(centroids[i], new_centroid):
                    centroids[i] = new_centroid
                    centroids_updated = True

                # Update quantum state (simplified)
                new_state = QuantumStateVector(self.dimension)
                avg_amplitude = np.zeros(self.dimension, dtype=complex)
                # Using centroid hash for state representation
                centroid_repr = tuple(np.round(centroids[i], 5))
                centroid_hash = hash(centroid_repr)
                start_idx = (centroid_hash >> 4) % self.dimension
                for pattern_idx in range(
                    min(16, self.dimension)
                ):  # Renamed l -> pattern_idx
                    idx = (start_idx + pattern_idx) % self.dimension
                    avg_amplitude[idx] += np.exp(1j * pattern_idx * np.pi / 8)

                new_state.amplitudes = avg_amplitude
                new_state.normalize()

                # Use new RNG for noise
                noise = self.rng.normal(0, 0.05, self.dimension) + 1j * self.rng.normal(
                    0, 0.05, self.dimension
                )
                new_state.amplitudes += noise
                new_state.normalize()
                cluster_states[i] = new_state
        return centroids, cluster_states, centroids_updated

    def _quantum_kmeans(
        self, data: np.ndarray, k: int, iterations: int = 100
    ) -> list[list[int]]:
        """Quantum-inspired k-means clustering."""
        n_samples = data.shape[0]
        if n_samples == 0 or k <= 0:
            return []
        k = min(k, n_samples)  # Simplified check

        # Use new RNG
        initial_indices = self.rng.choice(n_samples, k, replace=False)
        centroids = data[initial_indices]

        cluster_states: list[QuantumStateVector] = []
        for _ in range(k):
            state = QuantumStateVector(self.dimension)
            # Use new RNG
            real_part = self.rng.normal(0, 1, self.dimension)
            imag_part = self.rng.normal(0, 1, self.dimension)
            state.amplitudes = real_part + 1j * imag_part
            state.normalize()
            cluster_states.append(state)

        clusters: list[list[int]] = [[] for _ in range(k)]
        for _iter_count in range(iterations):
            clusters = [[] for _ in range(k)]

            for i in range(n_samples):
                point_state = self._create_kmeans_point_state(data[i])

                similarities = [
                    self.compute_quantum_similarity(point_state, state)
                    for state in cluster_states
                ]
                total_sim = sum(similarities)

                if total_sim > self.ZERO_TOLERANCE:
                    probs = np.array([sim / total_sim for sim in similarities])
                    probs /= probs.sum()  # Ensure sums exactly to 1
                    # Use new RNG
                    # Use constant for threshold
                    if self.rng.random() < self.KMEANS_RANDOM_CHOICE_THRESHOLD:
                        cluster_idx = int(np.argmax(probs))
                    else:
                        cluster_idx = self.rng.choice(k, p=probs)
                else:
                    distances = [
                        np.linalg.norm(data[i] - centroid) for centroid in centroids
                    ]
                    cluster_idx = int(np.argmin(distances))

                clusters[cluster_idx].append(i)

            old_centroids = centroids.copy()
            centroids, cluster_states, centroids_updated = (
                self._update_kmeans_centroids_and_states(
                    k, clusters, data, centroids, cluster_states
                )
            )

            # Check convergence based on centroid movement
            centroid_shift = np.sum(np.linalg.norm(centroids - old_centroids, axis=1))
            # Use constant for tolerance
            if (
                not centroids_updated
                or centroid_shift < self.KMEANS_CONVERGENCE_TOLERANCE
            ):
                break

        # Filter out empty clusters before returning
        return [cluster for cluster in clusters if cluster]

    def _group_imports_by_cluster(
        self, symbol_modules: dict[str, str], module_clusters: list[list[str]]
    ) -> defaultdict[int, defaultdict[str, list[str]]]:
        """Group symbols by their providing module within identified clusters."""
        module_to_cluster: dict[str, int] = {}
        for i, cluster in enumerate(module_clusters):
            for module in cluster:
                module_to_cluster[module] = i

        cluster_imports: defaultdict[int, defaultdict[str, list[str]]] = defaultdict(
            lambda: defaultdict(list)
        )
        # Assign symbols to clusters based on their chosen module
        for symbol, module in symbol_modules.items():
            cluster_id = module_to_cluster.get(module, -1)  # -1 for unclustered
            cluster_imports[cluster_id][module].append(symbol)
        return cluster_imports

    def generate_optimized_imports(
        self, required_symbols: list[str], context: list[str] | None = None
    ) -> list[str]:
        """Generate optimized import statements for required symbols."""
        symbol_modules: dict[str, str] = {}
        for symbol in set(required_symbols):  # Use set to avoid duplicates
            if result := self.find_best_import_for_symbol(symbol, context):
                module, confidence = result
                # Use constant threshold for confidence
                if confidence > self.IMPORT_CONFIDENCE_THRESHOLD:
                    symbol_modules[symbol] = module
                else:
                    logger.info(
                        f"Low confidence ({confidence:.2f}) for importing '{symbol}' from '{module}'"
                    )
            else:
                logger.warning(f"Could not find suitable module for symbol: '{symbol}'")

        if not symbol_modules:
            return ["# No suitable imports found or confidence too low."]

        # Use a reasonable default number of clusters or make it dynamic
        num_clusters = max(1, min(5, len(set(symbol_modules.values())) // 2))
        module_clusters = self.identify_import_clusters(num_clusters=num_clusters)

        cluster_imports = self._group_imports_by_cluster(
            symbol_modules, module_clusters
        )

        import_statements: list[str] = []
        sorted_clusters = sorted(cluster_imports.items())

        for i, (cluster_id, module_symbols) in enumerate(sorted_clusters):
            # Add cluster comments for organization
            if cluster_id >= 0:
                # Try to find a representative module name for the cluster comment
                # Handle case where cluster might be empty after filtering symbols
                cluster_modules_list = list(module_symbols.keys())
                if cluster_modules_list:
                    cluster_name = (
                        f"Cluster {cluster_id} ({cluster_modules_list[0]}...)"
                    )
                else:
                    cluster_name = f"Cluster {cluster_id} (Empty)"
                import_statements.append(f"# --- {cluster_name} ---")
            else:
                import_statements.append("# --- Other Imports ---")

            # Generate import statements for the cluster
            for module, symbols in sorted(module_symbols.items()):
                if symbols:
                    symbols_str = ", ".join(sorted(symbols))
                    import_statements.append(f"from {module} import {symbols_str}")

            # Add blank line between cluster blocks
            if i < len(sorted_clusters) - 1:
                import_statements.append("")

        return import_statements

    def update_from_feedback(
        self,
        symbol: str,
        correct_module: str,
        context: list[str] | None = None,
    ) -> bool:
        """Update the model based on feedback."""
        symbol_state = self.symbol_states.get(symbol)
        module_state = self.module_states.get(correct_module)

        if not symbol_state or not module_state:
            logger.warning(
                f"Symbol '{symbol}' or Module '{correct_module}' not found for feedback."
            )
            return False

        # Ensure relationship exists or add it
        if correct_module not in self.symbol_providers.get(symbol, []):
            # Use a try-except block for add_provider_relationship if it can fail
            try:
                if not self.add_provider_relationship(correct_module, symbol):
                    # Handle case where adding relationship fails internally
                    # Logged within add_provider_relationship if it returns False
                    logger.warning(
                        f"Failed to add provider relationship in feedback: {correct_module} -> {symbol}"
                    )
                    # Decide if we should proceed with state update or return False
                    # Continuing allows state update even if relationship add fails
            except KeyError as e:  # Catch specific error from index lookup
                logger.exception(
                    f"Failed to add provider relationship due to key error: {e}"
                )
                return False  # Stop on unexpected error

        # Strengthen quantum connection via entanglement operator
        entangle_op = np.eye(self.dimension, dtype=complex)
        try:
            module_idx = self.module_to_index[correct_module]
            symbol_idx = self.symbol_to_index[symbol]
        except KeyError as e:
            logger.exception(f"Index lookup failed for {e} during feedback update.")
            return False

        theta = np.pi / 3  # Stronger angle for feedback update
        half_dim = self.dimension // 2
        num_entangle_indices = min(32, self.dimension // 32)

        for i in range(num_entangle_indices):
            mod_hash_part = module_idx * 8 + i
            sym_hash_part = symbol_idx * 8 + i
            src_idx = mod_hash_part % half_dim
            tgt_idx = (sym_hash_part % half_dim) + half_dim

            if 0 <= src_idx < self.dimension and 0 <= tgt_idx < self.dimension:
                cos_t, sin_t = np.cos(theta), np.sin(theta)
                entangle_op[src_idx, src_idx] = cos_t
                entangle_op[src_idx, tgt_idx] = -sin_t
                entangle_op[tgt_idx, src_idx] = sin_t
                entangle_op[tgt_idx, tgt_idx] = cos_t

        # Apply gate with potentially higher weight/iterations for feedback?
        module_state.apply_gate(entangle_op)
        symbol_state.apply_gate(entangle_op)

        # Context-based update (if context provided)
        if context:
            self._extracted_from_update_from_feedback_67(context, symbol_state)
        self.distance_cache = {}  # Invalidate cache after model update
        logger.info(f"Feedback processed for {symbol} -> {correct_module}")
        return True

    # TODO Rename this here and in `update_from_feedback`
    def _extracted_from_update_from_feedback_67(self, context, symbol_state):
        context_operator = self._create_context_operator(context)
        temp_state = QuantumStateVector(self.dimension)
        temp_state.amplitudes = symbol_state.amplitudes.copy()
        temp_state.apply_gate(context_operator)

        # Blend the symbol state towards the context-influenced state
        lerp_factor = 0.5  # Stronger update factor for feedback
        blended_amplitudes = (
            1 - lerp_factor
        ) * symbol_state.amplitudes + lerp_factor * temp_state.amplitudes
        symbol_state.amplitudes = blended_amplitudes
        symbol_state.normalize()
