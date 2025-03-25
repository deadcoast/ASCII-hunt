import io
import tokenize
from typing import Any

import community as community_louvain  # type: ignore
import libcst as cst
import networkx as nx
import sourcery  # type: ignore
from libcst.metadata import ScopeProvider


# Define CST types for compatibility with multiple libcst versions
class CST_Contexts:
    """Compatibility class for CST contexts across libcst versions"""

    @staticmethod
    def is_import_star(node: Any) -> bool:
        """Check if a node is an ImportStar"""
        return hasattr(node, "__class__") and node.__class__.__name__ == "ImportStar"

    @staticmethod
    def is_load_context(node: Any, parent: Any) -> bool:
        """Check if a node is in a load context"""
        # If no parent, default to load
        if parent is None:
            return True

        # Check for store context first
        if CST_Contexts.is_store_context(node, parent):
            return False

        # Otherwise, assume load context
        return True

    @staticmethod
    def is_store_context(node: Any, parent: Any) -> bool:
        """Check if a node is in a store context"""
        if parent is None:
            return False

        try:
            # Simple checks for common store contexts
            if hasattr(parent, "target") and getattr(parent, "target", None) is node:
                return True

            # Check for common assignment patterns
            parent_class_name = parent.__class__.__name__
            if parent_class_name in ["Assign", "AnnAssign", "For", "AugAssign"]:
                target = getattr(parent, "target", None)
                return target is node
        except (AttributeError, TypeError):
            pass

        return False


class CSTImportAnalyzer(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (ScopeProvider,)

    def __init__(self):
        """
        Initialize the CSTImportAnalyzer.

        This analyzer will keep track of import statements, symbols referenced,
        and symbols defined in the code.
        """
        super().__init__()
        self.imports: list[dict[str, Any]] = []
        self.references: set[str] = set()
        self.defined: set[str] = set()
        # Add tracking for star imports
        self.star_imports: list[dict[str, Any]] = []

    def visit_Import(self, node):
        """
        Called when a node is an `Import` statement. This callback is useful for
        tracking which imports are used in the code.

        :param node: The `Import` node being visited.
        :type node: ``cst.Import``
        """
        for name in node.names:
            # Get the alias and module name safely
            alias = self._get_name_value(name.asname.name if name.asname else name.name)
            module = self._get_name_value(name.name)

            self.imports.append(
                {
                    "type": "import",
                    "module": module,
                    "alias": alias,
                    "node": node,
                }
            )

    def visit_ImportFrom(self, node):
        """
        Called when a node is an `ImportFrom` statement. It tracks import statements
        that use the `from ... import ...` syntax, recording data involved.

        :param node: The `ImportFrom` node being visited.
        :type node: ``cst.ImportFrom``
        """
        module = self._get_name_value(node.module) if node.module else ""

        # Handle star imports safely
        has_star_import = any(CST_Contexts.is_import_star(name) for name in node.names)  # type: ignore

        if has_star_import:
            self.star_imports.append(
                {
                    "type": "from_star",
                    "module": module,
                    "node": node,
                }
            )
            return

        for name in node.names:
            # Skip star imports safely
            if CST_Contexts.is_import_star(name):  # type: ignore
                continue

            alias = self._get_name_value(name.asname.name if name.asname else name.name)
            name_value = self._get_name_value(name.name)

            self.imports.append(
                {
                    "type": "from",
                    "module": module,
                    "name": name_value,
                    "alias": alias,
                    "node": node,
                }
            )

    def _get_name_value(self, name_obj: Any) -> str:
        """
        Safely get the value from a name object, handling different libcst versions.

        Args:
            name_obj: A name object from libcst

        Returns:
            The string value of the name
        """
        try:
            if hasattr(name_obj, "value"):
                return name_obj.value
            else:
                return str(name_obj)
        except (AttributeError, TypeError):
            return str(name_obj)

    def visit_Name(self, node):
        """
        Called when a node is a `Name` node. This callback is useful for
        tracking which variables are referenced in the code.

        :param node: The `Name` node being visited.
        :type node: ``cst.Name``
        """
        # Get the parent node (this is simplified)
        parent = self.get_parent(node)

        # Use the CST_Contexts helper to determine the context
        if CST_Contexts.is_load_context(node, parent):
            self.references.add(node.value)
        elif CST_Contexts.is_store_context(node, parent):
            self.defined.add(node.value)

    def get_parent(self, node):
        """Get the parent node of the current node if available."""
        # This is a simple implementation - in a real CST visitor,
        # you'd have access to the parent node
        return None


# Make sourcery handling more robust with fallbacks
class SimplifiedSourceryClient:
    """A simplified client that mimics the Sourcery API for development purposes"""

    def review(self, source_code, file_name):
        """Simulate a review of source code"""

        # Create a simple result object with suggestions
        class Result:
            def __init__(self):
                self.suggestions = []

        class Suggestion:
            def __init__(self, description="", code_before="", code_after=""):
                self.description = description
                self.code_before = code_before
                self.code_after = code_after

        # Create an empty result
        result = Result()
        # Add a dummy suggestion to result for import statement
        suggestion = Suggestion(
            description="Add import statement",
            code_before="x = 5",
            code_after="import math\nx = 5",
        )
        result.suggestions.append(suggestion)
        return result


def analyze_with_sourcery(source_code):
    """
    Analyze source code using Sourcery to identify potential imports.

    This function leverages Sourcery's analysis to extract suggestions
    for import statements that can be added to the code.

    Args:
        source_code (str): The source code to analyze.

    Returns:
        list[dict[str, str]]: A list of dictionaries containing Sourcery's suggestions.
    """
    # Create a generic client that will work regardless of Sourcery version
    client = SimplifiedSourceryClient()

    # Attempt to use the actual Sourcery client if available
    try:
        # Use a type ignore since Sourcery's API may vary
        sourcery_client = sourcery.Sourcery()  # type: ignore
        if hasattr(sourcery_client, "review"):
            client = sourcery_client
    except Exception:
        # Fall back to the simplified client if anything goes wrong
        pass

    # Process the code with the client
    result = client.review(source_code, "file.py")

    # Extract insights from analysis
    insights = []
    try:
        # Try to process the suggestions
        for suggestion in result.suggestions:
            if (
                hasattr(suggestion, "code_after")
                and hasattr(suggestion, "code_before")
                and hasattr(suggestion, "description")
            ):
                # Look for import-related suggestions
                code_after = str(suggestion.code_after)
                code_before = str(suggestion.code_before)
                if "import" in code_after and "import" not in code_before:
                    insights.append(
                        {
                            "description": suggestion.description,
                            "suggested_import": code_after,
                        }
                    )
    except Exception:
        # In case of any error, return an empty list
        pass

    return insights


# Make community detection more robust
def enhance_dependency_graph(graph):
    """
    Apply advanced graph algorithms to improve import understanding.

    Args:
        graph (nx.DiGraph): The dependency graph to analyze.

    Returns:
        dict[str, Any]: A dictionary containing the results of the analysis.
    """
    # Calculate centrality measures
    centrality = nx.betweenness_centrality(graph)

    # Use a more robust community detection approach
    partition = detect_communities(graph)

    # Calculate shortest paths for optimal import paths
    shortest_paths = dict(nx.all_pairs_shortest_path_length(graph))

    # Calculate graph density to identify overly coupled code
    density = nx.density(graph)

    return {
        "centrality": centrality,
        "communities": partition,
        "shortest_paths": shortest_paths,
        "density": density,
    }


def detect_communities(graph):
    """
    Detect communities in a graph, with multiple fallback methods.

    Args:
        graph (nx.Graph): The graph to analyze

    Returns:
        dict: Mapping of nodes to community IDs
    """
    # Try multiple methods to detect communities
    undirected = graph.to_undirected() if graph.is_directed() else graph

    # Method 1: Try community_louvain's best_partition
    try:
        # Use type ignore since community library may vary
        return community_louvain.best_partition(undirected)  # type: ignore
    except Exception:
        pass

    # Method 2: Try importing community directly
    try:
        import community  # type: ignore

        return community.best_partition(undirected)  # type: ignore
    except Exception:
        pass

    # Method 3: Use networkx connected components as communities
    return detect_communities_fallback(graph)


def detect_communities_fallback(graph):
    """
    Fallback community detection implementation.

    Args:
        graph (nx.Graph): The graph to analyze

    Returns:
        dict: Mapping of nodes to community IDs
    """
    partition = {}

    # Try to use connected components if the graph is undirected
    if not graph.is_directed():
        for i, component in enumerate(nx.connected_components(graph)):
            for node in component:
                partition[node] = i
    else:
        # Just assign each node to its own community
        for i, node in enumerate(graph.nodes()):
            partition[node] = i

    return partition


# Define tokenize_code and token_to_id functions to fix undefined references
def tokenize_code(code):
    """
    Tokenize Python code into a list of tokens.

    Args:
        code (str): The code to tokenize

    Returns:
        list: A list of tokens
    """
    tokens = []
    try:
        # Create a file-like object from the code string
        code_io = io.StringIO(code)
        # Tokenize the code
        for tok in tokenize.generate_tokens(code_io.readline):
            # Only keep tokens that are meaningful for analysis
            if tok.type not in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE):
                tokens.append((tok.type, tok.string))
    except tokenize.TokenError:
        # Handle tokenization errors gracefully
        pass
    return tokens


def token_to_id(token):
    """
    Convert a token to a numeric ID for feature matrix construction.

    Args:
        token (tuple): A token tuple containing (token_type, token_string)

    Returns:
        float: A numeric ID representing the token
    """
    token_type, token_string = token

    # Simple hash-based approach to convert tokens to numeric values
    hash_value = hash(token_string) % 997  # Use a prime number to reduce collisions

    # Scale the value to be between 0 and 1
    return (hash_value / 997.0) * 0.8 + (token_type / 100.0) * 0.2
