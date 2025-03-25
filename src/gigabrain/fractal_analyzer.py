    class FractalDimensionAnalyzer:
    """Analyzes the fractal dimension of import structures to identify complexity patterns."""
    
    def __init__(self, min_scale=1, max_scale=10):
        self.min_scale = min_scale
        self.max_scale = max_scale
        
    def compute_box_counting_dimension(self, graph):
        """Compute the fractal dimension using box counting method."""
        # Extract node coordinates (assuming nodes have position attributes)
        positions = {}
        
        for node, attrs in graph.nodes(data=True):
            if 'pos' in attrs:
                positions[node] = np.array(attrs['pos'])
            else:
                # Generate a random position if none exists
                positions[node] = np.random.rand(2)
                
        # Normalize positions to [0,1]
        max_x = max(p[0] for p in positions.values())
        max_y = max(p[1] for p in positions.values())
        min_x = min(p[0] for p in positions.values())
        min_y = min(p[1] for p in positions.values())
        
        range_x = max_x - min_x
        range_y = max_y - min_y
        
        if range_x > 0 and range_y > 0:
            for node in positions:
                positions[node] = np.array([
                    (positions[node][0] - min_x) / range_x,
                    (positions[node][1] - min_y) / range_y
                ])
                
        # Compute box counts at different scales
        scales = []
        counts = []
        
        for scale in range(self.min_scale, self.max_scale + 1):
            box_size = 1.0 / scale
            boxes = set()
            
            for pos in positions.values():
                # Determine which box this node falls in
                box_x = int(pos[0] / box_size)
                box_y = int(pos[1] / box_size)
                boxes.add((box_x, box_y))
                
            scales.append(1.0 / box_size)
            counts.append(len(boxes))
            
        # Compute fractal dimension using linear regression
        if len(scales) > 1:
            log_scales = np.log(scales)
            log_counts = np.log(counts)
            
            # Linear regression: log(count) = D * log(1/box_size) + C
            D, C = np.polyfit(log_scales, log_counts, 1)
            
            return {
                'fractal_dimension': D,
                'scales': scales,
                'counts': counts,
                'fit_quality': np.corrcoef(log_scales, log_counts)[0, 1]**2
            }
        else:
            return {
                'fractal_dimension': 0,
                'scales': scales,
                'counts': counts,
                'fit_quality': 0
            }
            
    def analyze_interface_complexity(self, module_graph):
        """Analyze the complexity of module interfaces using fractal analysis."""
        # Create a bipartite graph of modules and their interfaces
        import networkx as nx
        interface_graph = nx.Graph()
        
        # Add module nodes
        for node, data in module_graph.nodes(data=True):
            if data.get('type') == 'module':
                interface_graph.add_node(node, type='module')
                
                # Add exported symbols as interface nodes
                for symbol in data.get('exports', []):
                    symbol_node = f"{node}:{symbol}"
                    interface_graph.add_node(symbol_node, type='symbol')
                    interface_graph.add_edge(node, symbol_node)
                    
        # Compute layout using force-directed algorithm
        pos = nx.spring_layout(interface_graph, seed=42)
        
        # Set positions as node attributes
        for node, position in pos.items():
            interface_graph.nodes[node]['pos'] = position
            
        # Compute fractal dimension
        fractal_metrics = self.compute_box_counting_dimension(interface_graph)
        
        # Compute additional interface complexity metrics
        complexity_metrics = {
            'fractal_dimension': fractal_metrics['fractal_dimension'],
            'interface_density': len(interface_graph.edges()) / max(1, len(interface_graph.nodes())),
            'clustering': nx.average_clustering(interface_graph),
            'assortativity': nx.degree_assortativity_coefficient(interface_graph)
        }
        
        return complexity_metrics