import numpy as np
from qiskit.algorithms import QAOA, NumPyMinimumEigensolver
from qiskit.optimization import QuadraticProgram
from qiskit.optimization.algorithms import MinimumEigenOptimizer
from qiskit_aer import Aer
from qiskit_ibm_runtime import QiskitRuntimeService


class QuantumImportOptimizer:
    def __init__(self, use_real_quantum=False):
        self.use_real_quantum = use_real_quantum
        if use_real_quantum:
            # Connect to IBM Quantum Experience
            self.service = QiskitRuntimeService()
            self.backend = self.service.get_backend("ibmq_qasm_simulator")
        else:
            # Use simulator
            self.backend = Aer.get_backend("qasm_simulator")

    def optimize_imports(self, module_dependencies, constraints):
        """Use quantum optimization to find the optimal import structure.
        This solves the import ordering problem as a QUBO problem.
        """
        # Convert dependencies to an adjacency matrix
        n_modules = len(module_dependencies)
        adjacency_matrix = np.zeros((n_modules, n_modules))

        for i, (module_i, deps_i) in enumerate(module_dependencies.items()):
            for j, (module_j, deps_j) in enumerate(module_dependencies.items()):
                if i != j:
                    # Set the cost of having module i before module j
                    if module_j in deps_i:
                        # i depends on j, so j should come before i (penalty if not)
                        adjacency_matrix[i, j] = 10
                    elif module_i in deps_j:
                        # j depends on i, so i should come before j (penalty if not)
                        adjacency_matrix[j, i] = 10
                    else:
                        # No direct dependency, small cost for either ordering
                        adjacency_matrix[i, j] = 1
                        adjacency_matrix[j, i] = 1

        # Build the quadratic program
        qp = QuadraticProgram()

        # Add binary variables - x_ij means i comes before j
        for i in range(n_modules):
            for j in range(n_modules):
                if i != j:
                    qp.binary_var(f"x_{i}_{j}")

        # Objective: minimize the total cost
        objective = 0
        for i in range(n_modules):
            for j in range(n_modules):
                if i != j:
                    var_name = f"x_{i}_{j}"
                    objective += adjacency_matrix[i, j] * qp.get_variable(var_name)

        qp.minimize(objective)

        # Constraint: Either i comes before j, or j comes before i, not both
        for i in range(n_modules):
            for j in range(i + 1, n_modules):
                qp.add_constraint(
                    qp.get_variable(f"x_{i}_{j}") + qp.get_variable(f"x_{j}_{i}") == 1,
                    f"ordering_{i}_{j}",
                )

        # Constraint: Transitivity - if i before j and j before k, then i before k
        for i in range(n_modules):
            for j in range(n_modules):
                if i != j:
                    for k in range(n_modules):
                        if k != i and k != j:
                            qp.add_constraint(
                                qp.get_variable(f"x_{i}_{j}")
                                + qp.get_variable(f"x_{j}_{k}")
                                - qp.get_variable(f"x_{i}_{k}")
                                <= 1,
                                f"transitivity_{i}_{j}_{k}",
                            )

        # Add custom constraints (e.g., from style guides)
        for constraint in constraints:
            i, j = constraint  # i should come before j
            qp.add_constraint(qp.get_variable(f"x_{i}_{j}") == 1, f"custom_{i}_{j}")

        # Solve using quantum optimization
        if self.use_real_quantum:
            qaoa = QAOA(reps=3, quantum_instance=self.backend)
            optimizer = MinimumEigenOptimizer(qaoa)
        else:
            # Use classical solver for comparison
            optimizer = MinimumEigenOptimizer(NumPyMinimumEigensolver())

        result = optimizer.solve(qp)

        # Extract the optimal ordering
        optimal_ordering = {}
        for i in range(n_modules):
            predecessors = 0
            for j in range(n_modules):
                if (
                    i != j
                    and abs(result.x[qp.get_variable_index(f"x_{j}_{i}")] - 1) < 1e-5
                ):
                    predecessors += 1

            optimal_ordering[i] = predecessors

        # Convert to module order
        modules_by_index = list(module_dependencies.keys())
        ordered_modules = [
            modules_by_index[i]
            for i, _ in sorted(optimal_ordering.items(), key=lambda x: x[1])
        ]

        return ordered_modules, result.fval  # Return the ordering and its quality
