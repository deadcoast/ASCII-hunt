import ast
import os

import yaml


class DomainAwareImportAnalyzer:
    def __init__(self, codebase_path, domain_knowledge_base):
        """Initialize the domain-aware import analyzer.

        Args:
            codebase_path: The root directory of the codebase to analyze.
            domain_knowledge_base: The path to a YAML file containing domain-specific
                knowledge about import patterns.
        """
        self.codebase_path = codebase_path
        self.knowledge_base = self._load_knowledge_base(domain_knowledge_base)
        self.module_boundaries = {}

    def _load_knowledge_base(self, path):
        """Load a YAML file containing domain-specific knowledge about import patterns.

        Args:
            path: The path to the YAML file.

        Returns:
            The loaded YAML data as a Python object.
        """
        with open(path) as f:
            return yaml.safe_load(f)

    def analyze_codebase(self):
        """Analyze the codebase and compute module boundaries.

        Walks through the codebase and runs deep contextual analysis on all Python files.
        Then, computes module boundaries by applying domain-specific knowledge from the
        knowledge base to the collected data.

        Returns:
            None
        """
        for root, _, files in os.walk(self.codebase_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._analyze_file(file_path)

        self._compute_module_boundaries()

    def _analyze_file(self, file_path):
        """Analyze a single file and compute its import patterns and code metrics.

        This method parses the abstract syntax tree of a Python file, extracts
        import statements and code metrics, and applies domain-specific knowledge
        to classify the imports. Finally, it adds the results to the module
        boundaries dictionary.

        Args:
            file_path: The path to the file to analyze.

        Returns:
            None
        """
        with open(file_path) as f:
            code = f.read()

        tree = ast.parse(code)

        # Extract import statements
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(
                        {
                            "type": "import",
                            "module": name.name,
                            "alias": name.asname,
                            "line": node.lineno,
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
                            "line": node.lineno,
                        }
                    )

        # Extract code metrics and patterns
        metrics = self._compute_code_metrics(tree)

        # Apply domain knowledge to classify imports
        classified_imports = self._classify_imports_with_domain_knowledge(
            imports, metrics
        )

        self.module_boundaries[file_path] = {
            "imports": classified_imports,
            "metrics": metrics,
        }

    def _compute_code_metrics(self, tree):
        """Compute code metrics for the given AST.

        This method calculates the following code metrics for the given AST:

        - Cyclomatic complexity
        - Class count
        - Function count
        - Line count
        - Patterns (e.g., model, view, controller)
        - Domain markers (e.g., keywords in docstrings)

        The calculated metrics are stored in a dictionary with the following keys:

        - complexity: The cyclomatic complexity of the code.
        - class_count: The number of classes defined in the code.
        - function_count: The number of functions defined in the code.
        - line_count: The number of lines in the code.
        - patterns: A set of patterns found in the code (e.g., model, view, controller).
        - domain_markers: A set of domain markers found in docstrings and comments.

        Returns:
            A dictionary containing the calculated code metrics.
        """
        metrics = {
            "complexity": 0,
            "class_count": 0,
            "function_count": 0,
            "line_count": 0,
            "patterns": set(),
            "domain_markers": set(),
        }

        # Calculate cyclomatic complexity
        for node in ast.walk(tree):
            if isinstance(
                node, (ast.FunctionDef | ast.ClassDef | ast.AsyncFunctionDef)
            ):
                metrics["complexity"] += self._calculate_node_complexity(node)

                if isinstance(node, ast.ClassDef):
                    metrics["class_count"] += 1

                    # Detect class patterns (e.g., is this a model, view, controller?)
                    pattern = self._detect_class_pattern(node)
                    if pattern:
                        metrics["patterns"].add(pattern)

                elif isinstance(node, (ast.FunctionDef | ast.AsyncFunctionDef)):
                    metrics["function_count"] += 1

                    # Detect function patterns
                    pattern = self._detect_function_pattern(node)
                    if pattern:
                        metrics["patterns"].add(pattern)

        # Extract domain markers from docstrings and comments
        docstrings = [
            ast.get_docstring(node)
            for node in ast.walk(tree)
            if isinstance(node, (ast.Module | ast.ClassDef | ast.FunctionDef))
            and ast.get_docstring(node)
        ]

        for docstring in docstrings:
            markers = self._extract_domain_markers(docstring)
            metrics["domain_markers"].update(markers)

        return metrics

    def _classify_imports_with_domain_knowledge(self, imports, metrics):
        """Classify imports using domain knowledge rules.

        Given a list of imports and advanced code metrics, apply domain knowledge rules to
        classify each import as "domain_purpose" and "necessity". Also, detect boundary
        violations and provide a recommendation for each import.

        Args:
            imports: List of imports.
            metrics: Advanced code metrics.

        Returns:
            List of classified imports.
        """
        classified_imports = []

        for imp in imports:
            classification = {
                "import": imp,
                "domain_purpose": "unknown",
                "necessity": "unknown",
                "boundary_violation": False,
                "recommendation": None,
            }

            # Apply domain knowledge rules
            for rule in self.knowledge_base.get("import_rules", []):
                if self._rule_matches(rule, imp, metrics):
                    classification.update(rule.get("classification", {}))
                    break

            classified_imports.append(classification)

        return classified_imports

    def _compute_module_boundaries(self):
        """Compute module boundaries based on analyzed files.

        This method uses the collected information about imports and metrics
        to establish boundaries between modules, defining domain-specific
        import rules and restrictions.

        The boundaries are stored in self.module_boundaries and include:
        - allowed_imports: imports that respect domain boundaries
        - forbidden_imports: imports that violate domain boundaries
        - recommendations: suggested import fixes
        """
        # Identify domain boundaries
        domains = self._identify_domains()

        # For each module, determine boundaries
        for file_path, info in self.module_boundaries.items():
            domain = self._get_file_domain(file_path, domains)

            # Get domain rules
            domain_rules = self._get_domain_rules(domain)

            # Apply rules to determine allowed and forbidden imports
            allowed_imports = []
            forbidden_imports = []
            recommendations = []

            for classified_import in info.get("imports", []):
                import_info = classified_import["import"]
                import_module = import_info.get("module", "")

                # Check if this import crosses domain boundaries
                import_domain = self._get_module_domain(import_module, domains)

                if self._is_import_allowed(domain, import_domain, domain_rules):
                    allowed_imports.append(import_info)
                else:
                    forbidden_imports.append(import_info)
                    # Generate recommendation
                    recommendation = self._generate_recommendation(
                        import_info, domain, import_domain, domain_rules
                    )
                    if recommendation:
                        recommendations.append(recommendation)

            # Update module boundaries with computed information
            self.module_boundaries[file_path].update(
                {
                    "domain": domain,
                    "allowed_imports": allowed_imports,
                    "forbidden_imports": forbidden_imports,
                    "recommendations": recommendations,
                }
            )

    def _identify_domains(self):
        """Identify domains in the codebase based on directory structure and patterns.

        Returns:
            A dictionary mapping domain names to lists of files in those domains.
        """
        domains = {}

        # Use directory structure as initial domain boundaries
        for root, dirs, files in os.walk(self.codebase_path):
            if not any(f.endswith(".py") for f in files):
                continue

            # Get relative path to determine potential domain
            rel_path = os.path.relpath(root, self.codebase_path)
            if rel_path == ".":
                domain = "root"
            else:
                # Use first directory level as domain
                domain = rel_path.split(os.path.sep)[0]

            if domain not in domains:
                domains[domain] = []

            # Add all Python files in this directory to the domain
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    domains[domain].append(file_path)

        return domains

    def _get_file_domain(self, file_path, domains):
        """Determine which domain a file belongs to.

        Args:
            file_path: Path to the file.
            domains: Dictionary of domains to files.

        Returns:
            The domain name the file belongs to.
        """
        for domain, files in domains.items():
            if file_path in files:
                return domain
        return "unknown"

    def _get_module_domain(self, module_name, domains):
        """Determine which domain a module belongs to based on its name.

        Args:
            module_name: Name of the module.
            domains: Dictionary of domains to files.

        Returns:
            The domain name the module likely belongs to.
        """
        # For built-in modules, return 'stdlib'
        if not module_name or "." not in module_name:
            try:
                __import__(module_name)
                return "stdlib"
            except ImportError:
                pass

        # Try to match module name to file paths
        top_module = module_name.split(".")[0]
        for domain, files in domains.items():
            for file_path in files:
                # Extract module path from file path
                rel_path = os.path.relpath(file_path, self.codebase_path)
                file_module = os.path.splitext(rel_path)[0].replace(os.path.sep, ".")

                if file_module == module_name or file_module.startswith(
                    f"{top_module}."
                ):
                    return domain

        # If not found in codebase, assume it's a third-party module
        return "third_party"

    def _get_domain_rules(self, domain):
        """Get domain-specific import rules.

        Args:
            domain: The name of the domain.

        Returns:
            A dictionary of rules for the domain.
        """
        # Get domain rules from the knowledge base
        domains = self.knowledge_base.get("domains", {})
        return domains.get(domain, domains.get("default", {}))

    def _is_import_allowed(self, source_domain, target_domain, domain_rules):
        """Determine if an import from source domain to target domain is allowed.

        Args:
            source_domain: Domain of the importing module.
            target_domain: Domain of the imported module.
            domain_rules: Rules for the source domain.

        Returns:
            True if the import is allowed, False otherwise.
        """
        # Always allow imports within the same domain
        if source_domain == target_domain:
            return True

        # Always allow imports from standard library
        if target_domain == "stdlib":
            return True

        # Check allowed domains in rules
        allowed_domains = domain_rules.get("allowed_imports", [])
        forbidden_domains = domain_rules.get("forbidden_imports", [])

        if target_domain in forbidden_domains:
            return False

        if "all" in allowed_domains or target_domain in allowed_domains:
            return True

        # If not explicitly allowed or forbidden, use default rule
        return domain_rules.get("allow_by_default", False)

    def _generate_recommendation(
        self, import_info, source_domain, target_domain, domain_rules
    ):
        """Generate a recommendation for an import that violates domain boundaries.

        Args:
            import_info: Information about the import.
            source_domain: Domain of the importing module.
            target_domain: Domain of the imported module.
            domain_rules: Rules for the source domain.

        Returns:
            A recommendation string or None.
        """
        recommendations = domain_rules.get("recommendations", {})

        # Check domain-specific recommendations
        if target_domain in recommendations:
            return recommendations[target_domain].format(
                module=import_info.get("module", ""), name=import_info.get("name", "")
            )

        # Default recommendation
        return f"Consider using an alternative from the {source_domain} domain instead of importing from {target_domain}"

    def _calculate_node_complexity(self, node):
        """Calculate the cyclomatic complexity of an AST node.

        Args:
            node: The AST node to analyze.

        Returns:
            An integer representing the complexity score.
        """
        complexity = 1  # Base complexity

        # Count branches and loops
        for child in ast.walk(node):
            if isinstance(child, (ast.If | ast.While | ast.For | ast.IfExp)):
                complexity += 1
            elif (isinstance(child, ast.BoolOp) and isinstance(child.op, ast.And)) or (
                isinstance(child, ast.BoolOp) and isinstance(child.op, ast.Or)
            ):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers) + (1 if child.orelse else 0)

        return complexity

    def _detect_class_pattern(self, node):
        """Detect design patterns in a class definition.

        Args:
            node: The AST class definition node.

        Returns:
            A string representing the detected pattern, or None.
        """
        class_name = node.name
        base_names = [base.id for base in node.bases if isinstance(base, ast.Name)]

        # Check class name for pattern indicators
        patterns = self.knowledge_base.get("class_patterns", {})

        # Check class name against patterns
        for pattern, indicators in patterns.items():
            # Check class name
            for suffix in indicators.get("name_suffixes", []):
                if class_name.endswith(suffix):
                    return pattern

            # Check base classes
            for base in indicators.get("base_classes", []):
                if base in base_names:
                    return pattern

            # Check method names
            method_indicators = indicators.get("methods", [])
            if method_indicators:
                methods = [
                    method.name
                    for method in node.body
                    if isinstance(method, ast.FunctionDef)
                ]

                if all(indicator in methods for indicator in method_indicators):
                    return pattern

        return None

    def _detect_function_pattern(self, node):
        """Detect patterns in a function definition.

        Args:
            node: The AST function definition node.

        Returns:
            A string representing the detected pattern, or None.
        """
        function_name = node.name

        # Check function name and patterns
        patterns = self.knowledge_base.get("function_patterns", {})

        for pattern, indicators in patterns.items():
            # Check function name prefixes
            for prefix in indicators.get("name_prefixes", []):
                if function_name.startswith(prefix):
                    return pattern

            # Check function name suffixes
            for suffix in indicators.get("name_suffixes", []):
                if function_name.endswith(suffix):
                    return pattern

            # Check decorator names
            if hasattr(node, "decorator_list") and node.decorator_list:
                decorators = [
                    (
                        d.id
                        if isinstance(d, ast.Name)
                        else d.attr
                        if isinstance(d, ast.Attribute)
                        else None
                    )
                    for d in node.decorator_list
                ]
                decorators = [d for d in decorators if d]

                for decorator in indicators.get("decorators", []):
                    if decorator in decorators:
                        return pattern

        return None

    def _extract_domain_markers(self, text):
        """Extract domain-specific markers from text.

        Args:
            text: The text to analyze, typically a docstring or comment.

        Returns:
            A set of domain markers found in the text.
        """
        if not text:
            return set()

        markers = set()

        # Check for domain markers in the knowledge base
        domain_markers = self.knowledge_base.get("domain_markers", {})

        for domain, terms in domain_markers.items():
            for term in terms:
                if term.lower() in text.lower():
                    markers.add(domain)

        return markers

    def _rule_matches(self, rule, imp, metrics):
        """Check if a rule matches an import and metrics.

        Args:
            rule: The rule to check.
            imp: The import information.
            metrics: The code metrics.

        Returns:
            True if the rule matches, False otherwise.
        """
        # Check import type
        if "import_type" in rule and rule["import_type"] != imp["type"]:
            return False

        # Check module name
        if "module" in rule:
            if isinstance(rule["module"], str):
                if rule["module"] != imp.get("module", ""):
                    return False
            elif isinstance(rule["module"], list):
                if imp.get("module", "") not in rule["module"]:
                    return False

        # Check imported name for 'from' imports
        if "name" in rule and imp["type"] == "from":
            if isinstance(rule["name"], str):
                if rule["name"] != imp.get("name", ""):
                    return False
            elif isinstance(rule["name"], list):
                if imp.get("name", "") not in rule["name"]:
                    return False

        # Check code metrics
        if "metrics" in rule:
            rule_metrics = rule["metrics"]

            # Check complexity threshold
            if (
                "min_complexity" in rule_metrics
                and metrics["complexity"] < rule_metrics["min_complexity"]
            ):
                return False

            # Check pattern requirements
            if "required_patterns" in rule_metrics:
                required = set(rule_metrics["required_patterns"])
                if not required.issubset(metrics["patterns"]):
                    return False

            # Check domain markers
            if "required_markers" in rule_metrics:
                required = set(rule_metrics["required_markers"])
                if not required.issubset(metrics["domain_markers"]):
                    return False

        # If we passed all checks, the rule matches
        return True
