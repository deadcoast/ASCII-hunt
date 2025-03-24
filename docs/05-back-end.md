<userStyle>Claude aims to write in a clear, polished way that works well for business settings.
Claude structures its answers carefully, with clear sections and logical flow. It gets to the point quickly while giving enough detail to fully answer the question.
Claude uses a formal but clear tone, avoiding casual language and slang. It writes in a way that would be appropriate for sharing with colleagues and stakeholders.
Claude balances being thorough with being efficient. It includes important context and details while leaving out unnecessary information that might distract from the main points.
Claude writes prose and in full sentences, especially for reports, documents, explanations, and question answering. Claude can use bullet points or lists only if the human asks specifically for a list, or if it makes sense for the specific task that the human is asking about.</userStyle>

# 5. Back End - Comprehensive Implementation Plan

## 5.1 System Architecture Overview

The back end of the ASCII UI Translation Framework will employ an advanced, high-performance architecture designed to process, analyze, and transform ASCII UI designs into structured component models and generate corresponding code. This system will leverage cutting-edge algorithms, parallel processing capabilities, and sophisticated data structures to ensure optimal performance, accuracy, and extensibility.

### Core Architectural Principles

The back end architecture will adhere to the following principles:

1. **Pipeline Architecture**: The system will implement a sophisticated data processing pipeline that transforms raw ASCII input through multiple processing stages into a final code output, with each stage building upon the results of previous stages.

2. **Microkernel Design**: The core system will provide minimal essential functionality, with specialized modules plugging into well-defined extension points, enabling both maintainability and extensive customization.

3. **Domain-Driven Design**: The system will model the problem domain explicitly, with clear boundaries between different contexts (grid analysis, component recognition, hierarchical modeling, code generation).

4. **Reactive Processing**: The system will implement reactive data flow patterns to efficiently propagate changes through the processing pipeline, enabling incremental updates and real-time feedback.

5. **Immutable Data Structures**: Where appropriate, the system will use immutable data structures to simplify concurrency, enable efficient caching, and support transactional operations.

### High-Level System Components

The back end system will comprise the following major components:

1. **Data Processing Core**: Manages the flow of data through the processing pipeline, orchestrating the various analysis and transformation steps.

2. **Grid Analysis Subsystem**: Processes the raw ASCII grid to identify spatial structures, boundaries, and content regions.

3. **Component Recognition Engine**: Analyzes grid structures to recognize UI components and their properties.

4. **Hierarchical Modeling System**: Establishes parent-child relationships and builds the component hierarchy.

5. **Code Generation Framework**: Transforms the component model into framework-specific code.

6. **Extension Management System**: Provides mechanisms for extending and customizing system behavior.

7. **Persistence Layer**: Manages saving and loading of projects, including both raw ASCII data and recognized component models.

8. **Performance Optimization Subsystem**: Monitors and optimizes system performance during processing.

## 5.2 Data Stack Architecture

### Data Representation Layer

The data representation layer will provide optimized structures for storing and processing ASCII UI data:

#### ASCII Grid Representation

```python
class ASCIIGrid:
    def __init__(self, data=None, width=0, height=0):
        if data is not None:
            # Initialize from existing data
            if isinstance(data, str):
                # Parse string into grid
                lines = data.splitlines()
                self.height = len(lines)
                self.width = max(len(line) for line in lines) if self.height > 0 else 0
                self._grid = np.zeros((self.height, self.width), dtype=np.unicode_)

                for y, line in enumerate(lines):
                    for x, char in enumerate(line):
                        self._grid[y, x] = char
            elif isinstance(data, np.ndarray):
                # Use NumPy array directly
                self._grid = data
                self.height, self.width = data.shape
        else:
            # Create empty grid of specified size
            self._grid = np.full((height, width), ' ', dtype=np.unicode_)
            self.height = height
            self.width = width

        # Create views for efficient processing
        self._char_mapping = None
        self._line_indices = None
        self._boundary_mask = None

    def get_char(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._grid[y, x]
        return None

    def set_char(self, x, y, char):
        if 0 <= x < self.width and 0 <= y < self.height:
            self._grid[y, x] = char

            # Invalidate cached views
            self._char_mapping = None
            self._line_indices = None
            self._boundary_mask = None

    def get_row(self, y):
        if 0 <= y < self.height:
            return self._grid[y, :]
        return None

    def get_column(self, x):
        if 0 <= x < self.width:
            return self._grid[:, x]
        return None

    def get_region(self, x1, y1, x2, y2):
        x1 = max(0, min(x1, self.width-1))
        y1 = max(0, min(y1, self.height-1))
        x2 = max(0, min(x2, self.width-1))
        y2 = max(0, min(y2, self.height-1))

        if x1 <= x2 and y1 <= y2:
            return self._grid[y1:y2+1, x1:x2+1]
        return None

    def get_boundary_mask(self):
        """Get a mask indicating boundary characters."""
        if self._boundary_mask is None:
            # Create boundary character set
            boundary_chars = set('┌┐└┘│─┬┴├┤┼╔╗╚╝║═╦╩╠╣╬┏┓┗┛┃━┳┻┣┫╋╭╮╰╯')

            # Create mask using vectorized operations
            char_array = np.array(list(boundary_chars))
            self._boundary_mask = np.isin(self._grid, char_array)

        return self._boundary_mask

    def get_character_density_map(self):
        """Get a map of character densities for content analysis."""
        # Non-whitespace density
        density = np.zeros((self.height, self.width))

        # Use sliding window to calculate local density
        window_size = 3
        for y in range(self.height):
            for x in range(self.width):
                # Calculate window boundaries
                x1 = max(0, x - window_size // 2)
                x2 = min(self.width - 1, x + window_size // 2)
                y1 = max(0, y - window_size // 2)
                y2 = min(self.height - 1, y + window_size // 2)

                # Calculate density in window
                window = self._grid[y1:y2+1, x1:x2+1]
                count = np.sum(window != ' ')
                total = window.size

                density[y, x] = count / total if total > 0 else 0

        return density

    def to_numpy(self):
        """Get the NumPy array representation of the grid."""
        return self._grid.copy()

    def to_string(self):
        """Convert grid to a string representation."""
        lines = []
        for y in range(self.height):
            line = ''.join(self._grid[y, :])
            lines.append(line)
        return '\n'.join(lines)
```

#### Component Model Representation

```python
class ComponentModel:
    def __init__(self):
        self.components = {}
        self.root_components = set()
        self.component_types = {}
        self.relationships = {}

    def add_component(self, component):
        """Add a component to the model."""
        component_id = component.id
        self.components[component_id] = component

        # Register component by type
        component_type = component.type
        if component_type not in self.component_types:
            self.component_types[component_type] = set()
        self.component_types[component_type].add(component_id)

        # Initially, consider it a root component
        self.root_components.add(component_id)

    def add_relationship(self, source_id, target_id, relationship_type):
        """Add a relationship between components."""
        if source_id not in self.components or target_id not in self.components:
            raise ValueError("Both components must exist in the model")

        # Add to relationships dictionary
        if source_id not in self.relationships:
            self.relationships[source_id] = {}
        if relationship_type not in self.relationships[source_id]:
            self.relationships[source_id][relationship_type] = set()

        self.relationships[source_id][relationship_type].add(target_id)

        # If this is a containment relationship, update root status
        if relationship_type == 'contains':
            if target_id in self.root_components:
                self.root_components.remove(target_id)

    def get_component(self, component_id):
        """Get a component by ID."""
        return self.components.get(component_id)

    def get_components_by_type(self, component_type):
        """Get all components of a specific type."""
        component_ids = self.component_types.get(component_type, set())
        return [self.components[cid] for cid in component_ids]

    def get_relationships(self, component_id, relationship_type=None):
        """Get components related to the specified component."""
        if component_id not in self.relationships:
            return []

        if relationship_type is not None:
            related_ids = self.relationships[component_id].get(relationship_type, set())
            return [self.components[rid] for rid in related_ids]
        else:
            # Get all relationships
            related_ids = set()
            for rel_type, ids in self.relationships[component_id].items():
                related_ids.update(ids)
            return [self.components[rid] for rid in related_ids]

    def get_contained_components(self, container_id):
        """Get components contained within a container component."""
        return self.get_relationships(container_id, 'contains')

    def get_container(self, component_id):
        """Get the container of a component, if any."""
        for potential_container, relationships in self.relationships.items():
            if 'contains' in relationships and component_id in relationships['contains']:
                return self.components[potential_container]
        return None

    def get_hierarchy(self):
        """Get a hierarchical representation of the component model."""
        hierarchy = {}

        def build_hierarchy_node(component_id):
            component = self.components[component_id]
            node = {
                'component': component,
                'children': []
            }

            # Add contained components as children
            contained = self.get_contained_components(component_id)
            for child in contained:
                child_node = build_hierarchy_node(child.id)
                node['children'].append(child_node)

            return node

        # Start with root components
        for root_id in self.root_components:
            hierarchy[root_id] = build_hierarchy_node(root_id)

        return hierarchy

    def validate(self):
        """Validate the component model for consistency."""
        errors = []

        # Check that all components have required properties
        for component_id, component in self.components.items():
            if not component.validate():
                errors.append(f"Component {component_id} ({component.type}) is invalid")

        # Check for circular containment
        def check_circular_containment(component_id, visited=None):
            if visited is None:
                visited = set()

            if component_id in visited:
                return True  # Circular reference found

            visited.add(component_id)

            # Check all contained components
            contained = self.get_contained_components(component_id)
            for child in contained:
                if check_circular_containment(child.id, visited.copy()):
                    return True

            return False

        for root_id in self.root_components:
            if check_circular_containment(root_id):
                errors.append(f"Circular containment detected from component {root_id}")

        return len(errors) == 0, errors
```

#### Advanced Data Structures for Spatial Analysis

```python
class SpatialIndex:
    """Spatial indexing for efficient component queries."""
    def __init__(self, grid_width, grid_height, cell_size=5):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size

        # Calculate grid dimensions for spatial index
        self.index_width = (grid_width + cell_size - 1) // cell_size
        self.index_height = (grid_height + cell_size - 1) // cell_size

        # Initialize spatial grid
        self.spatial_grid = [[set() for _ in range(self.index_width)] for _ in range(self.index_height)]

    def add_component(self, component):
        """Add a component to the spatial index."""
        # Get component bounds
        if 'bounding_box' not in component.properties:
            return

        bounds = component.properties['bounding_box']
        x1, y1, x2, y2 = bounds

        # Calculate grid cells that the component overlaps
        cell_x1 = max(0, x1 // self.cell_size)
        cell_y1 = max(0, y1 // self.cell_size)
        cell_x2 = min(self.index_width - 1, x2 // self.cell_size)
        cell_y2 = min(self.index_height - 1, y2 // self.cell_size)

        # Add component to all overlapping cells
        for cy in range(cell_y1, cell_y2 + 1):
            for cx in range(cell_x1, cell_x2 + 1):
                self.spatial_grid[cy][cx].add(component.id)

    def query_point(self, x, y):
        """Query components at a specific point."""
        if not (0 <= x < self.grid_width and 0 <= y < self.grid_height):
            return set()

        cell_x = x // self.cell_size
        cell_y = y // self.cell_size

        return self.spatial_grid[cell_y][cell_x].copy()

    def query_region(self, x1, y1, x2, y2):
        """Query components that overlap with the specified region."""
        # Ensure bounds are within grid
        x1 = max(0, min(x1, self.grid_width - 1))
        y1 = max(0, min(y1, self.grid_height - 1))
        x2 = max(0, min(x2, self.grid_width - 1))
        y2 = max(0, min(y2, self.grid_height - 1))

        # Calculate grid cells that the region overlaps
        cell_x1 = x1 // self.cell_size
        cell_y1 = y1 // self.cell_size
        cell_x2 = min(self.index_width - 1, x2 // self.cell_size)
        cell_y2 = min(self.index_height - 1, y2 // self.cell_size)

        # Collect components from all overlapping cells
        result = set()
        for cy in range(cell_y1, cell_y2 + 1):
            for cx in range(cell_x1, cell_x2 + 1):
                result.update(self.spatial_grid[cy][cx])

        return result

    def rebuild(self, components):
        """Rebuild the spatial index with the provided components."""
        # Clear the spatial grid
        self.spatial_grid = [[set() for _ in range(self.index_width)] for _ in range(self.index_height)]

        # Add all components
        for component in components:
            self.add_component(component)
```

### Data Processing Pipeline

The data processing pipeline will coordinate the flow of data through the system:

```python
class ProcessingPipeline:
    def __init__(self):
        self.processors = []
        self.context = {}
        self.error_handlers = {}
        self.performance_monitors = {}

    def register_processor(self, processor, stage_name):
        """Register a processor for a specific pipeline stage."""
        self.processors.append((stage_name, processor))

    def register_error_handler(self, stage_name, handler):
        """Register an error handler for a specific stage."""
        self.error_handlers[stage_name] = handler

    def register_performance_monitor(self, stage_name, monitor):
        """Register a performance monitor for a specific stage."""
        self.performance_monitors[stage_name] = monitor

    def process(self, input_data, context=None):
        """Process input data through the pipeline."""
        # Initialize or update context
        if context is not None:
            self.context.update(context)

        current_data = input_data
        stage_results = {}

        # Process through each stage
        for stage_name, processor in self.processors:
            try:
                # Start performance monitoring
                if stage_name in self.performance_monitors:
                    self.performance_monitors[stage_name].start()

                # Process data
                stage_result = processor.process(current_data, self.context)

                # End performance monitoring
                if stage_name in self.performance_monitors:
                    self.performance_monitors[stage_name].end()

                # Store result for this stage
                stage_results[stage_name] = stage_result

                # Update current data for next stage
                current_data = stage_result

            except Exception as e:
                # Handle error
                if stage_name in self.error_handlers:
                    handled_data = self.error_handlers[stage_name].handle_error(e, current_data, self.context)

                    if handled_data is not None:
                        # Continue with handled data
                        current_data = handled_data
                    else:
                        # Cannot continue pipeline
                        raise PipelineError(f"Error in stage {stage_name}: {str(e)}")
                else:
                    # No handler, propagate error
                    raise PipelineError(f"Error in stage {stage_name}: {str(e)}")

        # Return the final result and all stage results
        return current_data, stage_results

    def process_incremental(self, delta, context=None):
        """Process an incremental update through the pipeline."""
        # Initialize or update context
        if context is not None:
            self.context.update(context)

        current_delta = delta
        stage_results = {}

        # Process through each stage
        for stage_name, processor in self.processors:
            # Check if processor supports incremental updates
            if hasattr(processor, 'process_incremental'):
                try:
                    # Start performance monitoring
                    if stage_name in self.performance_monitors:
                        self.performance_monitors[stage_name].start()

                    # Process delta
                    stage_result = processor.process_incremental(current_delta, self.context)

                    # End performance monitoring
                    if stage_name in self.performance_monitors:
                        self.performance_monitors[stage_name].end()

                    # Store result for this stage
                    stage_results[stage_name] = stage_result

                    # Update current delta for next stage
                    current_delta = stage_result

                except Exception as e:
                    # Handle error
                    if stage_name in self.error_handlers:
                        handled_delta = self.error_handlers[stage_name].handle_error(e, current_delta, self.context)

                        if handled_delta is not None:
                            # Continue with handled delta
                            current_delta = handled_delta
                        else:
                            # Cannot continue incremental update
                            raise PipelineError(f"Error in incremental update for stage {stage_name}: {str(e)}")
                    else:
                        # No handler, propagate error
                        raise PipelineError(f"Error in incremental update for stage {stage_name}: {str(e)}")
            else:
                # Processor doesn't support incremental updates, need to reprocess
                # This would retrieve the full data from context and process it
                full_data = self.context.get('current_data')
                if full_data is not None:
                    try:
                        # Start performance monitoring
                        if stage_name in self.performance_monitors:
                            self.performance_monitors[stage_name].start()

                        # Process full data
                        stage_result = processor.process(full_data, self.context)

                        # End performance monitoring
                        if stage_name in self.performance_monitors:
                            self.performance_monitors[stage_name].end()

                        # Store result for this stage
                        stage_results[stage_name] = stage_result

                        # Update current data for next stage
                        full_data = stage_result
                        self.context['current_data'] = full_data

                        # Create a new delta representing the full change
                        current_delta = {'type': 'full_update', 'data': full_data}

                    except Exception as e:
                        # Handle error
                        if stage_name in self.error_handlers:
                            handled_data = self.error_handlers[stage_name].handle_error(e, full_data, self.context)

                            if handled_data is not None:
                                # Continue with handled data
                                full_data = handled_data
                                self.context['current_data'] = full_data

                                # Create a new delta representing the full change
                                current_delta = {'type': 'full_update', 'data': full_data}
                            else:
                                # Cannot continue pipeline
                                raise PipelineError(f"Error in stage {stage_name}: {str(e)}")
                        else:
                            # No handler, propagate error
                            raise PipelineError(f"Error in stage {stage_name}: {str(e)}")
                else:
                    # No full data available, cannot continue
                    raise PipelineError(f"Cannot perform incremental update for stage {stage_name}: No full data available")

        # Return the final delta and all stage results
        return current_delta, stage_results

class PipelineError(Exception):
    """Exception raised for errors in the processing pipeline."""
    pass
```

### Data Persistence Framework

The persistence framework will manage saving and loading project data:

```python
class PersistenceManager:
    def __init__(self, storage_provider=None):
        self.storage_provider = storage_provider or FileSystemStorageProvider()
        self.serializers = {}

    def register_serializer(self, data_type, serializer):
        """Register a serializer for a specific data type."""
        self.serializers[data_type] = serializer

    def save_project(self, project_data, project_path):
        """Save project data to the specified path."""
        # Validate project data
        if not isinstance(project_data, dict):
            raise ValueError("Project data must be a dictionary")

        # Prepare serialized data
        serialized_data = {}

        for key, value in project_data.items():
            data_type = type(value).__name__

            if data_type in self.serializers:
                serialized_data[key] = {
                    'type': data_type,
                    'data': self.serializers[data_type].serialize(value)
                }
            else:
                # Use default serialization if no specific serializer
                serialized_data[key] = {
                    'type': data_type,
                    'data': self._default_serialize(value)
                }

        # Save to storage
        self.storage_provider.save(project_path, serialized_data)

    def load_project(self, project_path):
        """Load project data from the specified path."""
        # Load from storage
        serialized_data = self.storage_provider.load(project_path)

        if not isinstance(serialized_data, dict):
            raise ValueError("Invalid project data format")

        # Deserialize data
        project_data = {}

        for key, value_info in serialized_data.items():
            if not isinstance(value_info, dict) or 'type' not in value_info or 'data' not in value_info:
                raise ValueError(f"Invalid data format for key {key}")

            data_type = value_info['type']
            serialized_value = value_info['data']

            if data_type in self.serializers:
                project_data[key] = self.serializers[data_type].deserialize(serialized_value)
            else:
                # Use default deserialization if no specific serializer
                project_data[key] = self._default_deserialize(serialized_value, data_type)

        return project_data

    def _default_serialize(self, value):
        """Default serialization for types without specific serializers."""
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, (list, tuple)):
            return [self._default_serialize(item) for item in value]
        elif isinstance(value, dict):
            return {str(k): self._default_serialize(v) for k, v in value.items()}
        else:
            # For complex types, use their __dict__ if available
            if hasattr(value, '__dict__'):
                return {
                    '__class__': value.__class__.__name__,
                    '__module__': value.__class__.__module__,
                    '__dict__': self._default_serialize(value.__dict__)
                }
            else:
                # Last resort: string representation
                return str(value)

    def _default_deserialize(self, value, data_type):
        """Default deserialization for types without specific deserializers."""
        if data_type in ('str', 'int', 'float', 'bool', 'NoneType'):
            return value
        elif data_type in ('list', 'tuple'):
            result = [self._default_deserialize(item, type(item).__name__) for item in value]
            return tuple(result) if data_type == 'tuple' else result
        elif data_type == 'dict':
            return {k: self._default_deserialize(v, type(v).__name__) for k, v in value.items()}
        else:
            # Complex types - try to reconstruct if we have class info
            if isinstance(value, dict) and '__class__' in value and '__module__' in value and '__dict__' in value:
                try:
                    module = __import__(value['__module__'], fromlist=[value['__class__']])
                    cls = getattr(module, value['__class__'])
                    instance = cls.__new__(cls)

                    # Reconstruct __dict__
                    instance_dict = self._default_deserialize(value['__dict__'], 'dict')
                    instance.__dict__.update(instance_dict)

                    return instance
                except (ImportError, AttributeError):
                    # Fallback: return as dict
                    return value
            else:
                # No class info, return as is
                return value
```

## 5.3 Grid Analysis Subsystem

The Grid Analysis Subsystem will process the ASCII grid to identify boundaries, regions, and components:

### Advanced Flood Fill Implementation

```python
class FloodFillProcessor:
    def __init__(self):
        self.boundary_chars = set('┌┐└┘│─┬┴├┤┼╔╗╚╝║═╦╩╠╣╬┏┓┗┛┃━┳┻┣┫╋╭╮╰╯')

    def process(self, grid_data, context=None):
        """Process a grid to identify enclosed regions using flood fill."""
        if context is None:
            context = {}

        # Convert input to ASCIIGrid if needed
        if not isinstance(grid_data, ASCIIGrid):
            if isinstance(grid_data, str):
                grid = ASCIIGrid(grid_data)
            elif isinstance(grid_data, np.ndarray):
                grid = ASCIIGrid(data=grid_data)
            else:
                raise ValueError("Input must be ASCIIGrid, string, or NumPy array")
        else:
            grid = grid_data

        # Get NumPy array for processing
        grid_array = grid.to_numpy()
        height, width = grid_array.shape

        # Initialize visited mask and result list
        visited = np.zeros((height, width), dtype=bool)
        boundary_mask = grid.get_boundary_mask()

        # Mark boundaries as visited
        visited[boundary_mask] = True

        # Store detected components
        components = []

        # Process all cells
        for y in range(height):
            for x in range(width):
                if not visited[y, x]:
                    # Perform flood fill from this seed point
                    component = self._flood_fill(grid_array, visited, x, y)

                    if component:
                        # Add component to results
                        components.append(component)

                        # Mark all points as visited
                        for px, py in component['interior_points']:
                            visited[py, px] = True

        # Post-process components
        processed_components = self._process_components(components, grid_array)

        # Store in context for other stages
        context['flood_fill_results'] = processed_components

        return processed_components

    def _flood_fill(self, grid_array, visited, start_x, start_y):
        """Perform flood fill from a starting point."""
        height, width = grid_array.shape
        queue = [(start_x, start_y)]
        interior_points = set([(start_x, start_y)])
        boundary_points = set()

        # Process all connected points
        while queue:
            x, y = queue.pop(0)

            # Check neighbors in all 4 directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy

                # Check if in bounds
                if 0 <= nx < width and 0 <= ny < height:
                    if visited[ny, nx]:
                        # If it's a boundary character, add to boundary points
                        if grid_array[ny, nx] in self.boundary_chars:
                            boundary_points.add((nx, ny))
                    else:
                        # Mark as visited
                        visited[ny, nx] = True

                        # Add to queue and interior points
                        queue.append((nx, ny))
                        interior_points.add((nx, ny))

        # Only create a component if we have boundary points
        if boundary_points:
            # Calculate bounding box
            if interior_points:
                x_coords = [x for x, y in interior_points]
                y_coords = [y for x, y in interior_points]

                min_x = min(x_coords)
                max_x = max(x_coords)
                min_y = min(y_coords)
                max_y = max(y_coords)

                # Create component
                component = {
                    'interior_points': interior_points,
                    'boundary_points': boundary_points,
                    'bounding_box': (min_x, min_y, max_x, max_y),
                    'width': max_x - min_x + 1,
                    'height': max_y - min_y + 1
                }

                return component

        return None

    def _process_components(self, components, grid_array):
        """Post-process detected components to extract additional information."""
        processed_components = []

        for i, component in enumerate(components):
            # Assign ID
            component['id'] = f"component_{i}"

            # Extract content
            content = self._extract_component_content(component, grid_array)
            component['content'] = content

            # Determine component type based on boundary characters
            component_type = self._determine_component_type(component, grid_array)
            component['type'] = component_type

            # Extract special features
            special_features = self._extract_special_features(component, grid_array)
            component['special_features'] = special_features

            processed_components.append(component)

        return processed_components

    def _extract_component_content(self, component, grid_array):
        """Extract the content (characters) from a component's interior."""
        # Get bounding box
        min_x, min_y, max_x, max_y = component['bounding_box']

        # Extract content rows
        content_rows = []
        for y in range(min_y, max_y + 1):
            row = []
            for x in range(min_x, max_x + 1):
                if (x, y) in component['interior_points']:
                    row.append(grid_array[y, x])
            if row:
                content_rows.append(''.join(row))

        return content_rows

    def _determine_component_type(self, component, grid_array):
        """Determine the type of component based on boundary characters."""
        # Extract boundary characters
        boundary_chars = [grid_array[y, x] for x, y in component['boundary_points']]
        char_set = set(boundary_chars)

        # Check for specific boundary patterns
        if all(c in '┌┐└┘│─' for c in char_set):
            return 'single_line_box'
        elif all(c in '╔╗╚╝║═' for c in char_set):
            return 'double_line_box'
        elif all(c in '┏┓┗┛┃━' for c in char_set):
            return 'heavy_line_box'
        elif all(c in '╭╮╰╯│─' for c in char_set):
            return 'rounded_box'
        else:
            return 'custom_box'

    def _extract_special_features(self, component, grid_array):
        """Extract special features from a component."""
        # Look for special characters in content
        special_features = {}

        # Check for button markers [text]
        content_text = ' '.join(component['content'])
        if re.search(r'\[.*\]', content_text):
            special_features['button_text'] = re.findall(r'\[(.*?)\]', content_text)
            special_features['is_button'] = True

        # Check for other special indicators
        special_chars = {
            '●': 'active_indicator',
            '○': 'inactive_indicator',
            '▼': 'dropdown_expanded',
            '▶': 'dropdown_collapsed',
            '□': 'checkbox_unchecked',
            '■': 'checkbox_checked',
            '☐': 'checkbox_unchecked',
            '☑': 'checkbox_checked'
        }

        for char, feature in special_chars.items():
            if any(char in row for row in component['content']):
                special_features[feature] = True

        return special_features

    def process_incremental(self, delta, context):
        """Process incremental updates to the grid."""
        # Check if we have the original grid in context
        if 'grid' not in context:
            raise ValueError("Cannot process incremental update without original grid in context")

        # Get the original grid
        original_grid = context['grid']

        # Apply the delta to create a new grid
        if delta['type'] == 'character_change':
            # Single character change
            x, y, new_char = delta['data']
            updated_grid = original_grid.copy()
            updated_grid.set_char(x, y, new_char)

        elif delta['type'] == 'region_change':
            # Region change
            x1, y1, x2, y2, new_content = delta['data']
            updated_grid = original_grid.copy()

            # Apply new content to region
            for y, row in enumerate(new_content):
                for x, char in enumerate(row):
                    if 0 <= x1 + x < updated_grid.width and 0 <= y1 + y < updated_grid.height:
                        updated_grid.set_char(x1 + x, y1 + y, char)

        elif delta['type'] == 'full_update':
            # Full grid update
            updated_grid = delta['data']

        else:
            raise ValueError(f"Unknown delta type: {delta['type']}")

        # Process the updated grid
        result = self.process(updated_grid, context)

        # Update the grid in context
        context['grid'] = updated_grid

        return result
```

### Contour Detection System

```python
class ContourDetectionProcessor:
    def __init__(self):
        pass

    def process(self, components, context=None):
        """Process components to detect precise contours."""
        if context is None:
            context = {}

        # Ensure we have a grid available
        if 'grid' not in context:
            raise ValueError("Grid not available in context")

        grid = context['grid']

        # Process each component
        for component in components:
            # Create a binary mask for this component
            mask = self._create_component_mask(component, grid)

            # Detect contours in the mask
            contours = self._detect_contours(mask)

            # Add contours to component
            component['contours'] = contours

            # Refine bounding box based on contours
            if contours:
                refined_box = self._refine_bounding_box(contours)
                component['refined_bounding_box'] = refined_box

        # Store in context for other stages
        context['contour_detection_results'] = components

        return components

    def _create_component_mask(self, component, grid):
        """Create a binary mask for a component."""
        # Get bounding box
        min_x, min_y, max_x, max_y = component['bounding_box']

        # Create mask
        mask = np.zeros((max_y - min_y + 3, max_x - min_x + 3), dtype=np.uint8)

        # Fill mask with boundary points
        for x, y in component['boundary_points']:
            mask[y - min_y + 1, x - min_x + 1] = 255

        return mask

    def _detect_contours(self, mask):
        """Detect contours in a binary mask using OpenCV."""
        try:
            import cv2

            # Apply morphological operations to clean up the mask
            kernel = np.ones((2, 2), np.uint8)
            mask_processed = cv2.dilate(mask, kernel, iterations=1)

            # Find contours
            contours, hierarchy = cv2.findContours(mask_processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Convert contours to a serializable format
            serializable_contours = []
            for contour in contours:
                points = []
                for point in contour:
                    x, y = point[0]
                    points.append((int(x), int(y)))
                serializable_contours.append(points)

            return serializable_contours
        except ImportError:
            # Fall back to simpler method if OpenCV not available
            return self._detect_contours_simple(mask)

    def _detect_contours_simple(self, mask):
        """Simplified contour detection without OpenCV."""
        height, width = mask.shape
        visited = np.zeros_like(mask, dtype=bool)
        contours = []

        # Scan for boundary points
        for y in range(height):
            for x in range(width):
                if mask[y, x] > 0 and not visited[y, x]:
                    # Start of a new contour
                    contour = []
                    current_x, current_y = x, y
                    direction = 0  # 0: right, 1: down, 2: left, 3: up

                    # Trace the contour
                    for _ in range(width * height):  # Safety limit
                        contour.append((current_x, current_y))
                        visited[current_y, current_x] = True

                        # Try to turn right first (relative to current direction)
                        turned = False
                        for _ in range(4):  # Try all directions
                            new_direction = (direction - 1) % 4
                            dx, dy = [(1, 0), (0, 1), (-1, 0), (0, -1)][new_direction]
                            new_x, new_y = current_x + dx, current_y + dy

                            if (0 <= new_x < width and 0 <= new_y < height and
                                mask[new_y, new_x] > 0 and not visited[new_y, new_x]):
                                current_x, current_y = new_x, new_y
                                direction = new_direction
                                turned = True
                                break

                            direction = (direction + 1) % 4

                        if not turned:
                            break

                        # Check if we've returned to start
                        if current_x == x and current_y == y:
                            break

                    if len(contour) > 2:
                        contours.append(contour)

        return contours

    def _refine_bounding_box(self, contours):
        """Refine the bounding box based on contours."""
        if not contours:
            return None

        # Flatten all contours
        all_points = [point for contour in contours for point in contour]

        # Find min/max coordinates
        x_coords = [x for x, y in all_points]
        y_coords = [y for x, y in all_points]

        min_x = min(x_coords)
        max_x = max(x_coords)
        min_y = min(y_coords)
        max_y = max(y_coords)

        return (min_x, min_y, max_x, max_y)
```

### Pattern Recognition System

```python
class PatternRecognitionProcessor:
    def __init__(self):
        self.pattern_matchers = {}

    def register_pattern_matcher(self, name, matcher):
        """Register a pattern matcher."""
        self.pattern_matchers[name] = matcher

    def process(self, components, context=None):
        """Process components to recognize UI patterns."""
        if context is None:
            context = {}

        # Ensure we have a grid available
        if 'grid' not in context:
            raise ValueError("Grid not available in context")

        grid = context['grid']

        # Apply all registered pattern matchers
        for name, matcher in self.pattern_matchers.items():
            for component in components:
                pattern_matches = matcher.match(component, grid)

                if pattern_matches:
                    # Add pattern matches to component
                    if 'pattern_matches' not in component:
                        component['pattern_matches'] = {}

                    component['pattern_matches'][name] = pattern_matches

                    # Apply pattern-specific attributes
                    self._apply_pattern_attributes(component, name, pattern_matches)

        # Store in context for other stages
        context['pattern_recognition_results'] = components

        return components

    def _apply_pattern_attributes(self, component, pattern_name, matches):
        """Apply pattern-specific attributes to a component."""
        if pattern_name == 'button':
            component['is_button'] = True

            if 'text' in matches:
                component['button_text'] = matches['text']

        elif pattern_name == 'checkbox':
            component['is_checkbox'] = True

            if 'state' in matches:
                component['checkbox_state'] = matches['state']

        elif pattern_name == 'radio_button':
            component['is_radio_button'] = True

            if 'state' in matches:
                component['radio_state'] = matches['state']

            if 'group' in matches:
                component['radio_group'] = matches['group']

        elif pattern_name == 'text_field':
            component['is_text_field'] = True

            if 'text' in matches:
                component['field_text'] = matches['text']

            if 'placeholder' in matches:
                component['placeholder_text'] = matches['placeholder']

        elif pattern_name == 'dropdown':
            component['is_dropdown'] = True

            if 'text' in matches:
                component['dropdown_text'] = matches['text']

            if 'state' in matches:
                component['dropdown_state'] = matches['state']

        elif pattern_name == 'window':
            component['is_window'] = True

            if 'title' in matches:
                component['window_title'] = matches['title']

        # Add more pattern-specific attributes for other UI element types
```

## 5.4 Component Recognition Engine

The Component Recognition Engine will identify UI components from the grid analysis results:

### Feature Extraction System

```python
class FeatureExtractionProcessor:
    def __init__(self):
        self.feature_extractors = {}

    def register_feature_extractor(self, name, extractor):
        """Register a feature extractor."""
        self.feature_extractors[name] = extractor

    def process(self, components, context=None):
        """Extract features from components."""
        if context is None:
            context = {}

        # Ensure we have a grid available
        if 'grid' not in context:
            raise ValueError("Grid not available in context")

        grid = context['grid']

        # Process each component
        for component in components:
            # Initialize features dictionary
            if 'features' not in component:
                component['features'] = {}

            # Apply all registered feature extractors
            for name, extractor in self.feature_extractors.items():
                features = extractor.extract(component, grid, context)

                if features:
                    # Add features to component
                    component['features'][name] = features

        # Store in context for other stages
        context['feature_extraction_results'] = components

        return components
```

### Component Classification System

```python
class ComponentClassificationProcessor:
    def __init__(self):
        self.classifiers = {}
        self.default_classifier = None

    def register_classifier(self, component_type, classifier):
        """Register a classifier for a specific component type."""
        self.classifiers[component_type] = classifier

    def set_default_classifier(self, classifier):
        """Set the default classifier for components without a specific classifier."""
        self.default_classifier = classifier

    def process(self, components, context=None):
        """Classify components based on their features."""
        if context is None:
            context = {}

        # Process each component
        for component in components:
            # Get preliminary type information
            preliminary_type = component.get('type', 'unknown')

            # Select appropriate classifier
            classifier = self.classifiers.get(preliminary_type, self.default_classifier)

            if classifier:
                # Classify the component
                classification_result = classifier.classify(component, context)

                if classification_result:
                    # Update component with classification result
                    component.update(classification_result)

        # Store in context for other stages
        context['component_classification_results'] = components

        return components
```

### Component Relationship Analysis

```python
class RelationshipAnalysisProcessor:
    def __init__(self):
        self.relationship_analyzers = []

    def register_relationship_analyzer(self, analyzer):
        """Register a relationship analyzer."""
        self.relationship_analyzers.append(analyzer)

    def process(self, components, context=None):
        """Analyze relationships between components."""
        if context is None:
            context = {}

        # Create component model
        component_model = ComponentModel()

        # Add components to model
        for component in components:
            # Create AbstractComponent
            abstract_component = AbstractComponent(component.get('id', str(uuid.uuid4())), component.get('ui_type', 'unknown'))

            # Add properties
            for key, value in component.items():
                if key not in ('id', 'type', 'ui_type'):
                    abstract_component.add_property(key, value)

            # Add to model
            component_model.add_component(abstract_component)

        # Apply all relationship analyzers
        for analyzer in self.relationship_analyzers:
            analyzer.analyze(component_model, context)

        # Validate the model
        valid, errors = component_model.validate()

        if not valid:
            # Log validation errors
            for error in errors:
                print(f"Validation error: {error}")

        # Store in context for other stages
        context['component_model'] = component_model
        context['relationship_analysis_results'] = component_model

        return component_model
```

## 5.5 Hierarchical Modeling System

The Hierarchical Modeling System will establish the component hierarchy:

### Containment Analysis

```python
class ContainmentAnalyzer:
    def __init__(self):
        pass

    def analyze(self, component_model, context=None):
        """Analyze containment relationships between components."""
        if context is None:
            context = {}

        # Get all components
        components = list(component_model.components.values())

        # Create spatial index for efficient querying
        spatial_index = self._create_spatial_index(components)

        # Analyze containment relationships
        self._analyze_containment(components, component_model, spatial_index)

        return component_model

    def _create_spatial_index(self, components):
        """Create a spatial index for the components."""
        # Determine grid dimensions
        max_x = max_y = 0

        for component in components:
            if 'bounding_box' in component.properties:
                bb = component.properties['bounding_box']
                max_x = max(max_x, bb[2])
                max_y = max(max_y, bb[3])

        # Create spatial index
        index = SpatialIndex(max_x + 1, max_y + 1)

        # Add components to index
        for component in components:
            index.add_component(component)

        return index

    def _analyze_containment(self, components, component_model, spatial_index):
        """Analyze containment relationships between components."""
        # Sort components by area (largest first)
        components.sort(key=lambda c: self._get_component_area(c), reverse=True)

        # Build containment graph
        for outer_component in components:
            outer_bb = self._get_bounding_box(outer_component)

            if not outer_bb:
                continue

            x1, y1, x2, y2 = outer_bb

            # Query spatial index for potential contained components
            potential_contained_ids = spatial_index.query_region(x1, y1, x2, y2)

            for inner_id in potential_contained_ids:
                inner_component = component_model.get_component(inner_id)

                if inner_component and inner_component.id != outer_component.id:
                    inner_bb = self._get_bounding_box(inner_component)

                    if not inner_bb:
                        continue

                    # Check if inner component is fully contained
                    if self._is_contained(inner_bb, outer_bb):
                        # Add containment relationship
                        component_model.add_relationship(outer_component.id, inner_component.id, 'contains')

    def _get_bounding_box(self, component):
        """Get the bounding box of a component."""
        if 'refined_bounding_box' in component.properties:
            return component.properties['refined_bounding_box']
        elif 'bounding_box' in component.properties:
            return component.properties['bounding_box']
        return None

    def _get_component_area(self, component):
        """Get the area of a component."""
        bb = self._get_bounding_box(component)

        if bb:
            x1, y1, x2, y2 = bb
            return (x2 - x1 + 1) * (y2 - y1 + 1)
        return 0

    def _is_contained(self, inner_bb, outer_bb):
        """Check if inner bounding box is contained within outer bounding box."""
        ix1, iy1, ix2, iy2 = inner_bb
        ox1, oy1, ox2, oy2 = outer_bb

        # Inner must be fully contained with some margin
        margin = 1
        return (ox1 + margin <= ix1 <= ix2 <= ox2 - margin and
                oy1 + margin <= iy1 <= iy2 <= oy2 - margin)
```

### Functional Relationship Analysis

```python
class FunctionalRelationshipAnalyzer:
    def __init__(self):
        self.relationship_patterns = []

    def register_relationship_pattern(self, pattern):
        """Register a relationship pattern."""
        self.relationship_patterns.append(pattern)

    def analyze(self, component_model, context=None):
        """Analyze functional relationships between components."""
        if context is None:
            context = {}

        # Apply all relationship patterns
        for pattern in self.relationship_patterns:
            pattern.apply(component_model, context)

        return component_model
```

### Layout Analysis

```python
class LayoutAnalyzer:
    def __init__(self):
        pass

    def analyze(self, component_model, context=None):
        """Analyze layout relationships between components."""
        if context is None:
            context = {}

        # Analyze alignment relationships
        self._analyze_alignment(component_model)

        # Analyze grid arrangements
        self._analyze_grid_arrangement(component_model)

        # Analyze flow arrangements
        self._analyze_flow_arrangement(component_model)

        return component_model

    def _analyze_alignment(self, component_model):
        """Analyze alignment relationships between components."""
        # Get all components
        components = list(component_model.components.values())

        # Group components by containers
        container_groups = {}

        for component in components:
            container = component_model.get_container(component.id)

            if container:
                container_id = container.id
                if container_id not in container_groups:
                    container_groups[container_id] = []
                container_groups[container_id].append(component)

        # Analyze alignment within each container
        for container_id, container_components in container_groups.items():
            self._analyze_group_alignment(container_components, component_model)

    def _analyze_group_alignment(self, components, component_model):
        """Analyze alignment within a group of components."""
        # Skip if too few components
        if len(components) < 2:
            return

        # Sort components by position
        components_with_bb = [(c, self._get_bounding_box(c)) for c in components if self._get_bounding_box(c)]

        if not components_with_bb:
            return

        # Analyze horizontal alignment
        h_aligned_groups = self._find_aligned_groups(components_with_bb, 'horizontal')

        for group in h_aligned_groups:
            if len(group) >= 2:
                # Add 'alignsHorizontally' relationship between components
                first_component = group[0][0]

                for i in range(1, len(group)):
                    component_model.add_relationship(first_component.id, group[i][0].id, 'alignsHorizontally')

        # Analyze vertical alignment
        v_aligned_groups = self._find_aligned_groups(components_with_bb, 'vertical')

        for group in v_aligned_groups:
            if len(group) >= 2:
                # Add 'alignsVertically' relationship between components
                first_component = group[0][0]

                for i in range(1, len(group)):
                    component_model.add_relationship(first_component.id, group[i][0].id, 'alignsVertically')

    def _find_aligned_groups(self, components_with_bb, alignment_type):
        """Find groups of aligned components."""
        aligned_groups = []

        if alignment_type == 'horizontal':
            # Group by y-coordinate
            groups_by_y = {}

            for comp, bb in components_with_bb:
                y_mid = (bb[1] + bb[3]) // 2

                if y_mid not in groups_by_y:
                    groups_by_y[y_mid] = []

                groups_by_y[y_mid].append((comp, bb))

            # Create aligned groups (allow small variations)
            processed = set()

            for y in sorted(groups_by_y.keys()):
                if y in processed:
                    continue

                # Find similar y-values
                aligned_group = groups_by_y[y]

                for y2 in range(y + 1, y + 3):
                    if y2 in groups_by_y:
                        aligned_group.extend(groups_by_y[y2])
                        processed.add(y2)

                if len(aligned_group) >= 2:
                    # Sort by x-coordinate
                    aligned_group.sort(key=lambda item: item[1][0])
                    aligned_groups.append(aligned_group)

        elif alignment_type == 'vertical':
            # Group by x-coordinate
            groups_by_x = {}

            for comp, bb in components_with_bb:
                x_mid = (bb[0] + bb[2]) // 2

                if x_mid not in groups_by_x:
                    groups_by_x[x_mid] = []

                groups_by_x[x_mid].append((comp, bb))

            # Create aligned groups (allow small variations)
            processed = set()

            for x in sorted(groups_by_x.keys()):
                if x in processed:
                    continue

                # Find similar x-values
                aligned_group = groups_by_x[x]

                for x2 in range(x + 1, x + 3):
                    if x2 in groups_by_x:
                        aligned_group.extend(groups_by_x[x2])
                        processed.add(x2)

                if len(aligned_group) >= 2:
                    # Sort by y-coordinate
                    aligned_group.sort(key=lambda item: item[1][1])
                    aligned_groups.append(aligned_group)

        return aligned_groups

    def _get_bounding_box(self, component):
        """Get the bounding box of a component."""
        if 'refined_bounding_box' in component.properties:
            return component.properties['refined_bounding_box']
        elif 'bounding_box' in component.properties:
            return component.properties['bounding_box']
        return None

    def _analyze_grid_arrangement(self, component_model):
        """Analyze grid arrangements of components."""
        # Get all containers
        for container_id in list(component_model.components.keys()):
            # Get contained components
            contained = component_model.get_contained_components(container_id)

            if len(contained) < 4:  # Need at least 4 components for a grid
                continue

            # Check if components form a grid
            grid_info = self._check_grid_arrangement(contained)

            if grid_info:
                # Add grid arrangement to container
                container = component_model.get_component(container_id)
                container.add_property('layout', 'grid')
                container.add_property('grid_info', grid_info)

    def _check_grid_arrangement(self, components):
        """Check if components form a grid arrangement."""
        # Get components with bounding boxes
        components_with_bb = [(c, self._get_bounding_box(c)) for c in components if self._get_bounding_box(c)]

        if len(components_with_bb) < 4:
            return None

        # Extract row and column positions
        row_positions = set()
        col_positions = set()

        for comp, bb in components_with_bb:
            y_mid = (bb[1] + bb[3]) // 2
            x_mid = (bb[0] + bb[2]) // 2

            row_positions.add(y_mid)
            col_positions.add(x_mid)

        # Check if we have at least 2 rows and 2 columns
        if len(row_positions) < 2 or len(col_positions) < 2:
            return None

        # Sort positions
        rows = sorted(row_positions)
        cols = sorted(col_positions)

        # Check if number of components matches grid size
        grid_size = len(rows) * len(cols)

        if len(components_with_bb) < grid_size * 0.8:  # Allow some missing cells
            return None

        # Create a mapping of components to grid cells
        grid_map = {}

        for comp, bb in components_with_bb:
            y_mid = (bb[1] + bb[3]) // 2
            x_mid = (bb[0] + bb[2]) // 2

            row_idx = self._find_nearest_index(y_mid, rows)
            col_idx = self._find_nearest_index(x_mid, cols)

            grid_map[(row_idx, col_idx)] = comp.id

        return {
            'rows': len(rows),
            'columns': len(cols),
            'grid_map': grid_map
        }

    def _find_nearest_index(self, value, positions):
        """Find the index of the nearest position."""
        return min(range(len(positions)), key=lambda i: abs(positions[i] - value))

    def _analyze_flow_arrangement(self, component_model):
        """Analyze flow arrangements of components."""
        # Get all containers
        for container_id in list(component_model.components.keys()):
            # Get contained components
            contained = component_model.get_contained_components(container_id)

            if len(contained) < 2:  # Need at least 2 components for a flow
                continue

            # Get components with bounding boxes
            components_with_bb = [(c, self._get_bounding_box(c)) for c in contained if self._get_bounding_box(c)]

            if len(components_with_bb) < 2:
                continue

            # Check for horizontal flow
            h_flow = self._check_horizontal_flow(components_with_bb)

            if h_flow:
                # Add horizontal flow arrangement to container
                container = component_model.get_component(container_id)
                container.add_property('layout', 'horizontal_flow')
                container.add_property('flow_info', h_flow)
                continue

            # Check for vertical flow
            v_flow = self._check_vertical_flow(components_with_bb)

            if v_flow:
                # Add vertical flow arrangement to container
                container = component_model.get_component(container_id)
                container.add_property('layout', 'vertical_flow')
                container.add_property('flow_info', v_flow)

    def _check_horizontal_flow(self, components_with_bb):
        """Check if components form a horizontal flow arrangement."""
        # Sort by x-coordinate
        sorted_components = sorted(components_with_bb, key=lambda item: item[1][0])

        # Check if components are arranged horizontally
        avg_width = sum((bb[2] - bb[0]) for _, bb in sorted_components) / len(sorted_components)

        # Check that components have similar y-positions
        y_mids = [(bb[1] + bb[3]) // 2 for _, bb in sorted_components]
        y_variance = max(y_mids) - min(y_mids)

        if y_variance > avg_width * 0.5:  # Allow some vertical variation
            return None

        # Check for consistent spacing
        spacings = []
        for i in range(1, len(sorted_components)):
            prev_bb = sorted_components[i-1][1]
            curr_bb = sorted_components[i][1]

            spacing = curr_bb[0] - prev_bb[2]
            spacings.append(spacing)

        avg_spacing = sum(spacings) / len(spacings) if spacings else 0
        spacing_variance = max(abs(s - avg_spacing) for s in spacings) if spacings else 0

        if spacing_variance > avg_width * 0.3:  # Allow some spacing variation
            return None

        # Create flow information
        flow_map = {}

        for i, (comp, _) in enumerate(sorted_components):
            flow_map[i] = comp.id

        return {
            'direction': 'horizontal',
            'components': len(sorted_components),
            'flow_map': flow_map,
            'avg_spacing': avg_spacing
        }

    def _check_vertical_flow(self, components_with_bb):
        """Check if components form a vertical flow arrangement."""
        # Sort by y-coordinate
        sorted_components = sorted(components_with_bb, key=lambda item: item[1][1])

        # Check if components are arranged vertically
        avg_height = sum((bb[3] - bb[1]) for _, bb in sorted_components) / len(sorted_components)

        # Check that components have similar x-positions
        x_mids = [(bb[0] + bb[2]) // 2 for _, bb in sorted_components]
        x_variance = max(x_mids) - min(x_mids)

        if x_variance > avg_height * 0.5:  # Allow some horizontal variation
            return None

        # Check for consistent spacing
        spacings = []
        for i in range(1, len(sorted_components)):
            prev_bb = sorted_components[i-1][1]
            curr_bb = sorted_components[i][1]

            spacing = curr_bb[1] - prev_bb[3]
            spacings.append(spacing)

        avg_spacing = sum(spacings) / len(spacings) if spacings else 0
        spacing_variance = max(abs(s - avg_spacing) for s in spacings) if spacings else 0

        if spacing_variance > avg_height * 0.3:  # Allow some spacing variation
            return None

        # Create flow information
        flow_map = {}

        for i, (comp, _) in enumerate(sorted_components):
            flow_map[i] = comp.id

        return {
            'direction': 'vertical',
            'components': len(sorted_components),
            'flow_map': flow_map,
            'avg_spacing': avg_spacing
        }
```

## 5.6 Code Generation Framework

The Code Generation Framework will transform the component model into framework-specific code:

### Abstract Code Generation System

```python
class CodeGenerationProcessor:
    def __init__(self):
        self.framework_generators = {}

    def register_framework_generator(self, framework_name, generator):
        """Register a code generator for a specific framework."""
        self.framework_generators[framework_name] = generator

    def process(self, component_model, context=None):
        """Generate code for the given component model."""
        if context is None:
            context = {}

        # Get target framework
        framework = context.get('target_framework', 'default')

        # Check if we have a generator for this framework
        if framework not in self.framework_generators:
            raise ValueError(f"No code generator registered for framework: {framework}")

        # Get generator options from context
        options = context.get('generator_options', {})

        # Generate code
        generator = self.framework_generators[framework]
        generated_code = generator.generate(component_model, options)

        # Store in context for other stages
        context['generated_code'] = generated_code

        return generated_code
```

### Framework-Specific Code Generators

```python
class PythonTkinterGenerator:
    def __init__(self):
        self.template_registry = {}
        self.default_template = None

    def register_template(self, component_type, template):
        """Register a template for a specific component type."""
        self.template_registry[component_type] = template

    def set_default_template(self, template):
        """Set the default template for components without a specific template."""
        self.default_template = template

    def generate(self, component_model, options=None):
        """Generate Tkinter code for the given component model."""
        if options is None:
            options = {}

        # Start with imports
        code_parts = [
            "import tkinter as tk",
            "from tkinter import ttk\n",
            "class Application(tk.Tk):",
            "    def __init__(self):",
            "        super().__init__()",
            "        self.title('ASCII UI Application')",
            "        self.geometry('800x600')",
            "        self.create_widgets()\n",
            "    def create_widgets(self):"
        ]

        # Get the component hierarchy
        hierarchy = component_model.get_hierarchy()

        # Generate code for each root component
        for root_id, node in hierarchy.items():
            component_code = self._generate_component_code(node, "        ", options)
            code_parts.extend(component_code)

        # Add main function
        code_parts.extend([
            "\n",
            "if __name__ == '__main__':",
            "    app = Application()",
            "    app.mainloop()"
        ])

        # Join all code parts
        return "\n".join(code_parts)

    def _generate_component_code(self, node, indent, options):
        """Generate code for a component and its children."""
        component = node['component']
        children = node['children']

        # Get component type
        component_type = component.type

        # Get appropriate template
        template = self.template_registry.get(component_type, self.default_template)

        if not template:
            # Skip if no template
            return []

        # Generate code for this component
        try:
            component_code = template.render(component, indent, options)
        except Exception as e:
            # Log error and return empty list
            print(f"Error generating code for component {component.id}: {str(e)}")
            return []

        code_parts = component_code.split('\n')

        # Generate code for children
        for child_node in children:
            child_code = self._generate_component_code(child_node, indent + "    ", options)
            code_parts.extend(child_code)

        return code_parts
```

### Template System

```python
class CodeTemplate:
    def __init__(self, template_text):
        self.template_text = template_text
        self.placeholders = self._extract_placeholders(template_text)

    def render(self, component, indent='', options=None):
        """Render the template for a component."""
        if options is None:
            options = {}

        # Create context for rendering
        context = {
            'component': component,
            'options': options,
            'indent': indent
        }

        # Replace placeholders
        rendered_text = self.template_text

        for placeholder in self.placeholders:
            value = self._evaluate_placeholder(placeholder, context)
            rendered_text = rendered_text.replace(f"{{{placeholder}}}", str(value))

        # Apply indentation
        indented_text = self._apply_indentation(rendered_text, indent)

        return indented_text

    def _extract_placeholders(self, template_text):
        """Extract placeholders from template text."""
        placeholders = []
        current_pos = 0

        while True:
            start_pos = template_text.find('{', current_pos)

            if start_pos == -1:
                break

            end_pos = template_text.find('}', start_pos)

            if end_pos == -1:
                break

            placeholder = template_text[start_pos+1:end_pos]
            placeholders.append(placeholder)

            current_pos = end_pos + 1

        return placeholders

    def _evaluate_placeholder(self, placeholder, context):
        """Evaluate a placeholder in the given context."""
        component = context['component']
        options = context['options']

        if placeholder.startswith('component.'):
            # Component property
            prop_name = placeholder[len('component.'):]
            return component.properties.get(prop_name, '')

        elif placeholder.startswith('options.'):
            # Option value
            option_name = placeholder[len('options.'):]
            return options.get(option_name, '')

        elif placeholder == 'component.id':
            # Component ID
            return component.id

        elif placeholder == 'component.type':
            # Component type
            return component.type

        # Special placeholders
        if placeholder == 'var_name':
            # Generate variable name
            return f"{component.type.lower()}_{component.id}"

        return ''

    def _apply_indentation(self, text, indent):
        """Apply indentation to text."""
        lines = text.split('\n')
        indented_lines = [indent + line for line in lines]
        return '\n'.join(indented_lines)
```

### Layout Management

```python
class LayoutManager:
    def __init__(self):
        self.layout_handlers = {}

    def register_layout_handler(self, layout_type, handler):
        """Register a layout handler for a specific layout type."""
        self.layout_handlers[layout_type] = handler

    def generate_layout_code(self, component, children, indent='', options=None):
        """Generate layout code for a component and its children."""
        if options is None:
            options = {}

        # Get layout type
        layout_type = component.properties.get('layout', 'default')

        # Get appropriate handler
        handler = self.layout_handlers.get(layout_type)

        if not handler:
            # Use default positioning
            return self._generate_default_layout(component, children, indent, options)

        # Generate layout code
        return handler.generate_layout_code(component, children, indent, options)

    def _generate_default_layout(self, component, children, indent, options):
        """Generate default layout code with absolute positioning."""
        code_parts = []

        for child in children:
            # Get child position
            x = child.properties.get('x', 0)
            y = child.properties.get('y', 0)

            # Generate positioning code
            var_name = f"{child.type.lower()}_{child.id}"
            code_parts.append(f"{indent}{var_name}.place(x={x}, y={y})")

        return '\n'.join(code_parts)
```

## 5.7 Extension Management System

The Extension Management System will provide mechanisms for extending and customizing system behavior:

### Plugin System

```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.extension_points = {}

    def register_plugin(self, plugin_name, plugin):
        """Register a plugin."""
        self.plugins[plugin_name] = plugin

        # Register plugin with extension points
        for ext_point, ext_impl in plugin.get_extensions().items():
            self.register_extension(ext_point, plugin_name, ext_impl)

    def register_extension_point(self, ext_point_name, ext_point):
        """Register an extension point."""
        self.extension_points[ext_point_name] = ext_point

    def register_extension(self, ext_point_name, plugin_name, ext_impl):
        """Register an extension for an extension point."""
        if ext_point_name not in self.extension_points:
            raise ValueError(f"Unknown extension point: {ext_point_name}")

        self.extension_points[ext_point_name].register_extension(plugin_name, ext_impl)

    def get_plugins(self):
        """Get all registered plugins."""
        return self.plugins

    def get_plugin(self, plugin_name):
        """Get a plugin by name."""
        return self.plugins.get(plugin_name)

    def get_extension_points(self):
        """Get all registered extension points."""
        return self.extension_points

    def get_extension_point(self, ext_point_name):
        """Get an extension point by name."""
        return self.extension_points.get(ext_point_name)

    def load_plugin_from_file(self, plugin_path):
        """Load a plugin from a file."""
        import importlib.util

        # Load module from file
        module_name = os.path.basename(plugin_path).replace('.py', '')
        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Create plugin instance
        if hasattr(module, 'create_plugin'):
            plugin = module.create_plugin()
            plugin_name = plugin.get_name()

            # Register plugin
            self.register_plugin(plugin_name, plugin)

            return plugin_name
        else:
            raise ValueError(f"Invalid plugin file: {plugin_path}")
```

### Extension Point System

```python
class ExtensionPoint:
    def __init__(self, name):
        self.name = name
        self.extensions = {}

    def register_extension(self, plugin_name, extension):
        """Register an extension."""
        self.extensions[plugin_name] = extension

    def get_extensions(self):
        """Get all registered extensions."""
        return self.extensions

    def get_extension(self, plugin_name):
        """Get an extension by plugin name."""
        return self.extensions.get(plugin_name)

    def invoke(self, method_name, *args, **kwargs):
        """Invoke a method on all extensions."""
        results = {}

        for plugin_name, extension in self.extensions.items():
            if hasattr(extension, method_name):
                method = getattr(extension, method_name)
                try:
                    results[plugin_name] = method(*args, **kwargs)
                except Exception as e:
                    # Log error and continue
                    print(f"Error invoking {method_name} on extension {plugin_name}: {str(e)}")

        return results
```

### Configuration System

```python
class ConfigurationManager:
    def __init__(self):
        self.config = {}

    def load_config(self, config_path):
        """Load configuration from a file."""
        import json

        with open(config_path, 'r') as f:
            config_data = json.load(f)

        self.config.update(config_data)

    def save_config(self, config_path):
        """Save configuration to a file."""
        import json

        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_config(self, section=None):
        """Get configuration data."""
        if section is not None:
            return self.config.get(section, {})
        return self.config

    def set_config(self, section, key, value):
        """Set a configuration value."""
        if section not in self.config:
            self.config[section] = {}

        self.config[section][key] = value

    def get_value(self, section, key, default=None):
        """Get a configuration value."""
        section_data = self.config.get(section, {})
        return section_data.get(key, default)
```

## 5.8 Performance Optimization Subsystem

The Performance Optimization Subsystem will monitor and optimize system performance:

### Performance Monitoring

```python
class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.memory_usage = []
        self.metrics = {}

    def start(self):
        """Start performance monitoring."""
        import time
        import psutil
        import os

        self.start_time = time.time()
        self.memory_usage = []

        # Record initial memory usage
        process = psutil.Process(os.getpid())
        self.memory_usage.append(process.memory_info().rss)

    def end(self):
        """End performance monitoring."""
        import time
        import psutil
        import os

        self.end_time = time.time()

        # Record final memory usage
        process = psutil.Process(os.getpid())
        self.memory_usage.append(process.memory_info().rss)

        # Calculate metrics
        self.metrics['execution_time'] = self.end_time - self.start_time
        self.metrics['memory_increase'] = self.memory_usage[-1] - self.memory_usage[0]

    def get_metrics(self):
        """Get performance metrics."""
        return self.metrics
```

### Optimization Strategies

```python
class PerformanceOptimizer:
    def __init__(self):
        self.optimizers = {}

    def register_optimizer(self, stage_name, optimizer):
        """Register an optimizer for a specific pipeline stage."""
        self.optimizers[stage_name] = optimizer

    def optimize(self, pipeline, context=None):
        """Optimize the performance of a processing pipeline."""
        if context is None:
            context = {}

        # Apply optimizers to each stage
        for stage_name, processor in pipeline.processors:
            if stage_name in self.optimizers:
                optimizer = self.optimizers[stage_name]
                optimizer.optimize(processor, context)

        return pipeline
```

### Caching System

```python
class CacheManager:
    def __init__(self, max_size=100):
        self.max_size = max_size
        self.caches = {}

    def get_cache(self, name, create_if_missing=True):
        """Get a cache by name."""
        if name not in self.caches and create_if_missing:
            self.caches[name] = LRUCache(self.max_size)

        return self.caches.get(name)

    def clear_cache(self, name=None):
        """Clear a cache or all caches."""
        if name is not None:
            if name in self.caches:
                self.caches[name].clear()
        else:
            for cache in self.caches.values():
                cache.clear()

    def get_cache_stats(self, name=None):
        """Get cache statistics."""
        if name is not None:
            if name in self.caches:
                return self.caches[name].get_stats()
            return None

        stats = {}
        for name, cache in self.caches.items():
            stats[name] = cache.get_stats()

        return stats

class LRUCache:
    def __init__(self, max_size=100):
        self.max_size = max_size
        self.cache = {}
        self.order = []
        self.hits = 0
        self.misses = 0

    def get(self, key, default=None):
        """Get a value from the cache."""
        if key in self.cache:
            # Move to end of order (most recently used)
            self.order.remove(key)
            self.order.append(key)

            self.hits += 1
            return self.cache[key]

        self.misses += 1
        return default

    def put(self, key, value):
        """Put a value in the cache."""
        if key in self.cache:
            # Update existing entry
            self.cache[key] = value

            # Move to end of order (most recently used)
            self.order.remove(key)
            self.order.append(key)
        else:
            # Add new entry
            if len(self.cache) >= self.max_size:
                # Remove least recently used
                lru_key = self.order.pop(0)
                del self.cache[lru_key]

            self.cache[key] = value
            self.order.append(key)

    def clear(self):
        """Clear the cache."""
        self.cache = {}
        self.order = []

    def get_stats(self):
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }
```

## 5.9 System Integration

### Backend API

```python
class ASCIIUITranslationEngine:
    def __init__(self):
        # Create core components
        self.plugin_manager = PluginManager()
        self.config_manager = ConfigurationManager()
        self.pipeline = ProcessingPipeline()
        self.cache_manager = CacheManager()

        # Initialize processors
        self.flood_fill_processor = FloodFillProcessor()
        self.contour_detection_processor = ContourDetectionProcessor()
        self.pattern_recognition_processor = PatternRecognitionProcessor()
        self.feature_extraction_processor = FeatureExtractionProcessor()
        self.component_classification_processor = ComponentClassificationProcessor()
        self.relationship_analysis_processor = RelationshipAnalysisProcessor()
        self.code_generation_processor = CodeGenerationProcessor()

        # Initialize performance monitoring
        self.performance_monitors = {
            'flood_fill': PerformanceMonitor(),
            'contour_detection': PerformanceMonitor(),
            'pattern_recognition': PerformanceMonitor(),
            'feature_extraction': PerformanceMonitor(),
            'component_classification': PerformanceMonitor(),
            'relationship_analysis': PerformanceMonitor(),
            'code_generation': PerformanceMonitor()
        }

        # Register processors with pipeline
        self.pipeline.register_processor(self.flood_fill_processor, 'flood_fill')
        self.pipeline.register_processor(self.contour_detection_processor, 'contour_detection')
        self.pipeline.register_processor(self.pattern_recognition_processor, 'pattern_recognition')
        self.pipeline.register_processor(self.feature_extraction_processor, 'feature_extraction')
        self.pipeline.register_processor(self.component_classification_processor, 'component_classification')
        self.pipeline.register_processor(self.relationship_analysis_processor, 'relationship_analysis')
        self.pipeline.register_processor(self.code_generation_processor, 'code_generation')

        # Register performance monitors
        for stage_name, monitor in self.performance_monitors.items():
            self.pipeline.register_performance_monitor(stage_name, monitor)

        # Initialize extension points
        self._init_extension_points()

    def _init_extension_points(self):
        """Initialize extension points."""
        # Create extension points
        ext_points = {
            'pattern_matchers': ExtensionPoint('pattern_matchers'),
            'feature_extractors': ExtensionPoint('feature_extractors'),
            'component_classifiers': ExtensionPoint('component_classifiers'),
            'relationship_analyzers': ExtensionPoint('relationship_analyzers'),
            'code_generators': ExtensionPoint('code_generators')
        }

        # Register extension points
        for name, ext_point in ext_points.items():
            self.plugin_manager.register_extension_point(name, ext_point)

    def process_ascii_ui(self, ascii_text, options=None):
        """Process ASCII UI text and generate code."""
        if options is None:
            options = {}

        # Create processing context
        context = {
            'options': options,
            'target_framework': options.get('target_framework', 'default'),
            'generator_options': options.get('generator_options', {})
        }

        # Process the ASCII text
        try:
            # Create ASCIIGrid from text
            grid = ASCIIGrid(ascii_text)
            context['grid'] = grid

            # Process through pipeline
            result, stage_results = self.pipeline.process(grid, context)

            # Extract performance metrics
            performance_metrics = {}
            for stage_name, monitor in self.performance_monitors.items():
                performance_metrics[stage_name] = monitor.get_metrics()

            # Prepare response
            response = {
                'success': True,
                'generated_code': result if isinstance(result, str) else context.get('generated_code'),
                'component_model': context.get('component_model'),
                'performance_metrics': performance_metrics
            }

            return response

        except Exception as e:
            # Handle errors
            return {
                'success': False,
                'error': str(e)
            }

    def load_plugins(self, plugin_dir):
        """Load plugins from a directory."""
        import os

        # Scan directory for plugin files
        plugin_files = []

        for root, dirs, files in os.walk(plugin_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    plugin_files.append(os.path.join(root, file))

        # Load each plugin
        loaded_plugins = []

        for plugin_file in plugin_files:
            try:
                plugin_name = self.plugin_manager.load_plugin_from_file(plugin_file)
                loaded_plugins.append(plugin_name)
            except Exception as e:
                print(f"Error loading plugin {plugin_file}: {str(e)}")

        return loaded_plugins

    def load_config(self, config_path):
        """Load configuration from a file."""
        self.config_manager.load_config(config_path)

    def save_config(self, config_path):
        """Save configuration to a file."""
        self.config_manager.save_config(config_path)

    def get_supported_frameworks(self):
        """Get a list of supported frameworks for code generation."""
        ext_point = self.plugin_manager.get_extension_point('code_generators')

        if ext_point:
            return list(ext_point.get_extensions().keys())
        return []
```

### Command Line Interface

```python
def create_cli():
    """Create command line interface for the engine."""
    import argparse

    parser = argparse.ArgumentParser(description='ASCII UI Translation Engine')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Process command
    process_parser = subparsers.add_parser('process', help='Process an ASCII UI file')
    process_parser.add_argument('input_file', help='Input ASCII UI file')
    process_parser.add_argument('--output', '-o', help='Output file for generated code')
    process_parser.add_argument('--framework', '-f', default='default', help='Target framework for code generation')
    process_parser.add_argument('--config', '-c', help='Configuration file')

    # List frameworks command
    list_frameworks_parser = subparsers.add_parser('list-frameworks', help='List supported frameworks')

    # Load plugins command
    load_plugins_parser = subparsers.add_parser('load-plugins', help='Load plugins from a directory')
    load_plugins_parser.add_argument('plugin_dir', help='Plugin directory')

    return parser

def main():
    """Main entry point for the command line interface."""
    parser = create_cli()
    args = parser.parse_args()

    # Create engine
    engine = ASCIIUITranslationEngine()

    if args.command == 'process':
        # Load configuration if specified
        if args.config:
            engine.load_config(args.config)

        # Read input file
        with open(args.input_file, 'r') as f:
            ascii_text = f.read()

        # Process ASCII UI
        options = {
            'target_framework': args.framework
        }

        response = engine.process_ascii_ui(ascii_text, options)

        if response['success']:
            # Output generated code
            generated_code = response['generated_code']

            if args.output:
                with open(args.output, 'w') as f:
                    f.write(generated_code)
            else:
                print(generated_code)

            # Print performance metrics
            print("\nPerformance metrics:")
            for stage, metrics in response['performance_metrics'].items():
                if 'execution_time' in metrics:
                    print(f"  {stage}: {metrics['execution_time']:.4f} seconds")
        else:
            print(f"Error: {response['error']}")

    elif args.command == 'list-frameworks':
        # List supported frameworks
        frameworks = engine.get_supported_frameworks()

        print("Supported frameworks:")
        for framework in frameworks:
            print(f"  {framework}")

    elif args.command == 'load-plugins':
        # Load plugins
        loaded_plugins = engine.load_plugins(args.plugin_dir)

        print(f"Loaded {len(loaded_plugins)} plugins:")
        for plugin in loaded_plugins:
            print(f"  {plugin}")

if __name__ == '__main__':
    main()
```
