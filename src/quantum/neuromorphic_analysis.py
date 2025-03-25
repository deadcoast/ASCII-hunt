import networkx as nx
import numpy as np
import tensorflow as tf
from transformers import GPT2Tokenizer, TFGPT2Model


class NeuromorphicImportAnalyzer:
    def __init__(self, model_path="gpt2"):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
        self.model = TFGPT2Model.from_pretrained(model_path)
        self.synapse_graph = nx.DiGraph()
        self.module_embeddings = {}
        self.symbol_embeddings = {}
        self.context_cache = {}
        self.learning_rate = 0.01
        self.plasticity = 0.5  # Hebbian learning parameter

    def analyze_module(self, module_path, content=None):
        """Analyze a module using neuromorphic-inspired methods."""
        if content is None:
            with open(module_path) as f:
                content = f.read()

        # Create an embedding for the entire module
        module_embedding = self._create_semantic_embedding(content)
        self.module_embeddings[module_path] = module_embedding

        # Parse the module to extract imports and symbols
        import_network, symbol_map = self._parse_module(content)

        # Create embeddings for each symbol
        for symbol, context in symbol_map.items():
            symbol_key = f"{module_path}:{symbol}"
            self.symbol_embeddings[symbol_key] = self._create_semantic_embedding(
                context
            )

            # Add to the synapse graph
            if symbol_key not in self.synapse_graph:
                self.synapse_graph.add_node(symbol_key, type="symbol")

            # Link symbols to their module
            self.synapse_graph.add_edge(
                module_path, symbol_key, type="defines", weight=self.plasticity
            )

        # Process imports
        for import_item in import_network:
            imported_module = import_item["module"]

            # Add the import to the synapse graph
            if imported_module not in self.synapse_graph:
                self.synapse_graph.add_node(imported_module, type="module")

            # Create a synaptic connection for this import
            self.synapse_graph.add_edge(
                module_path, imported_module, type="imports", weight=self.plasticity
            )

            # Apply Hebbian learning - "neurons that fire together, wire together"
            for symbol_key in [
                k for k in self.symbol_embeddings if k.startswith(f"{module_path}:")
            ]:
                # Calculate semantic similarity between symbol and imported module
                symbol_embedding = self.symbol_embeddings[symbol_key]
                similarity = self._calculate_semantic_similarity(
                    symbol_embedding,
                    self.module_embeddings.get(imported_module, module_embedding),
                )

                # If similarity is high, create a synaptic connection
                if similarity > 0.7:
                    self.synapse_graph.add_edge(
                        symbol_key,
                        imported_module,
                        type="semantic_dependency",
                        weight=similarity * self.plasticity,
                    )

        return import_network

    def strengthen_connections(self, activation_pattern):
        """Strengthen connections based on activation patterns (Hebbian learning)."""
        for source, target in activation_pattern:
            if self.synapse_graph.has_edge(source, target):
                # Strengthen the connection
                current_weight = self.synapse_graph[source][target]["weight"]
                new_weight = current_weight + self.learning_rate * (1 - current_weight)
                self.synapse_graph[source][target]["weight"] = new_weight

    def predict_missing_imports(self, code_context, existing_imports=None):
        """Predict necessary imports for a code context using the neuromorphic network."""
        # Get semantic embedding for the code context
        context_embedding = self._create_semantic_embedding(code_context)

        # Extract symbols used in the context
        used_symbols = self._extract_symbols_from_context(code_context)

        # Find potential imported modules for each symbol
        import_candidates = {}

        for symbol in used_symbols:
            # Activate the neural network with this symbol
            activation = {}
            visited = set()

            # Initial activation from semantic similarity
            for node in self.synapse_graph.nodes():
                if self.synapse_graph.nodes[node].get("type") == "symbol":
                    if node.split(":")[-1] == symbol:
                        # Same symbol name from some module
                        module_part = node.split(":")[0]
                        symbol_embedding = self.symbol_embeddings.get(node)

                        if symbol_embedding is not None:
                            similarity = self._calculate_semantic_similarity(
                                context_embedding, symbol_embedding
                            )
                            activation[node] = similarity

                            # Add the module to the activation pattern
                            activation[module_part] = similarity * 0.5
                            visited.add(node)
                            visited.add(module_part)

            # Propagate activation through the network (spreading activation)
            for _ in range(3):  # 3 steps of spreading
                new_activation = activation.copy()

                for node in activation:
                    if activation[node] > 0.2:  # Activation threshold
                        for _, neighbor, data in self.synapse_graph.edges(
                            node, data=True
                        ):
                            if neighbor not in visited:
                                weight = data.get("weight", 0.1)
                                new_activation[neighbor] = (
                                    new_activation.get(neighbor, 0)
                                    + activation[node] * weight
                                )
                                visited.add(neighbor)

                activation = new_activation

            # Find the most activated modules that could provide this symbol
            candidates = []
            for node, value in activation.items():
                if (
                    self.synapse_graph.nodes.get(node, {}).get("type") == "module"
                    and value > 0.3
                ):
                    candidates.append((node, value))

            # Sort by activation strength
            candidates.sort(key=lambda x: x[1], reverse=True)
            import_candidates[symbol] = candidates

        # Generate import statements based on activation patterns
        suggested_imports = []
        seen_modules = set(existing_imports or [])

        for symbol, candidates in import_candidates.items():
            for module, score in candidates:
                if module not in seen_modules:
                    seen_modules.add(module)

                    # Check if we should import the whole module or just the symbol
                    if self._should_import_whole_module(module, symbol, score):
                        suggested_imports.append(
                            {"type": "import", "module": module, "confidence": score}
                        )
                    else:
                        suggested_imports.append(
                            {
                                "type": "from",
                                "module": module,
                                "name": symbol,
                                "confidence": score,
                            }
                        )

        # Strengthen connections based on this activation pattern
        # This is how the network learns
        activation_pattern = []
        for symbol, candidates in import_candidates.items():
            for module, _ in candidates[:1]:  # Top candidate for each symbol
                symbol_nodes = [
                    n
                    for n in self.synapse_graph.nodes()
                    if n.split(":")[-1] == symbol
                    and self.synapse_graph.nodes[n].get("type") == "symbol"
                ]

                for symbol_node in symbol_nodes:
                    activation_pattern.append((symbol_node, module))

        self.strengthen_connections(activation_pattern)

        return suggested_imports

    def _parse_module(self, content: str) -> tuple[list[dict], dict[str, str]]:
        """Parse a module to extract imports and symbol definitions."""
        try:
            import ast

            tree = ast.parse(content)
            imports = []
            symbol_map = {}

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(
                            {
                                "type": "import",
                                "module": name.name,
                                "alias": name.asname,
                            }
                        )
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        imports.append(
                            {
                                "type": "from",
                                "module": module,
                                "name": name.name,
                                "alias": name.asname,
                            }
                        )

                # Extract symbol definitions
                elif isinstance(
                    node, (ast.FunctionDef | ast.ClassDef | ast.AsyncFunctionDef)
                ):
                    symbol_map[node.name] = ast.get_source_segment(content, node) or ""
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            symbol_map[target.id] = (
                                ast.get_source_segment(content, node) or ""
                            )

            return imports, symbol_map
        except Exception as e:
            print(f"Error parsing module: {e}")
            return [], {}

    def _extract_symbols_from_context(self, code_context: str) -> list[str]:
        """Extract symbols used in the given code context."""
        try:
            import ast

            tree = ast.parse(code_context)
            symbols = set()

            for node in ast.walk(tree):
                # Extract variable names
                if isinstance(node, ast.Name):
                    symbols.add(node.id)
                # Extract attribute access
                elif isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        symbols.add(node.value.id)
                # Extract function calls
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        symbols.add(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        if isinstance(node.func.value, ast.Name):
                            symbols.add(node.func.value.id)

            return list(symbols)
        except Exception as e:
            print(f"Error extracting symbols: {e}")
            return []

    def _should_import_whole_module(
        self, module: str, symbol: str, score: float
    ) -> bool:
        """Determine if we should import the whole module or just the symbol."""
        # Check if the symbol is commonly used from this module
        symbol_nodes = [
            n for n in self.synapse_graph.nodes() if n.startswith(f"{module}:")
        ]

        if not symbol_nodes:
            return True  # No symbol information, import whole module

        # Count how many symbols from this module are used
        module_symbol_count = len(symbol_nodes)

        # If many symbols are used from this module, import the whole thing
        if module_symbol_count > 3:
            return True

        # If the symbol has high semantic similarity with the module itself
        if score > 0.8:
            return True

        # Check if this symbol is commonly imported individually
        individual_imports = sum(1 for n in symbol_nodes if n.endswith(f":{symbol}"))
        if individual_imports > 0:
            return False

        return True

    def _create_semantic_embedding(self, code_text: str) -> np.ndarray:
        """Create a semantic embedding for the given code text."""
        # Tokenize the code
        inputs = self.tokenizer(
            code_text, return_tensors="tf", max_length=512, truncation=True
        )

        # Get the model's output
        outputs = self.model(inputs)

        # Use the last hidden state's mean as the embedding
        embedding = tf.reduce_mean(outputs.last_hidden_state, axis=1)

        return embedding.numpy()[0]

    def _calculate_semantic_similarity(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """Calculate cosine similarity between two embeddings."""
        if embedding1 is None or embedding2 is None:
            return 0.0

        # Normalize the embeddings
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)

        return float(similarity)
