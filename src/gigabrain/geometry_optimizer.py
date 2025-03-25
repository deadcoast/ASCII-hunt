class InformationGeometryOptimizer:
   """Optimizes import structures using principles from information geometry."""
   
    def __init__(self, learning_rate=0.01, max_iter=100, tolerance=1e-5):
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.tolerance = tolerance
        
    def kl_divergence(self, p, q):
        """Compute KL divergence between probability distributions p and q."""
        # Add small epsilon to avoid log(0)
        eps = 1e-10
        p = np.maximum(p, eps)
        q = np.maximum(q, eps)
        
        # Normalize if not already
        p = p / np.sum(p)
        q = q / np.sum(q)
        
        return np.sum(p * np.log(p / q))
        
    def fisher_information_metric(self, theta, likelihood_function, epsilon=1e-4):
        """Approximate the Fisher information matrix at point theta."""
        n = len(theta)
        fisher_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                # Compute partial derivatives
                theta_pp = theta.copy()
                theta_pm = theta.copy()
                theta_mp = theta.copy()
                theta_mm = theta.copy()
                
                theta_pp[i] += epsilon
                theta_pp[j] += epsilon
                
                theta_pm[i] += epsilon
                theta_pm[j] -= epsilon
                
                theta_mp[i] -= epsilon
                theta_mp[j] += epsilon
                
                theta_mm[i] -= epsilon
                theta_mm[j] -= epsilon
                
                # Approximate second derivatives
                d2l = (likelihood_function(theta_pp) - likelihood_function(theta_pm) - 
                        likelihood_function(theta_mp) + likelihood_function(theta_mm))
                
                fisher_matrix[i, j] = d2l / (4 * epsilon * epsilon)
                
        return fisher_matrix
        
    def natural_gradient_step(self, theta, gradient, fisher_matrix):
        """Compute a natural gradient step using the Fisher information matrix."""
        # Regularize Fisher matrix to ensure numerical stability
        regularized_fisher = fisher_matrix + np.eye(len(theta)) * 1e-5
        
        # Compute inverse Fisher matrix
        try:
            inv_fisher = np.linalg.inv(regularized_fisher)
        except np.linalg.LinAlgError:
            # Fallback if inversion fails
            inv_fisher = np.eye(len(theta))
            
        # Compute natural gradient
        natural_gradient = inv_fisher @ gradient
        
        return natural_gradient
       
    def optimize_import_distribution(self, initial_theta, log_likelihood, prior=None):
        """Optimize import structure parameters using natural gradient descent."""
        theta = initial_theta.copy()
        
        # Define the objective function (posterior)
        def objective(theta):
            ll = log_likelihood(theta)
            
            if prior is not None:
                ll += prior(theta)
                
            return -ll  # Negative because we're minimizing
            
        # Keep track of optimization path
        theta_history = [theta.copy()]
        objective_history = [objective(theta)]
        
        for iteration in range(self.max_iter):
            # Compute gradient of objective
            gradient = self._compute_gradient(theta, objective)
            
            # Compute Fisher information matrix
            fisher_matrix = self.fisher_information_metric(theta, lambda t: -objective(t))
            
            # Compute natural gradient step
            natural_gradient = self.natural_gradient_step(theta, gradient, fisher_matrix)
            
            # Take a step
            theta -= self.learning_rate * natural_gradient
            
            # Record history
            theta_history.append(theta.copy())
            objective_history.append(objective(theta))
            
            # Check convergence
            if iteration > 0:
                improvement = objective_history[-2] - objective_history[-1]
                if improvement < self.tolerance:
                    break
                    
        return theta, theta_history, objective_history
        
    def _compute_gradient(self, theta, objective, epsilon=1e-6):
        """Compute gradient of objective function using finite differences."""
        gradient = np.zeros_like(theta)
        
        base_objective = objective(theta)
        
        for i in range(len(theta)):
            perturbed = theta.copy()
            perturbed[i] += epsilon
            
            gradient[i] = (objective(perturbed) - base_objective) / epsilon
            
        return gradient
        
    def optimize_import_groups(self, imports, similarity_matrix, n_groups=5):
        """Optimize the grouping of imports using information geometry."""
        n_imports = len(imports)
        
        # Initialize import assignments randomly
        import_probs = np.random.dirichlet(np.ones(n_groups), size=n_imports)
        
        # Define log likelihood for grouping
        def log_likelihood(probs_flat):
            # Reshape flat parameters
            probs = probs_flat.reshape((n_imports, n_groups))
            
            # Normalize probabilities
            probs = probs / np.sum(probs, axis=1, keepdims=True)
            
            # Compute likelihood based on how similar imports are grouped together
            ll = 0
            for i in range(n_imports):
                for j in range(n_imports):
                    # Higher similarity means these imports should be grouped similarly
                    group_alignment = np.sum(probs[i] * probs[j])
                    ll += similarity_matrix[i, j] * np.log(group_alignment + 1e-10)
                    
            return ll
            
        # Define prior for softmax probabilities
        def prior(probs_flat):
            probs = probs_flat.reshape((n_imports, n_groups))
            
            # Encourage sparsity (each import belongs strongly to one group)
            entropy = -np.sum(probs * np.log(probs + 1e-10))
            
            return -0.1 * entropy  # Negative because we want to minimize entropy
            
        # Flatten for optimization
        initial_theta = import_probs.flatten()
        
        # Optimize
        final_theta, theta_history, _ = self.optimize_import_distribution(
            initial_theta, log_likelihood, prior)
            
        # Reshape and normalize final assignments
        final_probs = final_theta.reshape((n_imports, n_groups))
        final_probs = final_probs / np.sum(final_probs, axis=1, keepdims=True)
        
        # Convert to hard assignments
        assignments = np.argmax(final_probs, axis=1)
        
        # Organize imports into groups
        groups = defaultdict(list)
        for i, group_id in enumerate(assignments):
            groups[group_id].append(imports[i])
            
        return groups, final_probs