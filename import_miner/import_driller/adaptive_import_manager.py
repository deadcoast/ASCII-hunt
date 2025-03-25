import os
from collections import Counter
from typing import Any

import numpy as np
from sklearn.cluster import KMeans


class AdaptiveImportManager:
    def __init__(self, project_root):
        self.project_root = project_root
        self.codebase_model = self._build_codebase_model()
        self.import_patterns = self._extract_import_patterns()
        self.correction_strategies = self._develop_correction_strategies()
        self.watcher = self._setup_file_watcher()

    def _build_codebase_model(self):
        """Build a comprehensive model of the codebase structure."""
        # Analyze project structure recursively
        codebase = {
            "modules": {},
            "symbols": {},
            "imports": {},
            "patterns": {},
            "architecture": self._infer_project_architecture(),
        }

        # Populate the model by scanning every Python file
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._analyze_file_for_model(file_path, codebase)

        # Apply graph algorithms to detect patterns and hierarchies
        self._apply_graph_analysis(codebase)

        return codebase

    def _infer_project_architecture(self):
        """Infer the architectural style of the project."""
        # Check for common architectural patterns
        patterns = []

        # Check for Django-style project
        if os.path.exists(os.path.join(self.project_root, "manage.py")):
            patterns.append("django")

        # Check for Flask-style project
        if self._find_files_with_content("from flask import Flask"):
            patterns.append("flask")

        # Check for typical data science project
        if self._find_files_with_content(
            "import pandas"
        ) or self._find_files_with_content("import numpy"):
            patterns.append("data-science")

        # Check for typical test-driven project
        if len(self._find_files_with_prefix("test_")) > 10:
            patterns.append("test-driven")

        # Determine the primary architecture based on patterns
        if "django" in patterns:
            return "django-web"
        elif "flask" in patterns:
            return "flask-web"
        elif "data-science" in patterns:
            return "data-science"
        elif "test-driven" in patterns:
            return "modular-with-tests"
        else:
            # Apply more sophisticated heuristics for unknown architecture
            return self._apply_architectural_clustering()

    def _apply_architectural_clustering(self):
        """Apply unsupervised learning to cluster files and infer architecture."""
        # Collect features from files
        features = []
        file_paths = []

        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    file_features = self._extract_architectural_features(file_path)
                    features.append(file_features)
                    file_paths.append(file_path)

        if not features:
            return "unknown"

        # Apply clustering
        X = np.array(features)
        kmeans = KMeans(n_clusters=min(5, len(features)))
        kmeans.fit(X)

        # Analyze clusters to infer architecture
        clusters = {}
        if kmeans.labels_ is not None:
            for i, label in enumerate(kmeans.labels_):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(file_paths[i])

        # Determine architecture based on cluster patterns
        # This is a simplified version - a real implementation would be more sophisticated
        if len(clusters) == 1:
            return "monolithic"
        elif len(clusters) >= 3:
            return "microservices"
        else:
            return "modular"

    def _extract_import_patterns(self):
        """Extract common import patterns from the codebase."""
        patterns = {
            "module_patterns": {},
            "symbol_patterns": {},
            "import_groups": {},
            "style_conventions": self._infer_style_conventions(),
        }

        # Analyze import frequencies
        for module_name, module_info in self.codebase_model["modules"].items():
            # Track the most common imports for each module
            imports_count = {}
            for imp in module_info.get("imports", []):
                import_key = f"{imp['type']}:{imp['module']}"
                imports_count[import_key] = imports_count.get(import_key, 0) + 1

            # Identify consistent import patterns
            if imports_count:
                common_imports = sorted(
                    imports_count.items(), key=lambda x: x[1], reverse=True
                )
                patterns["module_patterns"][module_name] = common_imports[
                    :10
                ]  # Top 10 imports

        # Identify import groups (imports that typically appear together)
        import_co_occurrence = {}
        for module_info in self.codebase_model["modules"].values():
            module_imports = set()
            for imp in module_info.get("imports", []):
                import_key = f"{imp['type']}:{imp['module']}"
                module_imports.add(import_key)

            # Update co-occurrence matrix
            for imp1 in module_imports:
                if imp1 not in import_co_occurrence:
                    import_co_occurrence[imp1] = {}

                for imp2 in module_imports:
                    if imp1 != imp2:
                        if imp2 not in import_co_occurrence[imp1]:
                            import_co_occurrence[imp1][imp2] = 0
                        import_co_occurrence[imp1][imp2] += 1

        # Identify groups of imports that commonly appear together
        # using a clustering algorithm
        import_groups = self._cluster_imports_by_co_occurrence(import_co_occurrence)
        patterns["import_groups"] = import_groups

        return patterns

    def _infer_style_conventions(self):
        """Infer the style conventions used in the project."""
        conventions: dict[str, Any] = {
            "import_order": None,
            "import_grouping": None,
            "line_breaks": None,
            "max_line_length": None,
        }

        # Analyze a sample of files to determine conventions
        file_sample = self._get_representative_files(20)  # 20 representative files

        import_orders = []
        line_breaks = []
        line_lengths = []

        for file_path in file_sample:
            with open(file_path) as f:
                content = f.read()

            # Extract import blocks
            import_blocks = self._extract_import_blocks(content)

            if import_blocks:
                # Analyze import order
                file_import_order = self._analyze_import_order(import_blocks)
                import_orders.append(file_import_order)

                # Analyze import grouping and line breaks
                line_break_pattern = self._analyze_line_breaks(import_blocks)
                line_breaks.append(line_break_pattern)

            # Analyze max line length
            lines = content.split("\n")
            if lines:
                max_length = max(len(line) for line in lines)
                line_lengths.append(max_length)

        # Determine the most common conventions
        if import_orders:
            order_counter = Counter(tuple(order) for order in import_orders if order)
            if order_counter:
                # Create a new list to avoid modifying a tuple
                most_common_order = list(order_counter.most_common(1)[0][0])
                conventions["import_order"] = most_common_order

        if line_breaks:
            break_counter = Counter(
                tuple(pattern) for pattern in line_breaks if pattern
            )
            if break_counter:
                # Create a new list to avoid modifying a tuple
                most_common_breaks = list(break_counter.most_common(1)[0][0])
                conventions["line_breaks"] = most_common_breaks

        if line_lengths:
            # Use 90th percentile to avoid outliers
            conventions["max_line_length"] = int(np.percentile(line_lengths, 90))

        return conventions

    def _develop_correction_strategies(self):
        """Develop strategies for correcting import issues based on the codebase model."""
        strategies = {
            "missing_imports": self._strategy_for_missing_imports(),
            "unused_imports": self._strategy_for_unused_imports(),
            "order_issues": self._strategy_for_order_issues(),
            "style_issues": self._strategy_for_style_issues(),
        }
        return strategies

    def _setup_file_watcher(self):
        """Set up a file watcher to monitor changes in the project files."""
        # This would typically use a library like watchdog
        # For this prototype, we'll return a simple placeholder
        watcher = {"active": False, "paths": [self.project_root]}
        return watcher

    def _analyze_file_for_model(self, file_path, codebase):
        """Analyze a Python file and update the codebase model with the findings."""
        try:
            with open(file_path) as f:
                content = f.read()

            # Extract module path relative to project root
            rel_path = os.path.relpath(file_path, self.project_root)
            module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, ".")

            # Parse imports and other code elements
            imports = self._extract_imports(content)
            symbols = self._extract_symbols(content)

            # Update codebase model
            if module_path not in codebase["modules"]:
                codebase["modules"][module_path] = {}

            codebase["modules"][module_path] = {
                "path": file_path,
                "imports": imports,
                "symbols": symbols,
                "modified": os.path.getmtime(file_path),
            }

            # Update symbols registry
            for symbol in symbols:
                if symbol not in codebase["symbols"]:
                    codebase["symbols"][symbol] = []
                codebase["symbols"][symbol].append(module_path)

        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")

    def _apply_graph_analysis(self, codebase):
        """Apply graph analysis algorithms to identify patterns and hierarchies."""
        import networkx as nx

        # Create a directed graph of module dependencies
        G = nx.DiGraph()

        # Add nodes for each module
        for module in codebase["modules"]:
            G.add_node(module)

        # Add edges for imports
        for module, module_info in codebase["modules"].items():
            for imp in module_info.get("imports", []):
                if imp["module"] in codebase["modules"]:
                    G.add_edge(module, imp["module"])

        # Analyze the graph
        codebase["graph_metrics"] = {
            "centrality": nx.degree_centrality(G),
            "cycles": list(nx.simple_cycles(G)),
            "communities": self._detect_communities(G),
            "hierarchy_levels": self._calculate_hierarchy_levels(G),
        }

    def _extract_imports(self, content):
        """Extract import statements from Python code."""
        import ast

        imports = []

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(
                            {
                                "type": "import",
                                "module": name.name,
                                "alias": name.asname,
                                "lineno": node.lineno,
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
                                "lineno": node.lineno,
                            }
                        )
        except SyntaxError:
            # Handle files with syntax errors
            pass

        return imports

    def _extract_symbols(self, content):
        """Extract defined symbols from Python code."""
        import ast

        symbols = []

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    symbols.append(
                        {"type": "class", "name": node.name, "lineno": node.lineno}
                    )
                elif isinstance(node, ast.FunctionDef):
                    symbols.append(
                        {"type": "function", "name": node.name, "lineno": node.lineno}
                    )
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            symbols.append(
                                {
                                    "type": "variable",
                                    "name": target.id,
                                    "lineno": node.lineno,
                                }
                            )
        except SyntaxError:
            # Handle files with syntax errors
            pass

        return symbols

    def _find_files_with_content(self, content_pattern):
        """Find files that contain the specified content pattern."""
        matching_files = []

        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path) as f:
                            content = f.read()
                            if content_pattern in content:
                                matching_files.append(file_path)
                    except Exception:
                        # Skip files that can't be read
                        pass

        return matching_files

    def _find_files_with_prefix(self, prefix):
        """Find files that have the specified filename prefix."""
        matching_files = []

        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.startswith(prefix) and file.endswith(".py"):
                    matching_files.append(os.path.join(root, file))

        return matching_files

    def _extract_architectural_features(self, file_path):
        """Extract features from a file that can help determine architectural patterns."""
        features: list[int | float] = [0] * 10  # Initialize feature vector

        try:
            with open(file_path) as f:
                content = f.read()

            # Feature 1: File size
            features[0] = float(len(content) / 1000)  # Normalize by 1000

            # Feature 2: Number of imports
            imports = self._extract_imports(content)
            features[1] = len(imports)

            # Feature 3: Number of classes
            features[2] = len(
                [s for s in self._extract_symbols(content) if s["type"] == "class"]
            )

            # Feature 4: Number of functions
            features[3] = len(
                [s for s in self._extract_symbols(content) if s["type"] == "function"]
            )

            # Feature 5: Ratio of classes to functions
            if features[3] > 0:
                features[4] = float(features[2] / features[3])

            # Feature 6: Presence of specific frameworks
            if "import django" in content or "from django" in content:
                features[5] = 1
            if "import flask" in content or "from flask" in content:
                features[6] = 1
            if "import pandas" in content or "import numpy" in content:
                features[7] = 1

            # Feature 7: File path depth
            rel_path = os.path.relpath(file_path, self.project_root)
            features[8] = len(rel_path.split(os.path.sep))

            # Feature 8: Test file indicator
            if "test_" in os.path.basename(file_path) or "_test" in os.path.basename(
                file_path
            ):
                features[9] = 1

        except Exception:
            # Return default features if extraction fails
            pass

        return features

    def _detect_communities(self, graph):
        """Detect communities in the module dependency graph."""
        import networkx as nx

        try:
            # Use NetworkX's built-in community detection methods
            # First try the newer community module if available
            try:
                from networkx.algorithms import community as nx_community

                communities = nx_community.greedy_modularity_communities(
                    graph.to_undirected()
                )

                # Convert to the expected format (node -> community_id dictionary)
                result = {}
                for i, community in enumerate(communities):
                    for node in community:
                        result[node] = i
                return result
            except (ImportError, AttributeError):
                # Fallback to connected components as a simpler form of community detection
                communities = {}
                for i, component in enumerate(
                    nx.connected_components(graph.to_undirected())
                ):
                    for node in component:
                        communities[node] = i
                return communities
        except Exception:
            # Ultimate fallback for any unexpected errors
            communities = {}
            for i, node in enumerate(graph.nodes()):
                communities[node] = i % 3  # Simple grouping into 3 communities
            return communities

    def _calculate_hierarchy_levels(self, graph):
        """Calculate the hierarchy level of each module in the dependency graph."""
        levels = {}
        visited = set()

        def visit(node, level=0):
            if node in visited:
                return
            visited.add(node)
            levels[node] = max(levels.get(node, 0), level)
            for neighbor in graph.successors(node):
                visit(neighbor, level + 1)

        for node in graph.nodes():
            if node not in visited:
                visit(node)

        return levels

    def _cluster_imports_by_co_occurrence(self, co_occurrence):
        """Cluster imports that commonly occur together."""
        import networkx as nx

        # Create a graph of co-occurring imports
        G = nx.Graph()

        # Add nodes for each import
        for imp in co_occurrence:
            G.add_node(imp)

        # Add edges with weights based on co-occurrence frequency
        for imp1, co_imps in co_occurrence.items():
            for imp2, frequency in co_imps.items():
                if frequency > 1:  # Only consider imports that co-occur multiple times
                    G.add_edge(imp1, imp2, weight=frequency)

        # Detect communities to find groups of imports
        partition = {}
        try:
            # Use NetworkX's built-in community detection methods
            try:
                from networkx.algorithms import community as nx_community

                communities = nx_community.greedy_modularity_communities(G)

                # Convert to the expected format (node -> community_id dictionary)
                for i, community in enumerate(communities):
                    for node in community:
                        partition[node] = i
            except (ImportError, AttributeError):
                # Fallback to connected components
                for i, component in enumerate(nx.connected_components(G)):
                    for node in component:
                        partition[node] = i
        except Exception:
            # Ultimate fallback for any unexpected errors
            for i, component in enumerate(nx.connected_components(G)):
                for node in component:
                    partition[node] = i

        # Organize imports by community
        groups = {}
        for imp, group_id in partition.items():
            if group_id not in groups:
                groups[group_id] = []
            groups[group_id].append(imp)

        return groups

    def _get_representative_files(self, num_files=20):
        """Get a representative sample of files from the codebase."""
        # Try to select files from different modules and with different characteristics
        files = []
        module_seen = set()

        # First pass: try to get files from different modules
        for module, info in self.codebase_model["modules"].items():
            if len(files) >= num_files:
                break

            # Skip if we've already seen a file from this module group
            module_prefix = module.split(".")[0]
            if module_prefix in module_seen:
                continue

            files.append(info["path"])
            module_seen.add(module_prefix)

        # Second pass: add more files if needed
        if len(files) < num_files:
            remaining = num_files - len(files)
            # Get files from the most central modules
            centrality = self.codebase_model.get("graph_metrics", {}).get(
                "centrality", {}
            )
            if centrality:
                central_modules = sorted(
                    centrality.items(), key=lambda x: x[1], reverse=True
                )
                for module, _ in central_modules:
                    if len(files) >= num_files:
                        break
                    path = self.codebase_model["modules"].get(module, {}).get("path")
                    if path and path not in files:
                        files.append(path)

        return files[:num_files]  # Ensure we don't return more than requested

    def _extract_import_blocks(self, content):
        """Extract blocks of import statements from code."""
        import re

        # Regular expression to match import statements
        import_re = r"^\s*(import|from)\s+.+$"

        lines = content.split("\n")
        blocks = []
        current_block = []
        in_block = False

        for line in lines:
            if re.match(import_re, line):
                if not in_block:
                    in_block = True
                    current_block = []
                current_block.append(line)
            elif in_block:
                if line.strip() == "":
                    # Empty line might be separating import blocks
                    continue
                else:
                    # Non-empty, non-import line ends the block
                    if current_block:
                        blocks.append(current_block)
                    in_block = False
                    current_block = []

        # Don't forget the last block
        if current_block:
            blocks.append(current_block)

        return blocks

    def _analyze_import_order(self, import_blocks):
        """Analyze the order of imports within each block."""
        import re

        order = []

        for block in import_blocks:
            block_type = None
            current_type = None  # Initialize current_type to avoid UnboundLocalError

            for line in block:
                if line.startswith("import"):
                    if re.match(r"import\s+[_a-zA-Z][_a-zA-Z0-9]*\s*$", line):
                        # Standard library import
                        current_type = "stdlib"
                    else:
                        # Third-party or local import
                        current_type = "thirdparty"
                elif line.startswith("from"):
                    if re.match(r"from\s+[_a-zA-Z][_a-zA-Z0-9]*\s+import", line):
                        # Standard library import
                        current_type = "stdlib_from"
                    elif re.match(r"from\s+[.]\s+import", line):
                        # Relative import
                        current_type = "relative"
                    else:
                        # Third-party or local import
                        current_type = "thirdparty_from"

                if block_type is None and current_type is not None:
                    block_type = current_type
                    order.append(current_type)
                elif current_type is not None and current_type != block_type:
                    order.append(current_type)
                    block_type = current_type

        return order

    def _analyze_line_breaks(self, import_blocks):
        """Analyze the pattern of line breaks between import blocks."""
        line_breaks = []

        if len(import_blocks) <= 1:
            return None

        # Count empty lines between blocks in the original code
        # This would require having the original line numbers of each import
        # For this prototype, we'll return a constant pattern
        for _ in range(len(import_blocks) - 1):
            line_breaks.append(1)  # Assume 1 blank line between blocks

        return line_breaks

    def _strategy_for_missing_imports(self):
        """Develop a strategy for fixing missing imports."""
        strategy = {"modules": {}, "symbols": {}, "fallbacks": []}

        # Use the codebase model to suggest imports for commonly used symbols
        for symbol, modules in self.codebase_model["symbols"].items():
            if modules:  # If this symbol is defined in one or more modules
                strategy["symbols"][symbol] = modules[
                    0
                ]  # Suggest the first defining module

        return strategy

    def _strategy_for_unused_imports(self):
        """Develop a strategy for fixing unused imports."""
        strategy = {
            "remove_all": False,  # Whether to aggressively remove all unused imports
            "preserve_list": [],  # List of imports to preserve even if unused
            "max_age": 7,  # Max age in days before removing an unused import
        }

        return strategy

    def _strategy_for_order_issues(self):
        """Develop a strategy for fixing import order issues."""
        # Use the inferred style conventions to determine the preferred order
        conventions = self.import_patterns["style_conventions"]

        strategy = {
            "order": conventions.get(
                "import_order",
                ["stdlib", "stdlib_from", "thirdparty", "thirdparty_from", "relative"],
            ),
            "enforce_groups": True,
        }

        return strategy

    def _strategy_for_style_issues(self):
        """Develop a strategy for fixing import style issues."""
        conventions = self.import_patterns["style_conventions"]

        strategy = {
            "line_breaks": conventions.get("line_breaks", [1, 1, 1]),
            "max_line_length": conventions.get("max_line_length", 88),
            "use_parentheses": True,
        }

        return strategy
