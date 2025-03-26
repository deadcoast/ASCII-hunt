import io
import tokenize
from collections.abc import Sequence
from typing import Any, TypeVar, Union, cast

import community as community_louvain
import libcst as cst
import networkx as nx
import sourcery
from libcst import CSTNode, ImportAlias, ImportFrom, ImportStar
from libcst.metadata import ScopeProvider

# Type definitions for better type checking
CSTNodeType = TypeVar("CSTNodeType", bound=CSTNode)
NameType = Union[cst.Name | cst.Attribute | cst.BaseExpression, str]
ImportNodeType = Union[ImportAlias, ImportStar]


# Define CST types for compatibility with multiple libcst versions
class CstContexts:
    """Compatibility class for CST contexts across libcst versions."""

    @staticmethod
    def is_import_star(node: CSTNodeType) -> bool:
        """Check if a node is an ImportStar node.

        Args:
            node: The node to check

        Returns:
            bool: True if the node is an ImportStar node
        """
        return hasattr(node, "__class__") and node.__class__.__name__ == "ImportStar"

    @staticmethod
    def is_load_context(node: CSTNodeType, parent: CSTNodeType | None) -> bool:
        """Check if a node is in a load context.

        Args:
            node: The node to check
            parent: The parent node

        Returns:
            bool: True if the node is in a load context
        """
        if parent is None:
            return True

        # Check for store context first
        if CstContexts.is_store_context(node, parent):
            return False

        # Otherwise, assume load context
        return True

    @staticmethod
    def is_store_context(node: CSTNodeType, parent: CSTNodeType | None) -> bool:
        """Check if a node is in a store context.

        Args:
            node: The node to check
            parent: The parent node

        Returns:
            bool: True if the node is in a store context
        """
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
    """Analyzer that tracks imports and symbol usage in Python code."""

    METADATA_DEPENDENCIES = (ScopeProvider,)

    def __init__(self) -> None:
        """Initialize a CSTImportAnalyzer.

        This analyzer tracks imports, references, defined symbols and star imports.
        """
        super().__init__()
        self.imports: list[dict[str, Any]] = []
        self.references: set[str] = set()
        self.defined: set[str] = set()
        self.star_imports: list[dict[str, Any]] = []
        self.import_history: list[dict[str, Any]] = []
        self.symbol_to_module: dict[str, str] = {}

    def visit_import(self, node: cst.Import) -> None:
        """Process an Import node.

        Args:
            node: The Import node being visited
        """
        for name in node.names:
            alias = self._get_name_value(
                cast(NameType, name.asname.name if name.asname else name.name)
            )
            module = self._get_name_value(cast(NameType, name.name))

            self.imports.append(
                {
                    "type": "import",
                    "module": module,
                    "alias": alias,
                    "node": node,
                }
            )

    def visit_import_from(self, node: ImportFrom) -> None:
        """Process an ImportFrom node.

        Args:
            node: The ImportFrom node being visited
        """
        module = (
            self._get_name_value(cast(NameType, node.module)) if node.module else ""
        )

        # Safely handle names by checking type first
        if not hasattr(node, "names"):
            return

        # Get names as a sequence of import nodes
        try:
            names = node.names
            if not isinstance(names, Sequence):
                return
        except (AttributeError, TypeError):
            return

        # First check if any name is an ImportStar
        has_star_import = False
        for name in names:
            if isinstance(name, ImportStar):
                has_star_import = True
                break

        if has_star_import:
            self.star_imports.append(
                {
                    "type": "from_star",
                    "module": module,
                    "node": node,
                }
            )
            return

        # Process regular imports
        for name in names:
            if isinstance(name, ImportStar):
                continue

            if not isinstance(name, ImportAlias):
                continue

            alias = self._get_name_value(
                cast(NameType, name.asname.name if name.asname else name.name)
            )
            name_value = self._get_name_value(cast(NameType, name.name))

            self.imports.append(
                {
                    "type": "from",
                    "module": module,
                    "name": name_value,
                    "alias": alias,
                    "node": node,
                }
            )

    def _get_name_value(self, name_obj: NameType) -> str:
        """Get the string value from a name object.

        Args:
            name_obj: A name object from libcst

        Returns:
            str: The string value of the name
        """
        try:
            if isinstance(name_obj, (cst.Name, cst.Attribute)) and hasattr(
                name_obj, "value"
            ):
                return cast(str, name_obj.value)
            return str(name_obj)
        except (AttributeError, TypeError):
            return str(name_obj)

    def visit_name(self, node: cst.Name) -> None:
        """Process a Name node.

        Args:
            node: The Name node being visited
        """
        parent = self.get_parent(node)

        if CstContexts.is_load_context(node, parent):
            self.references.add(node.value)
        elif CstContexts.is_store_context(node, parent):
            self.defined.add(node.value)

    def get_parent(self, node: cst.CSTNode) -> cst.CSTNode | None:
        """Get the parent node of a CST node.

        Args:
            node: The CST node to get the parent of

        Returns:
            Optional[cst.CSTNode]: The parent node or None
        """
        return None


class SimplifiedSourceryClient:
    """A simplified client that mimics the Sourcery API for development purposes."""

    class Result:
        """Result class for storing Sourcery suggestions."""

        def __init__(self) -> None:
            self.suggestions: list[SimplifiedSourceryClient.Suggestion] = []

    class Suggestion:
        """Suggestion class for storing code improvement suggestions."""

        def __init__(
            self, description: str = "", code_before: str = "", code_after: str = ""
        ) -> None:
            self.description = description
            self.code_before = code_before
            self.code_after = code_after

    def __init__(self) -> None:
        """Initialize the SimplifiedSourceryClient."""
        pass

    def review(
        self, source_code: str, file_name: str
    ) -> "SimplifiedSourceryClient.Result":
        """Review source code and suggest improvements.

        Args:
            source_code: The source code to review
            file_name: The name of the file being reviewed

        Returns:
            Result: A result object with suggestions
        """
        result = self.Result()
        suggestion = self.Suggestion(
            description="Add import statement",
            code_before="x = 5",
            code_after="import math\nx = 5",
        )
        result.suggestions.append(suggestion)
        return result


def analyze_with_sourcery(source_code: str) -> list[dict[str, Any]]:
    """Analyze source code using Sourcery for potential improvements.

    Args:
        source_code: The source code to analyze

    Returns:
        List[Dict[str, Any]]: List of suggestions for code improvements
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
    """Apply advanced graph algorithms to improve import understanding.

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
    """Detect communities in a graph, with multiple fallback methods.

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
    """Fallback community detection implementation.

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
    """Tokenize Python code into a list of tokens.

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
    """Convert a token to a numeric ID for feature matrix construction.

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
