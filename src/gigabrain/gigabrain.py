from gigabrain.multiscale_importer import MultiScaleImportRecommender
from gigabrain.import_entity import ImportEntity
from gigabrain.hypergraph_network import HypergraphImportNetwork
from gigabrain.fractal_analyzer import FractalDimensionAnalyzer
from gigabrain.wavelet_analyzer import WaveletImportAnalyzer
from gigabrain.riemannian_optimizer import RiemannianImportOptimizer

import os
import networkx as nx
from collections import defaultdict


class GIGABRAIN:
    """
    The GIGABRAIN unified import intelligence system.

    This system integrates multiple advanced algorithms and mathematical frameworks
    to provide unparalleled import management capabilities.
    """

    def __init__(self, project_path):
        self.project_path = project_path

        # Core components
        self.tensor_field_operator = TensorFieldOperator()
        self.manifold_mapper = NonlinearManifoldMapper()
        self.hypergraph = HypergraphImportNetwork()
        self.fractal_analyzer = FractalDimensionAnalyzer()
        self.wavelet_analyzer = WaveletImportAnalyzer()
        self.riemannian_optimizer = RiemannianImportOptimizer()
        self.eigenfunction_analyzer = ModularEigenfunctionAnalyzer()
        self.information_optimizer = InformationGeometryOptimizer()
        self.import_recommender = None

        # Codebase representation
        self.import_entities = {}
        self.module_graph = nx.DiGraph()
        self.symbol_to_modules = defaultdict(list)
        self.module_field = {}
        self.manifold_coords = {}

        # Analysis results
        self.complexity_profile = {}
        self.import_communities = {}
        self.optimal_structure = {}
        self.temporal_patterns = {}

    def initialize(self):
        """Initialize the system by analyzing the project."""
        print("Initializing GIGABRAIN system...")

        # Extract code corpus
        code_corpus = self._extract_code_corpus()

        # Initialize recommender
        self.import_recommender = MultiScaleImportRecommender(code_corpus)
        self.import_recommender.initialize()

        # Build entity representations
        self._build_entities()

        # Build module graph
        self._build_module_graph()

        # Build tensor field representation
        self._build_tensor_field()

        # Map to manifold
        self._map_to_manifold()

        # Analyze complexity
        self._analyze_complexity()

        # Identify optimal structure
        self._identify_optimal_structure()

        print("GIGABRAIN initialization complete.")

    def _extract_code_corpus(self):
        """Extract code corpus from the project."""
        code_corpus = []

        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            code_corpus.append({"path": file_path, "content": content})
                    except:
                        pass

        return code_corpus

    def _build_entities(self):
        """Build entity representations for imports."""
        # Extract imports and symbols
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        # Parse file
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        # Extract imports
                        imports = self._extract_imports(content)

                        # Extract symbols
                        symbols = self._extract_symbols(content)

                        # Update symbol to modules mapping
                        for import_info in imports:
                            module = import_info["module"]

                            if module not in self.import_entities:
                                self.import_entities[module] = ImportEntity(
                                    name=module, path=module
                                )
                                self.import_entities[module].initialize_tensor()

                            # Map imported symbols
                            for symbol in import_info.get("symbols", []):
                                self.symbol_to_modules[symbol].append(module)

                                if symbol not in self.import_entities[module].symbols:
                                    self.import_entities[module].symbols.append(symbol)
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

    def _build_module_graph(self):
        """Build a graph representing module relationships."""
        # Add modules as nodes
        for module, entity in self.import_entities.items():
            self.module_graph.add_node(
                module,
                **{
                    "symbols": entity.symbols,
                    "type": "module",
                },
            )

        # Add symbols as nodes
        for symbol, modules in self.symbol_to_modules.items():
            self.module_graph.add_node(symbol, **{"modules": modules, "type": "symbol"})
