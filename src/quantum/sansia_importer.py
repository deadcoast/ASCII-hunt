import ast
import json
import os
from collections import defaultdict
from typing import Any, TypeVar

import networkx as nx
import numpy as np
import numpy.typing as npt
import z3  # Import z3 module directly

try:
    from tensorflow import keras

    KERAS_AVAILABLE = True
except ImportError:
    print(
        "Warning: tensorflow.keras not found. Neural prediction features will be limited."
    )
    keras = None
    KERAS_AVAILABLE = False

# Type variables
Component = TypeVar("Component")
Symbol = str
Module = str
Context = list[str]


class SymbolicImportReasoner:
    def __init__(self) -> None:
        self.solver = z3.Solver()  # type: ignore
        self.symbol_vars: dict[str, z3.BoolRef] = {}  # type: ignore
        self.module_vars: dict[str, z3.BoolRef] = {}  # type: ignore
        self.constraints: list[z3.BoolRef] = []  # type: ignore

    def add_symbol(self, symbol_name: str) -> None:
        """Add a symbol to the reasoner."""
        if symbol_name not in self.symbol_vars:
            self.symbol_vars[symbol_name] = z3.Bool(f"sym_{symbol_name}")  # type: ignore

    def add_module(self, module_name: str) -> None:
        """Add a module to the reasoner."""
        if module_name not in self.module_vars:
            self.module_vars[module_name] = z3.Bool(f"mod_{module_name}")  # type: ignore

    def add_provides_constraint(self, module_name: str, symbol_name: str) -> None:
        """Add constraint that a module provides a symbol."""
        self.add_module(module_name)
        self.add_symbol(symbol_name)

        mod_var = self.module_vars[module_name]
        sym_var = self.symbol_vars[symbol_name]

        # If the module is imported, it can provide the symbol
        constraint = z3.Implies(mod_var, sym_var)  # type: ignore
        self.constraints.append(constraint)
        self.solver.add(constraint)

    def add_requires_constraint(self, module_name: str, required_module: str) -> None:
        """Add constraint that one module requires another."""
        self.add_module(module_name)
        self.add_module(required_module)

        mod_var = self.module_vars[module_name]
        req_var = self.module_vars[required_module]

        # If a module is imported, its requirements must also be imported
        constraint = z3.Implies(mod_var, req_var)  # type: ignore
        self.constraints.append(constraint)
        self.solver.add(constraint)

    def add_conflict_constraint(self, module1: str, module2: str) -> None:
        """Add constraint that two modules conflict."""
        self.add_module(module1)
        self.add_module(module2)

        mod1_var = self.module_vars[module1]
        mod2_var = self.module_vars[module2]

        # Both modules cannot be imported together
        constraint = z3.Not(z3.And(mod1_var, mod2_var))  # type: ignore
        self.constraints.append(constraint)
        self.solver.add(constraint)

    def solve_for_symbols(self, required_symbols: list[str]) -> tuple[bool, list[str]]:
        """Find a minimal set of modules to import for the required symbols."""
        # Add constraints that required symbols must be provided
        for symbol in required_symbols:
            self.add_symbol(symbol)
            self.solver.add(self.symbol_vars[symbol])

        # Objective: minimize the number of imported modules
        if self.solver.check() == z3.sat:  # type: ignore
            model = self.solver.model()

            # Find modules that should be imported
            imported_modules = []
            for module, var in self.module_vars.items():
                if model.evaluate(var):
                    imported_modules.append(module)

            return True, imported_modules
        return False, []

    def reset(self) -> None:
        """Reset the reasoner."""
        self.solver.reset()
        for constraint in self.constraints:
            self.solver.add(constraint)


class NeuralImportPredictor:
    def __init__(self, model_path: str | None = None) -> None:
        """Initialize the neural import predictor."""
        if not KERAS_AVAILABLE:
            raise ImportError("tensorflow.keras is required for NeuralImportPredictor")

        self.model: Any | None = None  # Using Any for keras.Model type
        self.symbol_embeddings: dict[str, npt.NDArray[np.float32]] = {}
        self.module_embeddings: dict[str, npt.NDArray[np.float32]] = {}
        self.embedding_dim = 128

        if model_path:
            self.load_model(model_path)
        else:
            self._build_model()

    def _build_model(self) -> None:
        """Build the neural network model."""
        if not KERAS_AVAILABLE or not keras:
            raise ImportError("tensorflow.keras is required for model building")

        try:
            # Symbol input
            symbol_input = keras.layers.Input(shape=(self.embedding_dim,))

            # Context input (sequence of symbol embeddings)
            context_input = keras.layers.Input(shape=(None, self.embedding_dim))

            # Process context using LSTM
            context_encoded = keras.layers.LSTM(64)(context_input)

            # Combine symbol and context
            combined = keras.layers.Concatenate()([symbol_input, context_encoded])

            # Dense layers
            x = keras.layers.Dense(128, activation="relu")(combined)
            x = keras.layers.Dropout(0.2)(x)
            x = keras.layers.Dense(64, activation="relu")(x)

            # Output layer (probability for each module)
            outputs = keras.layers.Dense(
                len(self.module_embeddings), activation="sigmoid"
            )(x)

            self.model = keras.Model(
                inputs=[symbol_input, context_input], outputs=outputs
            )
            self.model.compile(
                optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"]
            )
        except Exception as e:
            print(f"Error building model: {e}")
            raise

    def train(self, training_data: list[dict[str, Any]], epochs: int = 10) -> None:
        """Train the model on symbol-context-module examples."""
        if not KERAS_AVAILABLE or not keras:
            raise ImportError("tensorflow.keras is required for training")

        if not self.model:
            self._build_model()

        try:
            # Prepare training data
            symbol_inputs = []
            context_inputs = []
            module_outputs = []

            for data in training_data:
                symbol = data["symbol"]
                context = data.get("context", [])
                module = data["module"]

                # Get symbol embedding
                symbol_emb = self._get_symbol_embedding(symbol)
                symbol_inputs.append(symbol_emb)

                # Get context embeddings
                context_embs = [self._get_symbol_embedding(s) for s in context]
                context_inputs.append(np.array(context_embs))

                # Create one-hot encoded module vector
                module_vector = np.zeros(len(self.module_embeddings))
                if module in self.module_embeddings:
                    idx = list(self.module_embeddings.keys()).index(module)
                    module_vector[idx] = 1
                module_outputs.append(module_vector)

            # Convert to numpy arrays
            symbol_inputs = np.array(symbol_inputs)
            if keras and hasattr(keras.preprocessing, "sequence"):
                context_inputs = keras.preprocessing.sequence.pad_sequences(
                    context_inputs, padding="post", dtype="float32"
                )
            else:
                # Fallback padding implementation if keras is not available
                max_len = max(len(x) for x in context_inputs)
                padded = np.zeros(
                    (len(context_inputs), max_len, self.embedding_dim), dtype=np.float32
                )
                for i, seq in enumerate(context_inputs):
                    padded[i, : len(seq)] = seq
                context_inputs = padded

            module_outputs = np.array(module_outputs)

            # Train the model
            if self.model is not None:  # Check if model is not None before calling fit
                self.model.fit(
                    [symbol_inputs, context_inputs],
                    module_outputs,
                    epochs=epochs,
                    batch_size=32,
                    validation_split=0.2,
                )
        except Exception as e:
            print(f"Error during training: {e}")
            raise

    def predict_modules(
        self, symbol: str, context: list[str]
    ) -> list[tuple[str, float]]:
        """Predict likely modules for a symbol given its context."""
        if not KERAS_AVAILABLE or not keras:
            raise ImportError("tensorflow.keras is required for prediction")

        if not self.model:
            raise ValueError("Model not initialized")

        try:
            # Get embeddings
            symbol_emb = self._get_symbol_embedding(symbol)
            context_embs = [self._get_symbol_embedding(s) for s in context]

            # Prepare inputs
            symbol_input = np.array([symbol_emb])
            context_input = np.array([context_embs])

            # Pad context input if needed
            if keras and hasattr(keras.preprocessing, "sequence"):
                context_input = keras.preprocessing.sequence.pad_sequences(
                    [context_embs], padding="post", dtype="float32"
                )
            else:
                # Fallback padding implementation
                max_len = max(len(context_embs), 1)  # At least length 1
                padded = np.zeros((1, max_len, self.embedding_dim), dtype=np.float32)
                padded[0, : len(context_embs)] = context_embs
                context_input = padded

            # Get predictions
            predictions = self.model.predict([symbol_input, context_input])[0]

            # Convert to module-probability pairs
            modules = list(self.module_embeddings.keys())
            module_probs = [
                (mod, float(prob))
                for mod, prob in zip(modules, predictions, strict=False)
            ]

            # Sort by probability
            return sorted(module_probs, key=lambda x: x[1], reverse=True)
        except Exception as e:
            print(f"Error during prediction: {e}")
            return []

    def _get_symbol_embedding(self, symbol: str) -> npt.NDArray[np.float32]:
        """Get or create embedding vector for a symbol."""
        try:
            if symbol not in self.symbol_embeddings:
                # Create random embedding if not seen before
                self.symbol_embeddings[symbol] = np.random.normal(
                    0, 1, self.embedding_dim
                ).astype(np.float32)
            return self.symbol_embeddings[symbol]
        except Exception as e:
            print(f"Error getting symbol embedding: {e}")
            return np.zeros(self.embedding_dim, dtype=np.float32)

    def save_model(self, path: str) -> None:
        """Save the model and embeddings."""
        if not KERAS_AVAILABLE or not keras:
            raise ImportError("tensorflow.keras is required for saving model")

        try:
            if self.model:
                self.model.save(f"{path}_model")

            # Save embeddings as arrays
            symbol_arrays = {k: v.tolist() for k, v in self.symbol_embeddings.items()}
            module_arrays = {k: v.tolist() for k, v in self.module_embeddings.items()}
            embeddings = {"symbols": symbol_arrays, "modules": module_arrays}
            with open(f"{path}_embeddings.json", "w") as f:
                json.dump(embeddings, f)
        except Exception as e:
            print(f"Error saving model: {e}")
            raise

    def load_model(self, path: str) -> None:
        """Load the model and embeddings."""
        if not KERAS_AVAILABLE or not keras:
            raise ImportError("tensorflow.keras is required for loading model")

        try:
            if not keras:
                raise ImportError("keras is not available")
            self.model = keras.models.load_model(f"{path}_model")

            with open(f"{path}_embeddings.json") as f:
                embeddings = json.load(f)

            # Convert lists back to numpy arrays
            self.symbol_embeddings = {
                k: np.array(v, dtype=np.float32)
                for k, v in embeddings["symbols"].items()
            }
            self.module_embeddings = {
                k: np.array(v, dtype=np.float32)
                for k, v in embeddings["modules"].items()
            }
        except Exception as e:
            print(f"Error loading model: {e}")
            self._build_model()


class SANSIA:
    """Self-Adaptive Neural-Symbolic Import Architecture"""

    def __init__(self, codebase_path: str) -> None:
        self.codebase_path = codebase_path
        self.module_graph: nx.DiGraph = nx.DiGraph()  # Initialize directly
        self.symbolic_reasoner: SymbolicImportReasoner = (
            SymbolicImportReasoner()
        )  # Initialize directly
        try:
            self.neural_predictor: NeuralImportPredictor | None = (
                NeuralImportPredictor() if KERAS_AVAILABLE else None
            )
        except ImportError:
            self.neural_predictor = None
            print("Neural prediction features will be disabled")
        self.symbol_providers = defaultdict(list)
        self.module_requirements = defaultdict(list)
        self.conflicting_modules = []
        self.feedback_data = []

    def initialize(self) -> None:
        """Initialize SANSIA components."""
        try:
            self._build_module_graph()
            self._initialize_symbolic_reasoner()
            self._generate_initial_feedback_data()
            if self.neural_predictor and self.feedback_data:
                self.neural_predictor.train(self.feedback_data)
        except Exception as e:
            print(f"Error during initialization: {e}")
            raise

    def _build_module_graph(self) -> nx.DiGraph:
        """Build the module dependency graph."""
        try:
            # Scan codebase for Python files
            for root, _, files in os.walk(self.codebase_path):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        self._analyze_file_dependencies(file_path)
            return self.module_graph
        except Exception as e:
            print(f"Error building module graph: {e}")
            raise

    def _analyze_file_dependencies(self, file_path: str) -> None:
        """Analyze a Python file for its dependencies."""
        try:
            with open(file_path) as f:
                content = f.read()

            tree = ast.parse(content)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            # Add node and edges to graph
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            self.module_graph.add_node(
                module_name, file_path=file_path, imports=imports
            )
            for imp in imports:
                self.module_graph.add_edge(module_name, imp)
                self.module_requirements[module_name].append(imp)
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def _initialize_symbolic_reasoner(self) -> None:
        """Initialize the symbolic reasoning component."""
        try:
            # Add module relationships to the symbolic reasoner
            for module, requirements in self.module_requirements.items():
                for required_module in requirements:
                    self.symbolic_reasoner.add_requires_constraint(
                        module, required_module
                    )

            # Add symbol providers
            for symbol, providers in self.symbol_providers.items():
                for provider in providers:
                    self.symbolic_reasoner.add_provides_constraint(provider, symbol)

            # Add conflicting modules
            for module1, module2 in self.conflicting_modules:
                self.symbolic_reasoner.add_conflict_constraint(module1, module2)
        except Exception as e:
            print(f"Error initializing symbolic reasoner: {e}")
            raise

    def _generate_initial_feedback_data(self) -> None:
        """Generate initial feedback data for training."""
        if not self.module_graph:
            raise ValueError("Module graph not initialized")

        # For each symbol and its providers
        for symbol, providers in self.symbol_providers.items():
            for provider in providers:
                # Generate example contexts for this symbol-module pair
                contexts = self._generate_example_contexts(symbol, provider)

                # Add feedback data entries
                for context in contexts:
                    self.feedback_data.append(
                        {"symbol": symbol, "module": provider, "context": context}
                    )

    def _generate_example_contexts(self, symbol: str, module: str) -> list[list[str]]:
        """Generate example contexts for a symbol-module pair."""
        contexts = []

        # Get all files that import this module
        importing_files = []
        for node in self.module_graph.nodes():
            if module in self.module_graph.nodes[node].get("imports", []):
                importing_files.append(node)

        # Extract contexts from these files
        for file_path in importing_files:
            try:
                with open(file_path) as f:
                    code = f.read()
                context = self._extract_context(code, symbol)
                if context:
                    contexts.append(context)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        return contexts

    def analyze_code(self, code: str) -> dict[str, str]:
        """Analyze code and suggest imports."""
        # Extract symbols that need to be imported
        symbols = self._extract_symbols(code)

        # Get suggestions from neural predictor
        neural_suggestions: dict[str, str] = {}
        if self.neural_predictor is not None:  # Check if neural_predictor exists
            for symbol in symbols:
                context = self._extract_context(code, symbol)
                predictions = self.neural_predictor.predict_modules(symbol, context)
                if predictions:  # Check if we got any predictions
                    module, confidence = predictions[0]  # Get top prediction
                    if confidence > 0.7:  # Confidence threshold
                        neural_suggestions[symbol] = module

        # Get suggestions from symbolic reasoner
        symbolic_suggestions = self._get_symbolic_suggestions(symbols)

        # Combine suggestions, preferring symbolic ones
        final_suggestions = {}
        for symbol in symbols:
            if symbol in symbolic_suggestions:
                final_suggestions[symbol] = symbolic_suggestions[symbol]
            elif symbol in neural_suggestions:
                final_suggestions[symbol] = neural_suggestions[symbol]

        return final_suggestions

    def _extract_symbols(self, code: str) -> list[str]:
        """Extract symbols that need to be imported from the code."""
        try:
            tree = ast.parse(code)
            symbols = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    if isinstance(node.ctx, ast.Load):
                        symbols.add(node.id)
                elif isinstance(node, ast.Attribute):
                    if isinstance(node.ctx, ast.Load):
                        symbols.add(node.attr)

            return list(symbols)
        except Exception as e:
            print(f"Error extracting symbols: {e}")
            return []

    def _extract_context(self, code: str, symbol: str) -> list[str]:
        """Extract context around a symbol usage."""
        try:
            lines = code.split("\n")
            context = []

            for i, line in enumerate(lines):
                if symbol in line:
                    # Add surrounding lines as context
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    context.extend(lines[start:end])

            # Tokenize context
            tokens = []
            for line in context:
                tokens.extend(line.split())

            return tokens
        except Exception as e:
            print(f"Error extracting context: {e}")
            return []

    def _get_symbolic_suggestions(self, symbols: list[str]) -> dict[str, str]:
        """Get suggestions from the symbolic reasoner."""
        suggestions = {}
        for symbol in symbols:
            success, import_modules = self.symbolic_reasoner.solve_for_symbols([symbol])
            if success:
                suggestions[symbol] = import_modules[0]
        return suggestions

    def provide_feedback(
        self, symbol: str, correct_module: str, context: list[str]
    ) -> None:
        """Provide feedback to improve future predictions."""
        # Add to feedback data
        self.feedback_data.append(
            {"symbol": symbol, "module": correct_module, "context": context}
        )

        # Update symbolic reasoner
        self.symbolic_reasoner.add_provides_constraint(correct_module, symbol)

        # Trigger adaptation if enough new feedback
        if len(self.feedback_data) % 10 == 0:  # Every 10 feedback items
            self.adapt()

    def adapt(self) -> None:
        """Adapt the system based on accumulated feedback."""
        # Retrain neural predictor with all feedback data
        if self.neural_predictor is not None:  # Add null check
            self.neural_predictor.train(self.feedback_data, epochs=5)

        # Reset and reinitialize symbolic reasoner
        self.symbolic_reasoner.reset()
        self._initialize_symbolic_reasoner()
