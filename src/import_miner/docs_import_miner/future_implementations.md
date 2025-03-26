# Advanced Import Management: Further Enhancements

You've already developed a sophisticated system for managing Python imports, but there are several ways to take it even further. Here's how you can enhance your script's ability to correct and track imports with additional third-party libraries, mathematical approaches, and advanced techniques.

## Third-Party Libraries for Import Enhancement

### 1. Machine Learning with scikit-learn

Scikit-learn can help build predictive models for import suggestions based on code patterns:

```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

class MLImportSuggester:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 3))
        self.nn_model = None
        self.import_database = []

    def train(self, code_samples, correct_imports):
        """Train the model on existing code with known correct imports."""
        # Transform code samples into feature vectors
        X = self.vectorizer.fit_transform(code_samples)

        # Train nearest neighbors model
        self.nn_model = NearestNeighbors(n_neighbors=5, algorithm='ball_tree')
        self.nn_model.fit(X)

        # Store import database
        self.import_database = correct_imports

    def suggest_imports(self, new_code):
        """Suggest imports for new code based on similar patterns."""
        code_vector = self.vectorizer.transform([new_code])

        # Find similar code patterns
        distances, indices = self.nn_model.kneighbors(code_vector)

        # Weight suggestions by similarity
        weighted_suggestions = {}
        total_weight = np.sum(1.0 / (distances + 0.1))

        for i, idx in enumerate(indices[0]):
            weight = 1.0 / (distances[0][i] + 0.1) / total_weight
            for imp in self.import_database[idx]:
                if imp not in weighted_suggestions:
                    weighted_suggestions[imp] = 0
                weighted_suggestions[imp] += weight

        # Return suggestions sorted by confidence
        return sorted(weighted_suggestions.items(), key=lambda x: x[1], reverse=True)
```

This adds machine learning to your pipeline to suggest imports based on code patterns it has seen before.

### 2. Abstract Syntax Tree Enhancement with LibCST

LibCST provides a more powerful way to analyze and modify Python code:

```python
import libcst as cst
from libcst.metadata import MetadataWrapper, ScopeProvider

class CSTImportAnalyzer(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (ScopeProvider,)

    def __init__(self):
        super().__init__()
        self.imports = []
        self.references = set()
        self.defined = set()

    def visit_Import(self, node):
        for name in node.names:
            alias = name.asname.name if name.asname else name.name.value
            self.imports.append({
                "type": "import",
                "module": name.name.value,
                "alias": alias,
                "node": node
            })

    def visit_ImportFrom(self, node):
        module = node.module.value if node.module else ""
        for name in node.names:
            alias = name.asname.name if name.asname else name.name.value
            self.imports.append({
                "type": "from",
                "module": module,
                "name": name.name.value,
                "alias": alias,
                "node": node
            })

    def visit_Name(self, node):
        if isinstance(node.ctx, cst.Load):
            self.references.add(node.value)
        elif isinstance(node.ctx, cst.Store):
            self.defined.add(node.value)
```

LibCST allows for more accurate code parsing and modification while preserving comments and formatting.

### 3. Static Type Analysis with mypy or pytype

Incorporate type information for more accurate import suggestions:

```python
from mypy import api as mypy_api

def analyze_types(file_path):
    """Analyze a file for type information to improve import suggestions."""
    result = mypy_api.run(['--json-report', 'type-report.json', file_path])

    # Parse the JSON report
    import json
    with open('type-report.json', 'r') as f:
        type_info = json.load(f)

    # Extract type information that can help with imports
    return type_info
```

Type information helps determine what modules should be imported based on type annotations.

### 4. Code Understanding with Sourcery

Sourcery provides deep code understanding capabilities:

```python
import sourcery

def analyze_with_sourcery(source_code):
    """Use Sourcery's code understanding to improve import suggestions."""
    client = sourcery.Sourcery()
    result = client.review(source_code, 'file.py')

    # Extract insights from Sourcery's analysis
    insights = []
    for suggestion in result.suggestions:
        if suggestion.code_after:
            # Look for import-related suggestions
            if 'import' in suggestion.code_after and 'import' not in suggestion.code_before:
                insights.append({
                    'description': suggestion.description,
                    'suggested_import': suggestion.code_after
                })

    return insights
```

## Mathematical Approaches

### 1. Graph Theory with NetworkX

Enhance your dependency graph with more sophisticated algorithms:

```python
import networkx as nx
import community as community_louvain

def enhance_dependency_graph(graph):
    """Apply advanced graph algorithms to improve import understanding."""
    # Calculate centrality measures to identify important modules
    centrality = nx.betweenness_centrality(graph)

    # Community detection to find related modules
    partition = community_louvain.best_partition(graph.to_undirected())

    # Calculate shortest paths for optimal import paths
    shortest_paths = dict(nx.all_pairs_shortest_path_length(graph))

    # Calculate graph density to identify overly coupled code
    density = nx.density(graph)

    return {
        'centrality': centrality,
        'communities': partition,
        'shortest_paths': shortest_paths,
        'density': density
    }
```

This uses graph theory to identify important modules, related code groups, and optimal import paths.

### 2. Vector Embeddings with numpy

Create vector representations of code to find similar patterns:

```python
import numpy as np
from sklearn.decomposition import TruncatedSVD

def create_code_embeddings(code_segments):
    """Create vector embeddings of code segments for similarity analysis."""
    # Create a matrix of code features
    feature_matrix = np.zeros((len(code_segments), 1000))  # Example dimension

    # Fill the matrix with extracted features
    for i, code in enumerate(code_segments):
        # Extract features from code
        tokens = tokenize_code(code)
        for j, token in enumerate(tokens[:1000]):
            feature_matrix[i, j] = token_to_id(token)

    # Reduce dimensionality
    svd = TruncatedSVD(n_components=50)
    embeddings = svd.fit_transform(feature_matrix)

    return embeddings
```

Vector embeddings allow you to represent code in a mathematical space where similar code patterns have similar vectors.

### 3. Bayesian Inference for Import Confidence

Use Bayesian methods to estimate confidence in import suggestions:

```python
import numpy as np
from scipy import stats

class BayesianImportConfidence:
    def __init__(self):
        # Prior probabilities for import correctness
        self.prior_alpha = 2  # Correct examples
        self.prior_beta = 1   # Incorrect examples

    def update_confidence(self, suggestions, feedback):
        """Update confidence scores based on feedback."""
        for import_stmt, was_correct in feedback.items():
            if import_stmt in suggestions:
                # Update the beta distribution parameters
                if was_correct:
                    self.prior_alpha += 1
                else:
                    self.prior_beta += 1

    def get_confidence(self, suggestion, code_context):
        """Get the confidence score for a suggestion in a given context."""
        # Compute probability from beta distribution
        return stats.beta.mean(self.prior_alpha, self.prior_beta)

    def sample_suggestions(self, suggestions, n_samples=10):
        """Use Thompson sampling to select imports to suggest."""
        samples = np.random.beta(self.prior_alpha, self.prior_beta, size=(len(suggestions), n_samples))
        mean_samples = np.mean(samples, axis=1)

        # Sort suggestions by sampled value
        sorted_idx = np.argsort(-mean_samples)
        return [suggestions[i] for i in sorted_idx]
```

This approach quantifies the uncertainty in import suggestions and improves over time with feedback.

## Advanced Import Tracking Techniques

### 1. Git Integration for Historical Analysis

Track how imports evolve over time using Git history:

```python
import git
import os

def analyze_import_history(repo_path, file_path):
    """Analyze how imports have evolved over the file's history."""
    repo = git.Repo(repo_path)
    relative_path = os.path.relpath(file_path, repo_path)

    import_history = []
    for commit in repo.iter_commits(paths=relative_path, max_count=50):
        try:
            # Get the file content at this commit
            blob = commit.tree / relative_path
            content = blob.data_stream.read().decode('utf-8')

            # Extract imports
            imports = extract_imports_from_content(content)

            import_history.append({
                'commit': commit.hexsha,
                'date': commit.committed_datetime,
                'author': commit.author.name,
                'imports': imports
            })
        except:
            # File might not exist in this commit
            pass

    return import_history
```

This allows you to see how imports have changed over time and identify patterns or regressions.

### 2. Import Usage Tracking

Track where and how imported symbols are actually used:

```python
class ImportUsageTracker(ast.NodeVisitor):
    def __init__(self):
        self.imports = {}  # Map from alias to import info
        self.usages = {}   # Map from alias to usage information

    def visit_Import(self, node):
        for name in node.names:
            alias = name.asname or name.name
            self.imports[alias] = {
                'type': 'import',
                'module': name.name,
                'lineno': node.lineno
            }
            self.usages[alias] = []

    def visit_ImportFrom(self, node):
        module = node.module or ""
        for name in node.names:
            alias = name.asname or name.name
            self.imports[alias] = {
                'type': 'from',
                'module': module,
                'name': name.name,
                'lineno': node.lineno
            }
            self.usages[alias] = []

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id in self.imports:
            self.usages[node.id].append({
                'lineno': node.lineno,
                'col_offset': node.col_offset,
                'context': self._get_context(node)
            })

    def _get_context(self, node):
        """Get the surrounding context of a node usage."""
        # This would extract the function/class/etc where the import is used
        return "context extraction placeholder"
```

This tracks not just what's imported, but where and how it's used, which helps with refactoring.

### 3. Dependency Impact Analysis

Analyze the impact of changing imports on the codebase:

```python
def analyze_import_impact(codebase_graph, import_to_change):
    """Analyze the impact of changing an import on the codebase."""
    # Find all nodes that depend on this import
    dependent_nodes = set()
    import_node = f"import:{import_to_change}"

    if import_node in codebase_graph:
        # Direct dependents
        dependent_nodes.update(codebase_graph.successors(import_node))

        # Indirect dependents (transitive closure)
        for node in list(dependent_nodes):
            dependent_nodes.update(nx.descendants(codebase_graph, node))

    # Analyze risk level based on:
    # 1. Number of dependent files
    # 2. Centrality of dependent files
    # 3. Test coverage of dependent files

    risk_level = len(dependent_nodes) * calculate_centrality_factor(codebase_graph, dependent_nodes)

    return {
        'dependent_files': list(dependent_nodes),
        'risk_level': risk_level,
        'suggested_testing_strategy': generate_testing_strategy(dependent_nodes)
    }
```

This helps you understand the potential impact of changing imports before making changes.

## Comprehensive Enhancement Strategy

To create a truly advanced import management system, integrate these components in this order:

1. **Core Analysis Improvements**:

   - Add LibCST for better AST handling
   - Integrate Jedi for intelligent completion
   - Add mypy/pytype for type-aware import suggestions

2. **Mathematical Enhancements**:

   - Enhance the dependency graph with NetworkX algorithms
   - Add Bayesian confidence scoring for import suggestions
   - Implement vector embeddings for code similarity

3. **Machine Learning Integration**:

   - Train an ML model on your codebase's import patterns
   - Use the model to provide ranked import suggestions
   - Implement feedback loops to improve over time

4. **Advanced Tracking**:
   - Add Git history analysis for temporal patterns
   - Implement detailed usage tracking
   - Add impact analysis for import changes

This comprehensive approach combines the strengths of multiple techniques to create an extremely powerful import management system that not only fixes imports but helps understand and optimize the import structure across your entire codebase.

The result will be far more than a simple import fixer—it will be a tool that provides deep insights into your code's dependency structure and helps maintain a clean, efficient import ecosystem in your project.

```python
class SymbolDependencyGraph:
    def __init__(self, project_root):
        self.project_root = project_root
        self.dependency_graph = nx.DiGraph()
        self.symbol_to_module = {}
        self.module_to_symbols = defaultdict(set)

    def analyze_project(self):
        """Build complete symbol-level dependency graph for the entire project."""
        for file_path in find_python_files(self.project_root):
            self._process_file(file_path)

        # Run transitive reduction to optimize the graph
        self.dependency_graph = nx.transitive_reduction(self.dependency_graph)

    def _process_file(self, file_path):
        """Process a single file to extract defined symbols and dependencies."""
        with open(file_path, 'r') as f:
            code = f.read()

        module_name = file_path_to_module_name(file_path, self.project_root)
        tree = ast.parse(code)

        # Extract defined symbols
        defined_symbols = self._extract_defined_symbols(tree, module_name)

        # Extract symbol references and build dependency edges
        self._extract_symbol_references(tree, module_name, defined_symbols)

    def find_optimal_import_path(self, target_file, symbol_name):
        """Find the optimal module to import a symbol from using graph algorithms."""
        if symbol_name not in self.symbol_to_module:
            return None

        possible_sources = self.symbol_to_module[symbol_name]
        target_module = file_path_to_module_name(target_file, self.project_root)

        best_path = None
        min_distance = float('inf')

        # Find the import path that minimizes coupling and maximizes cohesion
        for source_module in possible_sources:
            # Skip circular imports
            path_exists = nx.has_path(self.dependency_graph, source_module, target_module)
            if path_exists:
                continue

            # Calculate coupling metric
            coupling_metric = self._calculate_coupling_metric(source_module, target_module)

            # Calculate cohesion metric
            cohesion_metric = self._calculate_cohesion_metric(source_module, target_module)

            # Combined distance (lower is better)
            distance = coupling_metric - cohesion_metric

            if distance < min_distance:
                min_distance = distance
                best_path = source_module

        return best_path



import symexec

class DynamicImportTracer:
    def __init__(self):
        self.symbolic_engine = symexec.Engine()
        self.dynamic_imports = {}

    def trace_dynamic_imports(self, file_path):
        """Trace dynamic imports that might be missed by static analysis."""
        # Set up tracing for __import__, importlib functions, etc.
        self.symbolic_engine.hook_function('__import__', self._import_callback)
        self.symbolic_engine.hook_function('importlib.import_module', self._import_callback)

        # Execute the file symbolically
        self.symbolic_engine.execute_file(file_path)

        return self.dynamic_imports

    def _import_callback(self, args, execution_context):
        """Callback for import function calls."""
        import_name = args[0].concrete_value

        # Get call site information
        callsite = execution_context.get_current_location()

        # Record the dynamic import
        self.dynamic_imports[import_name] = {
            'location': callsite,
            'conditional_path': execution_context.get_path_constraints(),
            'variable_state': execution_context.get_variable_state()
        }

class ImportLocalityOptimizer:
    def __init__(self, codebase_graph):
        self.codebase_graph = codebase_graph
        self.import_heat_map = {}

    def build_heat_map(self):
        """Build a heat map of import usage throughout the codebase."""
        # For each module
        for module_node in self.codebase_graph.nodes():
            if not isinstance(module_node, str) or not module_node.endswith('.py'):
                continue

            # Get all symbols imported in this module
            imports = self._get_module_imports(module_node)

            # Get all symbols used in this module
            usage_map = self._get_symbol_usage_map(module_node)

            # Calculate heat (usage density) for each import
            for import_name, import_info in imports.items():
                if import_name not in self.import_heat_map:
                    self.import_heat_map[import_name] = {}

                # Calculate the heat as a function of:
                # 1. Number of usages
                # 2. Locality of usages (how concentrated they are)
                # 3. Distance from import statement

                usage_count = len(usage_map.get(import_name, []))
                if usage_count == 0:
                    # Unused import
                    heat = 0
                else:
                    # Calculate locality metrics
                    line_numbers = [usage['line'] for usage in usage_map.get(import_name, [])]
                    import_line = import_info['line']

                    # Locality is inversely proportional to standard deviation of usage
                    locality = 1.0 / (np.std(line_numbers) + 1.0)

                    # Distance from import statement
                    avg_distance = np.mean([abs(line - import_line) for line in line_numbers])
                    distance_factor = 1.0 / (avg_distance + 1.0)

                    # Combined heat metric
                    heat = usage_count * locality * distance_factor

                self.import_heat_map[import_name][module_node] = heat

    def recommend_import_reorganization(self, module_path):
        """Recommend import reorganization to optimize locality."""
        # Get current imports
        current_imports = self._get_module_imports(module_path)

        # Get symbol usages
        usage_map = self._get_symbol_usage_map(module_path)

        # Group imports by usage patterns
        groups = self._cluster_imports_by_usage_pattern(current_imports, usage_map)

        # Generate recommended ordering
        recommendations = []
        for group in groups:
            recommendations.append({
                'imports': group,
                'placement': self._recommend_placement(group, usage_map),
                'reason': self._explain_grouping(group, usage_map)
            })

        return recommendations


class ImportProfiler:
    def __init__(self):
        self.import_times = {}
        self.import_stacks = {}
        self.original_import = __import__

    def install(self):
        """Install the import profiler."""
        import builtins
        import time
        import traceback

        def profiled_import(*args, **kwargs):
            module_name = args[0]
            start_time = time.time()

            # Get the call stack
            stack = traceback.extract_stack()
            caller = stack[-2]  # The frame that called __import__

            try:
                result = self.original_import(*args, **kwargs)

                # Record import time
                end_time = time.time()
                import_time = end_time - start_time

                if module_name not in self.import_times:
                    self.import_times[module_name] = []
                    self.import_stacks[module_name] = []

                self.import_times[module_name].append(import_time)
                self.import_stacks[module_name].append(caller)

                return result
            except Exception as e:
                # Record failed imports too
                if module_name not in self.import_times:
                    self.import_times[module_name] = []
                    self.import_stacks[module_name] = []

                self.import_times[module_name].append(None)  # None indicates failure
                self.import_stacks[module_name].append(caller)

                raise

        builtins.__import__ = profiled_import

    def uninstall(self):
        """Uninstall the import profiler."""
        import builtins
        builtins.__import__ = self.original_import

    def analyze_results(self):
        """Analyze the import profiling results."""
        import statistics

        results = {}

        for module_name, times in self.import_times.items():
            successful_times = [t for t in times if t is not None]
            failure_count = times.count(None)

            if successful_times:
                avg_time = statistics.mean(successful_times)
                max_time = max(successful_times)
                min_time = min(successful_times)

                # Identify slow imports
                is_slow = avg_time > 0.1  # 100ms threshold

                # Identify frequently imported modules
                frequency = len(times)

                # Identify import chains
                import_chains = self._identify_import_chains(module_name)

                results[module_name] = {
                    'avg_time': avg_time,
                    'max_time': max_time,
                    'min_time': min_time,
                    'frequency': frequency,
                    'failures': failure_count,
                    'is_slow': is_slow,
                    'callers': self._analyze_callers(module_name),
                    'import_chains': import_chains
                }

        return results

class SymbolicImportOptimizer:
    def __init__(self, codebase_graph):
        self.codebase_graph = codebase_graph
        self.symbol_table = {}
        self.module_dependencies = {}

    def build_symbolic_model(self):
        """Build a symbolic mathematical model of the codebase's import structure."""
        import sympy as sp

        # Create variables representing each module's import cost
        for module in self.get_all_modules():
            self.symbol_table[module] = sp.Symbol(f"cost_{module}")

        # Define the cost function based on:
        # 1. Module size & complexity (bigger = higher cost)
        # 2. Import depth (deeper imports = higher cost)
        # 3. Number of dependent modules (more dependents = higher cost)

        cost_expressions = {}

        for module in self.get_all_modules():
            # Calculate base cost from module complexity
            size_factor = self.calculate_module_size_factor(module)
            complexity_factor = self.calculate_module_complexity(module)
            base_cost = size_factor * complexity_factor

            # Add dependency costs
            dependencies = self.get_module_dependencies(module)
            dependency_expr = sum(self.symbol_table[dep] for dep in dependencies)

            # Final cost expression
            cost_expressions[module] = base_cost + dependency_expr / len(dependencies) if dependencies else base_cost

        # Set up equations for optimization
        equations = []
        for module, expr in cost_expressions.items():
            equations.append(sp.Eq(self.symbol_table[module], expr))

        # Solve the system of equations
        solution = sp.solve(equations, list(self.symbol_table.values()))

        return solution

    def recommend_import_strategy(self):
        """Generate optimal import strategy based on symbolic model."""
        solution = self.build_symbolic_model()

        # Convert symbolic solution to concrete recommendations
        recommendations = {}

        for module in self.get_all_modules():
            # Calculate import budget based on module's role
            import_budget = self.calculate_import_budget(module)

            # Identify essential vs. optional imports
            essential_imports = self.identify_essential_imports(module)
            optional_imports = self.identify_optional_imports(module)

            # Prioritize imports within budget based on symbolic costs
            prioritized_imports = self.prioritize_imports(module, essential_imports, optional_imports, solution)

            # Generate refactoring recommendations
            recommendations[module] = {
                'keep_imports': prioritized_imports[:import_budget],
                'refactor_imports': prioritized_imports[import_budget:],
                'refactoring_strategy': self.generate_refactoring_strategy(module, prioritized_imports[import_budget:])
            }

        return recommendations



class ImportPathCompressor:
    def __init__(self, project_root):
        self.project_root = project_root
        self.module_map = {}
        self.symbol_map = {}
        self.compressed_paths = {}

    def analyze_project(self):
        """Build comprehensive module and symbol maps."""
        for file_path in find_python_files(self.project_root):
            module_name = file_path_to_module_name(file_path, self.project_root)

            with open(file_path, 'r') as f:
                code = f.read()

            tree = ast.parse(code)

            # Map symbols defined in this module
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    symbol_name = node.name

                    if symbol_name not in self.symbol_map:
                        self.symbol_map[symbol_name] = []

                    self.symbol_map[symbol_name].append({
                        'module': module_name,
                        'line': node.lineno,
                        'type': type(node).__name__
                    })

            # Store module information
            self.module_map[module_name] = {
                'file_path': file_path,
                'symbols': [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
            }

    def compute_compression_paths(self):
        """Compute optimal compressed import paths."""
        # Build a graph of import relationships
        import_graph = nx.DiGraph()

        for symbol, locations in self.symbol_map.items():
            for location in locations:
                import_graph.add_node(location['module'])

        # Add edges for every import relationship
        for module_name, module_info in self.module_map.items():
            with open(module_info['file_path'], 'r') as f:
                code = f.read()

            tree = ast.parse(code)

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if name.name in self.module_map:
                            import_graph.add_edge(module_name, name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self.module_map:
                        import_graph.add_edge(module_name, node.module)

        # Compute strongly connected components for cycle detection
        sccs = list(nx.strongly_connected_components(import_graph))

        # Perform topological compression
        for scc in sccs:
            if len(scc) > 1:
                # Found a cycle, need to break it
                self._compress_cycle(scc, import_graph)
            else:
                # Single module, compress its paths
                module = list(scc)[0]
                self._compress_module_paths(module, import_graph)

        return self.compressed_paths

    def _compress_cycle(self, cycle_modules, graph):
        """Break import cycles by refactoring imports."""
        # Identify the best module to act as a broker
        centrality = nx.betweenness_centrality(graph.subgraph(cycle_modules))
        broker_module = max(centrality.items(), key=lambda x: x[1])[0]

        # Create a new intermediate module if needed
        if all(c > 0.2 for c in centrality.values()):
            # All modules are too interconnected, create a new broker module
            broker_module = self._create_broker_module(cycle_modules)

        # For each module in the cycle
        for module in cycle_modules:
            if module == broker_module:
                continue

            # Redirect imports through the broker
            self.compressed_paths[module] = {
                'cycle_broken': True,
                'broker_module': broker_module,
                'original_imports': self._get_module_imports(module),
                'compressed_imports': [{'module': broker_module, 'symbols': '*'}]
            }

    def _compress_module_paths(self, module, graph):
        """Compress import paths for a single module."""
        # Get current imports
        current_imports = self._get_module_imports(module)

        # Get transitive dependencies
        dependencies = list(nx.descendants(graph, module))

        # Group imports by common parent modules
        compressed_imports = []

        # Build a prefix tree of import paths
        prefix_tree = {}

        for imp in current_imports:
            parts = imp['module'].split('.')

            current_dict = prefix_tree
            for part in parts:
                if part not in current_dict:
                    current_dict[part] = {}
                current_dict = current_dict[part]

            # Mark this path as having symbols
            current_dict['__symbols__'] = imp.get('symbols', [])

        # Compress the prefix tree
        compressed_imports = self._compress_prefix_tree(prefix_tree)

        # Store the compressed paths
        self.compressed_paths[module] = {
            'cycle_broken': False,
            'original_imports': current_imports,
            'compressed_imports': compressed_imports
        }
```
