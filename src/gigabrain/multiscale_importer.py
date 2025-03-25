import os
import ast
import re
import math
import numpy as np
from collections import defaultdict
from gigabrain.import_entity import ImportEntity
from gigabrain.hypergraph_network import HypergraphImportNetwork
from gigabrain.fractal_analyzer import FractalDimensionAnalyzer
from gigabrain.wavelet_analyzer import WaveletImportAnalyzer
from gigabrain.riemannian_optimizer import RiemannianImportOptimizer


class MultiScaleImportRecommender:
   """Recommends imports using a multi-scale approach combining local and global patterns."""
   
    def __init__(self, code_corpus, embedding_dim=128):
       self.code_corpus = code_corpus
       self.embedding_dim = embedding_dim
       self.module_embeddings = {}
       self.symbol_embeddings = {}
       self.usage_patterns = defaultdict(list)
       self.context_encoder = None
       self.importance_weights = None
       
   def initialize(self):
       """Initialize the recommender with code corpus analysis."""
       # Build module and symbol embeddings
       self._build_embeddings()
       
       # Build context encoder
       self._build_context_encoder()
       
       # Compute importance weights
       self._compute_importance_weights()
       
    def _build_embeddings(self):
        """Build embeddings for modules and symbols from the code corpus."""
        # Count co-occurrences between modules and symbols
        module_symbol_cooccurrence = defaultdict(lambda: defaultdict(int))
        
        for code_file in self.code_corpus:
            # Extract imports and symbols used
            imports = self._extract_imports(code_file)
            symbols = self._extract_symbols(code_file)
            
            # Update co-occurrence matrix
            for module in imports:
                for symbol in symbols:
                    module_symbol_cooccurrence[module][symbol] += 1
        
        # Build joint co-occurrence matrix
        modules = list(module_symbol_cooccurrence.keys())
        symbols = set()
        for module_counts in module_symbol_cooccurrence.values():
            symbols.update(module_counts.keys())
        symbols = list(symbols)
        
        # Build co-occurrence matrix
        n_modules = len(modules)
        n_symbols = len(symbols)
        cooccurrence_matrix = np.zeros((n_modules + n_symbols, n_modules + n_symbols))
        
        # Map entities to indices
        module_to_idx = {module: i for i, module in enumerate(modules)}
        symbol_to_idx = {symbol: i + n_modules for i, symbol in enumerate(symbols)}
        
        # Fill the matrix
        for module, symbol_counts in module_symbol_cooccurrence.items():
            module_idx = module_to_idx[module]
            
            for symbol, count in symbol_counts.items():
                if symbol in symbol_to_idx:  # Symbol might not be in our list if filtered
                    symbol_idx = symbol_to_idx[symbol]
                    
                    # Update co-occurrence counts
                    cooccurrence_matrix[module_idx, symbol_idx] = count
                    cooccurrence_matrix[symbol_idx, module_idx] = count
        
        # Apply GloVe-inspired embedding algorithm
        embeddings = self._train_embeddings(cooccurrence_matrix, n_modules + n_symbols)
        
        # Store the embeddings
        for module, idx in module_to_idx.items():
            self.module_embeddings[module] = embeddings[idx]
            
        for symbol, idx in symbol_to_idx.items():
            self.symbol_embeddings[symbol] = embeddings[idx]
    
    def _train_embeddings(self, cooccurrence_matrix, n_entities):
        """Train embeddings using a GloVe-inspired approach."""
        # Initialize random embeddings
        embeddings = np.random.normal(0, 0.1, (n_entities, self.embedding_dim))
        
        # Hyperparameters
        learning_rate = 0.05
        max_count = np.max(cooccurrence_matrix)
        alpha = 0.75  # Smoothing parameter
        iterations = 50
        
        # Optimize embeddings
        for iteration in range(iterations):
            cost = 0
            
            # Process all non-zero co-occurrences
            for i in range(n_entities):
                for j in range(n_entities):
                    if cooccurrence_matrix[i, j] > 0:
                        # Apply scaling to handle common co-occurrences
                        weight = (cooccurrence_matrix[i, j] / max_count) ** alpha
                        
                        # Compute the squared distance
                        diff = np.dot(embeddings[i], embeddings[j]) - np.log(cooccurrence_matrix[i, j])
                        
                        # Update cost
                        cost += weight * diff ** 2
                        
                        # Compute gradients
                        grad_i = weight * diff * embeddings[j]
                        grad_j = weight * diff * embeddings[i]
                        
                        # Update embeddings
                        embeddings[i] -= learning_rate * grad_i
                        embeddings[j] -= learning_rate * grad_j
            
            # Adaptive learning rate
            learning_rate = learning_rate * 0.9
            
        # Normalize embeddings
        norms = np.sqrt(np.sum(embeddings ** 2, axis=1, keepdims=True))
        normalized_embeddings = embeddings / np.maximum(norms, 1e-10)
        
        return normalized_embeddings
    
    def _build_context_encoder(self):
        """Build a neural encoder for code context."""
        # A simple 2-layer neural network for context encoding
        import tensorflow as tf
        
        # Input layer for tokenized code
        input_layer = tf.keras.layers.Input(shape=(None,))
        
        # Embedding layer
        embedding = tf.keras.layers.Embedding(input_dim=10000, output_dim=128)(input_layer)
        
        # Apply bidirectional LSTM
        lstm = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128))(embedding)
        
        # Dense output layer
        output = tf.keras.layers.Dense(self.embedding_dim)(lstm)
        
        # Build the model
        self.context_encoder = tf.keras.Model(inputs=input_layer, outputs=output)
    
    def _compute_importance_weights(self):
        """Compute importance weights for symbols based on prevalence and information content."""
        # Count symbols across the corpus
        symbol_counts = defaultdict(int)
        total_files = len(self.code_corpus)
        
        for code_file in self.code_corpus:
            # Extract symbols and update counts
            symbols = set(self._extract_symbols(code_file))  # Use set to count only once per file
            
            for symbol in symbols:
                symbol_counts[symbol] += 1
        
        # Compute TF-IDF inspired weights
        self.importance_weights = {}
        
        for symbol, count in symbol_counts.items():
            # Inverse document frequency
            idf = math.log(total_files / (1 + count))
            
            # More complex weighting that considers symbol complexity
            symbol_complexity = len(symbol) / 10  # Simple heuristic
            self.importance_weights[symbol] = idf * (1 + symbol_complexity)
    
    def _extract_imports(self, code_file):
        """Extract imports from a code file."""
        imports = []
        
        try:
            # Parse the code file
            tree = ast.parse(code_file['content'])
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except:
            # Fallback to regex-based extraction
            import_pattern = r'^\s*(?:from\s+(\S+)\s+import|import\s+(\S+))'
            for line in code_file['content'].split('\n'):
                match = re.match(import_pattern, line)
                if match:
                    module = match.group(1) or match.group(2)
                    if module:
                        imports.append(module)
        
        return imports
    
    def _extract_symbols(self, code_file):
        """Extract symbols used in a code file."""
        symbols = []
        
        try:
            # Parse the code file
            tree = ast.parse(code_file['content'])
            
            # Extract symbol names
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    symbols.append(node.id)
        except:
            # Fallback to regex-based extraction
            identifier_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
            content = re.sub(r'#.*$', '', code_file['content'], flags=re.MULTILINE)  # Remove comments
            content = re.sub(r'""".*?"""', '', content, flags=re.DOTALL)  # Remove docstrings
            
            # Extract identifiers
            for match in re.finditer(identifier_pattern, content):
                symbols.append(match.group(0))
        
        return symbols
    
    def recommend_imports(self, code_snippet, max_recommendations=5):
        """Recommend imports for a code snippet using multi-scale analysis."""
        # Extract symbols from the snippet
        symbols = self._extract_symbols({'content': code_snippet})
        
        # Encode the context
        context_embedding = self._encode_context(code_snippet)
        
        # Compute relevance scores for all modules
        module_scores = {}
        
        for module, module_embedding in self.module_embeddings.items():
            # Start with context similarity
            score = self._cosine_similarity(context_embedding, module_embedding)
            
            # Add symbol-based scores
            for symbol in symbols:
                if symbol in self.symbol_embeddings:
                    symbol_embedding = self.symbol_embeddings[symbol]
                    
                    # Compute similarity between symbol and module
                    symbol_module_similarity = self._cosine_similarity(symbol_embedding, module_embedding)
                    
                    # Weight by symbol importance
                    weight = self.importance_weights.get(symbol, 1.0)
                    score += symbol_module_similarity * weight
            
            module_scores[module] = score
        
        # Sort modules by score
        ranked_modules = sorted(module_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top recommendations with explanations
        recommendations = []
        for module, score in ranked_modules[:max_recommendations]:
            # Find symbols that most likely come from this module
            related_symbols = []
            for symbol in symbols:
                if symbol in self.symbol_embeddings:
                    symbol_embedding = self.symbol_embeddings[symbol]
                    similarity = self._cosine_similarity(symbol_embedding, self.module_embeddings[module])
                    if similarity > 0.5:
                        related_symbols.append(symbol)
            
            recommendations.append({
                'module': module,
                'score': score,
                'related_symbols': related_symbols,
                'import_statement': self._generate_import_statement(module, related_symbols)
            })
        
        return recommendations
    
    def _encode_context(self, code_snippet):
        """Encode a code snippet into a context vector."""
        # For simplicity, return a random vector
        # In a real implementation, this would use the trained context encoder
        return np.random.normal(0, 1, self.embedding_dim)
    
    def _cosine_similarity(self, v1, v2):
        """Compute cosine similarity between two vectors."""
        dot_product = np.dot(v1, v2)
        norm1 = np.sqrt(np.sum(v1**2))
        norm2 = np.sqrt(np.sum(v2**2))
        return dot_product / max(norm1 * norm2, 1e-10)
    
    def _generate_import_statement(self, module, symbols):
        """Generate an appropriate import statement."""
        if not symbols:
            return f"import {module}"
        elif len(symbols) == 1:
            return f"from {module} import {symbols[0]}"
        else:
            symbols_str = ', '.join(symbols)
            return f"from {module} import {symbols_str}"