import networkx as nx
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork


class BayesianImportAnalyzer:
    def __init__(self) -> None:
        """Initialize the BayesianImportAnalyzer.

        This constructor initializes the BayesianImportAnalyzer instance with
        an empty BayesianNetwork, a set of variables and an empty evidence dictionary.
        """
        self.model = BayesianNetwork()
        self.variables: set[str] = set()
        self.evidence: dict[str, int] = {}
        # Track edge importance for resolving cycles
        self.edge_importance: dict[tuple[str, str], float] = {}

    def build_model_from_codebase(
        self, import_data: dict[str, dict[str, list[str]]]
    ) -> None:
        # Create nodes for each module
        """Build a Bayesian network from the given import data.

        Args:
            import_data (dict): Dictionary of modules and their dependencies.

        Returns:
            None
        """
        for module in import_data:
            self.variables.add(module)

        # Create edges based on import relationships
        edges = []
        for module, deps in import_data.items():
            for dep in deps["static_imports"]:
                if dep in self.variables:  # Only add edges for modules we're tracking
                    edges.append((dep, module))
                    # Initialize edge importance based on frequency of use
                    self.edge_importance[(dep, module)] = len(
                        deps.get("usage_count", [])
                    )

        # Add the edges to the model
        self.model.add_edges_from(edges)

        # Avoid cycles (Bayesian networks must be acyclic)
        self._remove_cycles()

        # Create conditional probability tables
        self._create_cpds(import_data)

        # Finalize model
        self.model.check_model()

        # Create inference engine
        self.inference = VariableElimination(self.model)

    def _remove_cycles(self) -> None:
        """Remove cycles from the Bayesian network to ensure it is acyclic.

        This method iteratively detects and removes cycles from the model by
        identifying the first cycle found in the network and removing the edge
        with the lowest calculated "importance" from that cycle. It continues
        this process until the model is a directed acyclic graph (DAG).
        """
        while not nx.is_directed_acyclic_graph(self.model):
            cycles = list(nx.simple_cycles(self.model))
            if not cycles:
                break

            # Remove the edge with the lowest "importance" in the first cycle
            cycle = cycles[0]
            edge_to_remove = None
            min_importance = float("inf")

            for i in range(len(cycle)):
                source = cycle[i]
                target = cycle[(i + 1) % len(cycle)]

                if (source, target) in self.model.edges():
                    # Use the edge_importance dictionary to calculate importance
                    importance = self._calculate_edge_importance(source, target)
                    if importance < min_importance:
                        min_importance = importance
                        edge_to_remove = (source, target)

            if edge_to_remove:
                self.model.remove_edge(*edge_to_remove)

    def _calculate_edge_importance(self, source: str, target: str) -> float:
        """Calculate the importance of an edge based on the usage count.

        Args:
            source: The source node of the edge
            target: The target node of the edge

        Returns:
            A float representing the importance of the edge
        """
        # Use the edge_importance dictionary or default to 0
        return self.edge_importance.get((source, target), 0.0)

    def _create_cpds(self, import_data: dict[str, dict[str, list[str]]]) -> None:
        """Create conditional probability tables (CPTs) for the Bayesian network.

        The CPTs are based on the import relationships between modules. If a module
        has no dependencies, it has a 90% chance of being correctly imported. If a
        module has dependencies, its CPT is based on the parent states. If any parent
        is incorrect, there is an 80% chance the module is incorrect. If all parents
        are correct, there is a 95% chance the module is correct.

        Args:
            import_data: The import data from which to create the CPTs
        """
        for node in self.model.nodes():
            parents = list(self.model.get_parents(node))

            if not parents:
                # No parents, just use prior probability
                # 90% chance the module is correctly imported if no dependencies
                cpd = TabularCPD(
                    variable=node,
                    variable_card=2,  # binary: correct/incorrect
                    values=[[0.1], [0.9]],  # P(incorrect)=0.1, P(correct)=0.9
                )
            else:
                # Create CPT based on parent states
                # For simplicity: if any parent is incorrect, 80% chance this is incorrect
                # If all parents correct, 95% chance this is correct
                num_parents = len(parents)
                parent_cards = [2] * num_parents

                # Calculate values array based on parent combinations
                values = []
                for i in range(2):  # i=0: incorrect, i=1: correct
                    row = []
                    for j in range(2**num_parents):
                        # Convert j to binary representation of parent states
                        parent_states = [(j >> k) & 1 for k in range(num_parents)]

                        if all(parent_states):  # All parents correct
                            row.append(0.05 if i == 0 else 0.95)
                        else:  # At least one parent incorrect
                            row.append(0.8 if i == 0 else 0.2)

                    values.append(row)

                cpd = TabularCPD(
                    variable=node,
                    variable_card=2,
                    values=values,
                    evidence=parents,
                    evidence_card=parent_cards,
                )

            self.model.add_cpds(cpd)

    def analyze_import_correctness(
        self, module_name: str, evidence: dict[str, int] | None = None
    ) -> float:
        """Analyze the correctness of the imports in a module.

        Args:
            module_name: name of the module to analyze
            evidence: dictionary of variable names and values to use as evidence
                for the inference. If None, use the default evidence.

        Returns:
            probability the imports are correct
        """
        if evidence:
            for var, val in evidence.items():
                self.evidence[var] = val

        # Check if module_name is valid
        if module_name not in self.variables:
            return 0.0  # Return 0 if module doesn't exist in model

        # Perform the query
        query_result = self.inference.query(
            variables=[module_name], evidence=self.evidence
        )

        # Return probability the imports are correct
        # Handle potential None or set result by safely extracting values
        try:
            # For pgmpy versions that return a Factor
            if hasattr(query_result, "values"):
                if hasattr(query_result.values, "tolist"):  # type: ignore
                    values_list = query_result.values.tolist()  # type: ignore
                    return values_list[1]  # Index 1 corresponds to "correct"
                # For versions that return a different structure
                return float(query_result.values[1])  # type: ignore
            # Fallback for other return types
            return 0.5  # Default probability
        except (IndexError, AttributeError, TypeError):
            return 0.5  # Default probability if we can't extract a value

    def suggest_import_fixes(self, threshold: float = 0.3) -> list[tuple[str, str]]:
        """Suggest fixes for imports that are likely incorrect based on a threshold.

        This method iterates over all modules and suggests import fixes for those
        not already verified in the evidence dictionary. It queries the Bayesian
        model to check if the probability of an import being incorrect exceeds the
        given threshold. If so, it suggests a fix by calling the `_suggest_fix`
        method and prints the suggestion.

        Args:
            threshold: A float value representing the probability threshold above
                which an import is considered incorrect and a fix is suggested.

        Returns:
            A list of tuples of (module_name, suggested_fix)
        """
        suggestions = []

        for module in self.variables:
            if module not in self.evidence:
                try:
                    # Get the most likely state for this module
                    query_result = self.inference.query(
                        variables=[module], evidence=self.evidence
                    )

                    # Convert the query result values to a list for proper indexing
                    incorrect_prob = 0.0

                    # Handle potential None or set result by safely extracting values
                    if hasattr(query_result, "values"):
                        if hasattr(query_result.values, "tolist"):  # type: ignore
                            values_list = query_result.values.tolist()  # type: ignore
                            incorrect_prob = values_list[0]
                        else:
                            # For versions that return a different structure
                            incorrect_prob = float(query_result.values[0])  # type: ignore

                    if incorrect_prob > threshold:
                        # Suggest a fix for this module
                        fix = self._suggest_fix(module)
                        print(f"Suggested fix for {module}: {fix}")
                        suggestions.append((module, fix))

                except (IndexError, AttributeError, TypeError) as e:
                    # Log the error but continue processing other modules
                    print(f"Error processing module {module}: {e!s}")

        return suggestions

    def _suggest_fix(self, module: str) -> str:
        # Check if the module has a known correct import
        """Suggest a fix for an incorrect import of a module.

        This method checks the Bayesian model for parent modules of the given module.
        If a parent module is found in the evidence dictionary, it suggests an import
        using that parent module. If no such parent is found, it suggests a general
        import for the module.

        Args:
            module: The name of the module for which to suggest a fix.

        Returns:
            A string containing the suggested import statement.
        """
        for dep in self.model.get_parents(module):
            if dep in self.evidence:
                # Use the correct import from the evidence
                return f"from {dep} import {module}"

        # If no correct parent, suggest a general import
        return f"import {module}"
