import ast
import hashlib
import random
import threading
from typing import Any, TypeVar, cast

import astunparse
import numpy as np
from numpy.typing import NDArray

Component = TypeVar("Component")


class ImportAgent:
    def __init__(self, agent_id: int, swarm: "ImportSwarmOptimizer") -> None:
        self.agent_id = agent_id
        self.swarm = swarm
        self.position: NDArray[np.float64] | None = None
        self.best_position: NDArray[np.float64] | None = None
        self.best_quality = float("-inf")
        self.knowledge_base: dict[str, float] = {}
        self.explored_regions: set[str] = set()

    def initialize(self) -> None:
        """Initialize the agent with a random position."""
        self.position = self.swarm.generate_random_position()
        if self.position is not None:
            self.best_position = self.position.copy()

    def explore(self) -> tuple[list[dict[str, Any]] | None, float]:
        """Explore the solution space and return the best solution found."""
        if self.position is None:
            return None, float("-inf")

        # Generate and evaluate solution
        solution = self.swarm.generate_solution_from_position(self.position)
        quality = self.swarm.evaluate_solution(solution)

        # Update personal best
        if quality > self.best_quality:
            self.best_quality = quality
            self.best_position = self.position.copy()

        # Update knowledge and deposit pheromone
        self._update_knowledge(self.position, quality)
        self.deposit_pheromone(quality)

        # Choose next position
        self.position = self._choose_next_position()

        return solution, quality

    def deposit_pheromone(self, quality: float) -> None:
        """Deposit pheromone at current position."""
        if self.position is None:
            return

        region_hash = self._hash_position(self.position)
        if region_hash:
            current_strength = self.swarm.pheromone_map.get(region_hash, 0)
            self.swarm.pheromone_map[region_hash] = max(current_strength, quality)
            self.swarm.position_cache[region_hash] = self.position.copy()

    def _choose_next_position(self) -> NDArray[np.float64]:
        """Choose the next position to explore."""
        if random.random() < 0.2:  # 20% chance to explore new regions
            return self._explore_new_regions()
        if random.random() < 0.5:  # 30% chance to exploit known good regions
            return self._exploit_knowledge()
        # 50% chance to follow pheromone trails
        return self._follow_pheromone_trail()

    def _exploit_knowledge(self) -> NDArray[np.float64]:
        """Exploit known good regions."""
        if not self.knowledge_base:
            return self._random_walk()

        # Find the best known region
        best_region = None
        best_quality = float("-inf")

        for region_hash in self.explored_regions:
            quality = self.knowledge_base.get(region_hash, 0)
            if quality > best_quality:
                best_quality = quality
                best_region = region_hash

        if best_region:
            # Move close to the best region with some random perturbation
            base_position = self._unhash_position(best_region)
            if base_position is not None:
                perturbation = np.random.normal(0, 0.1, base_position.shape[0])
                new_position = np.clip(base_position + perturbation, 0, 1)
                return new_position

        return self._random_walk()

    def _explore_new_regions(self) -> NDArray[np.float64]:
        """Explore regions that haven't been visited yet."""
        # Generate a new position that's different from explored regions
        attempts = 0
        while attempts < 10:
            new_position = self.swarm.generate_random_position()
            if new_position is not None:
                region_hash = self._hash_position(new_position)
                if region_hash and region_hash not in self.explored_regions:
                    return new_position
            attempts += 1

        # If we can't find a completely new region, find one that's least explored
        return self._random_walk()

    def _follow_pheromone_trail(self) -> NDArray[np.float64]:
        """Follow the strongest pheromone trail."""
        if self.position is None:
            return self._random_walk()

        # Find the strongest pheromone in the neighborhood
        neighborhood = self.swarm.get_neighborhood(self.position, radius=0.2)
        strongest_pheromone = None
        strongest_strength = 0

        for region_hash in neighborhood:
            strength = self.swarm.pheromone_map.get(region_hash, 0)
            if strength > strongest_strength:
                strongest_strength = strength
                strongest_pheromone = region_hash

        if strongest_pheromone:
            # Move towards the strongest pheromone
            target_position = self._unhash_position(strongest_pheromone)
            if target_position is not None:
                move_factor = random.uniform(0.3, 0.9)
                return self._interpolate_positions(
                    self.position, target_position, move_factor
                )

        return self._random_walk()

    def _random_walk(self) -> NDArray[np.float64]:
        """Take a random step from the current position."""
        if self.position is None:
            return self.swarm.generate_random_position()

        step_size = random.uniform(0.05, 0.2)
        direction = np.random.normal(0, 1, self.position.shape[0])
        direction = direction / np.linalg.norm(direction)

        new_position = self.position + step_size * direction
        return np.clip(new_position, 0, 1)  # Keep within bounds

    def _interpolate_positions(
        self, pos1: NDArray[np.float64], pos2: NDArray[np.float64], factor: float
    ) -> NDArray[np.float64]:
        """Interpolate between two positions."""
        return np.array(pos1) * (1 - factor) + np.array(pos2) * factor

    def _hash_position(self, position: NDArray[np.float64]) -> str | None:
        """Hash a position to a unique string identifier."""
        if position is None:
            return None
        position_bytes = position.tobytes()
        return hashlib.md5(position_bytes).hexdigest()

    def _unhash_position(self, region_hash: str) -> NDArray[np.float64] | None:
        """Convert a hashed region back to a position (approximate)."""
        if region_hash in self.swarm.position_cache:
            return self.swarm.position_cache[region_hash]
        return None

    def _update_knowledge(self, position: NDArray[np.float64], quality: float) -> None:
        """Update the agent's knowledge base with new information."""
        region_hash = self._hash_position(position)
        if region_hash:
            if region_hash not in self.knowledge_base:
                self.knowledge_base[region_hash] = quality
            else:
                # Update with exponential moving average
                alpha = 0.3
                self.knowledge_base[region_hash] = (
                    alpha * quality + (1 - alpha) * self.knowledge_base[region_hash]
                )


class ImportSwarmOptimizer:
    def __init__(self, project_files: list[str], num_agents: int = 20) -> None:
        self.project_files = project_files
        self.num_agents = num_agents
        self.agents: list[ImportAgent] = []
        self.pheromone_map: dict[str, float] = {}
        self.position_cache: dict[str, NDArray[np.float64]] = {}
        self.running = False
        self.best_solution: list[dict[str, Any]] | None = None
        self.best_solution_quality = 0.0
        self.best_position: NDArray[np.float64] | None = None
        self.best_position_quality = 0.0

    def initialize(self) -> None:
        """Initialize the swarm."""
        self.agents = [ImportAgent(i, self) for i in range(self.num_agents)]
        for agent in self.agents:
            agent.initialize()

    def run(self, iterations: int = 100) -> tuple[list[dict[str, Any]] | None, float]:
        """Run the swarm optimization."""
        self.running = True
        best_solution = None
        best_quality = float("-inf")

        for _ in range(iterations):
            if not self.running:
                break

            # Run each agent
            for agent in self.agents:
                solution, quality = agent.explore()
                if quality > best_quality:
                    best_quality = quality
                    best_solution = solution.copy() if solution is not None else None

            # Evaporate pheromones
            self._evaporate_pheromones()

        return best_solution, best_quality

    def run_async(self, iterations: int = 100) -> threading.Thread:
        """Run the swarm optimization asynchronously."""
        thread = threading.Thread(target=self.run, args=(iterations,))
        thread.start()
        return thread

    def stop(self) -> None:
        """Stop the optimization process."""
        self.running = False

    def generate_random_position(self) -> NDArray[np.float64]:
        """Generate a random position in the solution space."""
        return np.random.random(len(self.project_files))

    def generate_solution_from_position(
        self, position: NDArray | None
    ) -> list[dict[str, Any]] | None:
        """Generate an import solution from a position vector."""
        if position is None or not isinstance(position, np.ndarray):
            return None

        position_array = cast("NDArray", position)
        if len(position_array) == 0:
            return None

        solution = []
        for i, file_path in enumerate(self.project_files):
            # Analyze file symbols
            symbols = self._analyze_file_symbols(file_path)
            if not symbols:
                continue

            # Convert position component to import decisions
            pos_value = float(position_array[i])  # Explicit conversion to float
            import_style = self._determine_import_style(pos_value)

            # Group symbols by module
            grouped_symbols: dict[str, list[str]] = {}
            for symbol in symbols:
                module = self._find_module_for_symbol(symbol, [])
                if module:
                    if module not in grouped_symbols:
                        grouped_symbols[module] = []
                    grouped_symbols[module].append(symbol)

            # Generate import statements
            imports = []
            for module, symbols in grouped_symbols.items():
                if import_style == "specific":
                    imports.append(f"from {module} import {', '.join(symbols)}")
                else:
                    imports.append(f"import {module}")

            solution.append({"file": file_path, "imports": imports})

        return solution

    def evaluate_solution(self, solution: list[dict[str, Any]] | None) -> float:
        """Evaluate the quality of a solution."""
        if solution is None:
            return float("-inf")

        # Evaluate different aspects of the solution
        style_score = self._evaluate_style_consistency(solution)
        circular_score = self._evaluate_circular_imports(solution)
        namespace_score = self._evaluate_namespace_pollution(solution)
        grouping_score = self._evaluate_grouping_consistency(solution)

        # Weighted combination of scores
        weights = {"style": 0.3, "circular": 0.3, "namespace": 0.2, "grouping": 0.2}

        total_score = (
            weights["style"] * float(style_score)
            + weights["circular"] * float(circular_score)
            + weights["namespace"] * float(namespace_score)
            + weights["grouping"] * float(grouping_score)
        )

        return float(total_score)

    def get_neighborhood(
        self, position: NDArray[np.float64], radius: float
    ) -> list[str]:
        """Get the neighborhood of a position."""
        if not isinstance(position, np.ndarray):
            return []

        neighborhood = []
        for region_hash, cached_position in self.position_cache.items():
            if cached_position is not None:
                distance = np.linalg.norm(position - cached_position)
                if distance <= radius:
                    neighborhood.append(region_hash)
        return neighborhood

    def _evaporate_pheromones(self, rate: float = 0.1) -> None:
        """Evaporate pheromones by a given rate."""
        for region in self.pheromone_map:
            self.pheromone_map[region] *= 1 - rate

    def _determine_import_style(self, value):
        """Determine import style based on position value."""
        return "specific" if value > 0.5 else "module"

    def _analyze_file_symbols(self, file_path):
        """Analyze symbols in a Python file."""
        try:
            with open(file_path) as f:
                content = f.read()
            # Basic symbol extraction - in practice, use AST parsing
            symbols = set()
            lines = content.split("\n")
            for line in lines:
                if line.strip().startswith("import ") or line.strip().startswith(
                    "from "
                ):
                    continue
                words = line.split()
                symbols.update(word for word in words if word.isidentifier())
            return list(symbols)
        except Exception:
            return []

    def _find_module_for_symbol(self, symbol, contexts):
        """Find the most likely module for a symbol."""
        common_modules = {
            "print": "builtins",
            "list": "builtins",
            "dict": "builtins",
            "set": "builtins",
            "int": "builtins",
            "str": "builtins",
            "float": "builtins",
            "bool": "builtins",
            "tuple": "builtins",
            "range": "builtins",
            "len": "builtins",
            "type": "builtins",
            "object": "builtins",
            "Exception": "builtins",
            "open": "builtins",
        }
        return common_modules.get(symbol)

    def _evaluate_style_consistency(self, solution: list[dict[str, Any]]) -> float:
        """Evaluate style consistency of imports."""
        if not solution:
            return 0.0

        total_imports = 0
        style_counts = {"module": 0, "specific": 0}

        for file_info in solution:
            imports = file_info.get("imports", [])
            if not imports:
                continue

            total_imports += len(imports)
            for imp in imports:
                if isinstance(imp, str):
                    if imp.startswith("from"):
                        style_counts["specific"] += 1
                    else:
                        style_counts["module"] += 1

        if total_imports == 0:
            return 0.0

        max_style_count = max(style_counts.values())
        return float(max_style_count) / float(total_imports)

    def _evaluate_circular_imports(self, solution: list[dict[str, Any]]) -> float:
        """Evaluate circular import score."""
        # Implementation of circular import detection
        return 1.0  # Placeholder return value

    def _evaluate_namespace_pollution(self, solution: list[dict[str, Any]]) -> float:
        """Evaluate namespace pollution score."""
        # Implementation of namespace pollution evaluation
        return 1.0  # Placeholder return value

    def _evaluate_grouping_consistency(self, solution: list[dict[str, Any]]) -> float:
        """Evaluate grouping consistency score."""
        # Implementation of grouping consistency evaluation
        return 1.0  # Placeholder return value

    def _hash_position(self, position: np.ndarray) -> str:
        """Hash a position vector to a string."""
        if position is None:
            return ""
        return hashlib.md5(position.tobytes()).hexdigest()

    def apply_optimal_imports(self, solution):
        """Apply the optimized import solution to project files."""
        for file_path in self.project_files:
            try:
                with open(file_path) as f:
                    content = f.read()

                # Parse the file
                tree = ast.parse(content)

                # Remove existing imports
                new_body = []
                for node in tree.body:
                    if not isinstance(node, (ast.Import, ast.ImportFrom)):
                        new_body.append(node)

                # Find file-specific imports
                file_imports = []
                for imp in solution["imports"]:
                    file_required_symbols = self._analyze_file_symbols(file_path)

                    if ("symbol" in imp and imp["symbol"] in file_required_symbols) or (
                        imp["module"] in file_required_symbols
                    ):
                        file_imports.append(imp)

                # Group imports according to PEP 8
                standard_lib_imports, third_party_imports, local_imports = (
                    self._group_imports(file_imports)
                )

                # Create import nodes
                import_nodes = []

                # Add standard library imports
                if standard_lib_imports:
                    for imp in standard_lib_imports:
                        import_nodes.append(self._create_import_node(imp))
                    if third_party_imports or local_imports:
                        import_nodes.append(ast.Expr(value=ast.Str(s="")))

                # Add third-party imports
                if third_party_imports:
                    for imp in third_party_imports:
                        import_nodes.append(self._create_import_node(imp))
                    if local_imports:
                        import_nodes.append(ast.Expr(value=ast.Str(s="")))

                # Add local imports
                if local_imports:
                    for imp in local_imports:
                        import_nodes.append(self._create_import_node(imp))

                # Add imports at the beginning
                tree.body = import_nodes + new_body

                # Convert back to source code
                new_content = astunparse.unparse(tree)

                # Write back to file
                with open(file_path, "w") as f:
                    f.write(new_content)

                print(f"Applied optimized imports to {file_path}")

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        return True

    def _group_imports(
        self, imports: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        """Group imports into standard library, third-party, and local imports."""
        standard_lib_imports = []
        third_party_imports = []
        local_imports = []

        for import_item in imports:
            module_name = import_item.get("module", "")
            if not module_name:
                continue

            if "." not in module_name or module_name.split(".")[0] in [
                "os",
                "sys",
                "re",
                "math",
            ]:
                standard_lib_imports.append(import_item)
            elif module_name.startswith("."):
                local_imports.append(import_item)
            else:
                third_party_imports.append(import_item)

        # Sort each group
        for group in [standard_lib_imports, third_party_imports, local_imports]:
            group.sort(key=lambda x: x.get("module", ""))

        return standard_lib_imports, third_party_imports, local_imports

    def _create_import_node(self, import_item: dict[str, Any]) -> ast.AST:
        """Create an AST node for an import statement."""
        module_name = import_item.get("module", "")
        symbol_name = import_item.get("symbol")
        alias_name = import_item.get("alias")
        import_type = import_item.get("type", "import")

        if import_type == "import":
            return ast.Import(names=[ast.alias(name=module_name, asname=alias_name)])
        # from import
        level = 0
        while module_name.startswith("."):
            level += 1
            module_name = module_name[1:]

        return ast.ImportFrom(
            module=module_name,
            names=[ast.alias(name=symbol_name, asname=alias_name)],
            level=level,
        )

    def _apply_imports_to_file(
        self, file_path: str, imports: list[dict[str, Any]]
    ) -> bool:
        """Apply optimized imports to a file."""
        try:
            with open(file_path) as f:
                content = f.read()

            # Parse the file
            tree = ast.parse(content)

            # Remove existing imports
            new_body = [
                node
                for node in tree.body
                if not isinstance(node, (ast.Import, ast.ImportFrom))
            ]

            # Group imports
            std_imports, third_party_imports, local_imports = self._group_imports(
                imports
            )

            # Create import nodes
            import_nodes = []

            # Add standard library imports
            if std_imports:
                for imp in std_imports:
                    import_nodes.append(self._create_import_node(imp))
                if third_party_imports or local_imports:
                    import_nodes.append(ast.Expr(value=ast.Str(s="")))

            # Add third-party imports
            if third_party_imports:
                for imp in third_party_imports:
                    import_nodes.append(self._create_import_node(imp))
                if local_imports:
                    import_nodes.append(ast.Expr(value=ast.Str(s="")))

            # Add local imports
            if local_imports:
                for imp in local_imports:
                    import_nodes.append(self._create_import_node(imp))

            # Add imports at the beginning
            tree.body = import_nodes + new_body

            # Convert back to source code
            new_content = astunparse.unparse(tree)

            # Write back to file
            with open(file_path, "w") as f:
                f.write(new_content)

            print(f"Applied optimized imports to {file_path}")
            return True

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
