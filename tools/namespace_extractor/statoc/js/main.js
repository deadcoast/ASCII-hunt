document.addEventListener('DOMContentLoaded', function () {
    // Load initial data
    fetchData();
    fetchStats();
    
    // Set up event listeners
    setupEventListeners();
});

function setupEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', function() {
            // Deactivate all tabs
            document.querySelectorAll('.tab-button').forEach(b => {
                b.classList.remove('active');
            });
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('active');
            });
            
            // Activate clicked tab
            this.classList.add('active');
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Search functionality
    document.getElementById('search-button').addEventListener('click', function() {
        const query = document.getElementById('search-input').value;
        if (query) {
            searchData(query);
        }
    });
    
    // Allow pressing Enter in search box
    document.getElementById('search-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = this.value;
            if (query) {
                searchData(query);
            }
        }
    });
    
    // Filter checkboxes
    document.querySelectorAll('[data-filter]').forEach(checkbox => {
        checkbox.addEventListener('change', applyFilters);
    });
    
    // Display option checkboxes
    document.querySelectorAll('[data-option]').forEach(checkbox => {
        checkbox.addEventListener('change', applyDisplayOptions);
    });
}

// Global data storage
let extractionData = null;

function fetchData() {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            extractionData = data.data;
            renderTreeView(extractionData);
            renderListView(extractionData);
            renderGraphView(extractionData);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            document.getElementById('tree-container').innerHTML = 
                '<div class="error-message">Error loading data. Please check the console for details.</div>';
        });
}

function fetchStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            renderStats(data.stats);
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
        });
}

function searchData(query) {
    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            renderSearchResults(data.results);
        })
        .catch(error => {
            console.error('Error searching data:', error);
        });
}

function renderStats(stats) {
    const statsContainer = document.getElementById('stats-content');
    
    const statItems = [
        { label: 'Files', value: stats.total_files },
        { label: 'Directories', value: stats.total_directories },
        { label: 'Classes', value: stats.total_classes },
        { label: 'Functions', value: stats.total_functions },
        { label: 'Methods', value: stats.total_methods },
        { label: 'Nested Classes', value: stats.total_nested_classes },
        { label: 'Variables', value: stats.total_variables }
    ];
    
    let html = '<div class="stats-grid">';
    statItems.forEach(item => {
        html += `
            <div class="stat-item">
                <div class="stat-value">${item.value}</div>
                <div class="stat-label">${item.label}</div>
            </div>
        `;
    });
    html += '</div>';
    
    statsContainer.innerHTML = html;
}

function renderTreeView(data) {
    const container = document.getElementById('tree-container');
    
    if (!data) {
        container.innerHTML = '<div class="no-data">No data available</div>';
        return;
    }
    
    let html = '<div class="tree-root">';
    
    // Structure depends on the data format
    if (isHierarchicalFormat(data)) {
        // Hierarchical format
        html += renderHierarchicalTree(data);
    } else {
        // Dictionary format
        for (const directory in data) {
            html += `
                <div class="tree-node">
                    <div class="tree-label" data-expanded="true">
                        <span class="tree-toggle">-</span>
                        <span class="directory-name">${directory || '[root]'}</span>
                    </div>
                    <div class="tree-children">
            `;
            
            for (const file in data[directory]) {
                html += `
                    <div class="tree-node">
                        <div class="tree-label" data-expanded="true">
                            <span class="tree-toggle">-</span>
                            <span class="file-name">${file}</span>
                        </div>
                        <div class="tree-children">
                `;
                
                for (const namespace of data[directory][file]) {
                    html += renderNamespaceTree(namespace, file);
                }
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            html += `
                    </div>
                </div>
            `;
        }
    }
    
    html += '</div>';
    container.innerHTML = html;
    
    // Add click handlers for tree toggles
    document.querySelectorAll('.tree-label').forEach(label => {
        label.addEventListener('click', function(e) {
            if (e.target.classList.contains('tree-toggle')) {
                return; // Let the toggle handler deal with it
            }
            
            const isExpanded = this.getAttribute('data-expanded') === 'true';
            this.setAttribute('data-expanded', !isExpanded);
            
            const children = this.nextElementSibling;
            if (children && children.classList.contains('tree-children')) {
                children.style.display = isExpanded ? 'none' : 'block';
                
                const toggle = this.querySelector('.tree-toggle');
                if (toggle) {
                    toggle.textContent = isExpanded ? '+' : '-';
                }
            }
        });
    });
}

function renderNamespaceTree(namespace, filename) {
    const type = namespace.type || 'unknown';
    const name = namespace.name || 'unnamed';
    
    let html = `
        <div class="tree-node">
            <div class="tree-label" data-expanded="false">
                <span class="tree-toggle">+</span>
                <span class="namespace-name ${type}">${name}</span>
                <span class="namespace-type">${type}</span>
            </div>
            <div class="tree-children" style="display: none;">
    `;
    
    // Add details
    html += `<div class="namespace-details">`;
    
    if (type === 'function' || type === 'method') {
        html += `<div class="signature">${namespace.signature || ''}</div>`;
    }
    
    if (namespace.docstring) {
        html += `<div class="docstring">${namespace.docstring}</div>`;
    }
    
    html += `</div>`;
    
    // Add methods for classes
    if (type === 'class' && namespace.methods) {
        for (const method of namespace.methods) {
            html += renderNamespaceTree(method, filename);
        }
    }
    
    // Add nested classes
    if (type === 'class' && namespace.nested_classes) {
        if (Array.isArray(namespace.nested_classes)) {
            for (const nestedClass of namespace.nested_classes) {
                html += renderNamespaceTree(nestedClass, filename);
            }
        } else {
            for (const className in namespace.nested_classes) {
                html += renderNamespaceTree(namespace.nested_classes[className], filename);
            }
        }
    }
    
    html += `
            </div>
        </div>
    `;
    
    return html;
}

function renderHierarchicalTree(data) {
    let html = '';
    
    // Render packages
    if (data.packages) {
        for (const packageName in data.packages) {
            const packageData = data.packages[packageName];
            
            html += `
                <div class="tree-node">
                    <div class="tree-label" data-expanded="true">
                        <span class="tree-toggle">-</span>
                        <span class="package-name">${packageName}/</span>
                    </div>
                    <div class="tree-children">
                        ${renderHierarchicalTree(packageData)}
                    </div>
                </div>
            `;
        }
    }
    
    // Render modules
    if (data.modules) {
        for (const moduleName in data.modules) {
            const moduleData = data.modules[moduleName];
            const filename = moduleData.filename || `${moduleName}.py`;
            
            html += `
                <div class="tree-node">
                    <div class="tree-label" data-expanded="true">
                        <span class="tree-toggle">-</span>
                        <span class="module-name">${filename}</span>
                    </div>
                    <div class="tree-children">
            `;
            
            // Render classes
            if (moduleData.classes) {
                for (const className in moduleData.classes) {
                    const classData = moduleData.classes[className];
                    classData.name = className;
                    classData.type = 'class';
                    
                    html += renderNamespaceTree(classData, filename);
                }
            }
            
            // Render functions
            if (moduleData.functions) {
                for (const func of moduleData.functions) {
                    html += renderNamespaceTree(func, filename);
                }
            }
            
            // Render variables
            if (moduleData.variables) {
                for (const variable of moduleData.variables) {
                    html += renderNamespaceTree(variable, filename);
                }
            }
            
            html += `
                    </div>
                </div>
            `;
        }
    }
    
    return html;
}

function renderListView(data) {
    const container = document.getElementById('list-container');
    
    if (!data) {
        container.innerHTML = '<div class="no-data">No data available</div>';
        return;
    }
    
    // Flatten the data for list view
    const flatList = flattenData(data);
    
    let html = '<div class="list-view">';
    
    flatList.forEach(item => {
        const type = item.namespace.type || 'unknown';
        const name = item.namespace.name || 'unnamed';
        
        html += `
            <div class="list-item" data-type="${type}">
                <div class="list-item-header">
                    <div class="list-item-name">${name}</div>
                    <div class="list-item-type">${type}</div>
                </div>
                <div class="list-item-path">${item.directory}/${item.file}</div>
        `;
        
        if (type === 'function' || type === 'method') {
            html += `<div class="list-item-details">${item.namespace.signature || ''}</div>`;
        }
        
        if (item.namespace.docstring) {
            html += `<div class="list-item-docstring">${item.namespace.docstring}</div>`;
        }
        
        html += `</div>`;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function renderGraphView(data) {
    const container = document.getElementById('graph-container');
    
    if (!data) {
        container.innerHTML = '<div class="no-data">No data available</div>';
        return;
    }
    
    container.innerHTML = '<svg width="100%" height="100%"></svg>';
    
    // Convert data to a format suitable for D3
    const graphData = convertToGraphData(data);
    
    // Create the graph
    createForceDirectedGraph(graphData);
}

function createForceDirectedGraph(data) {
    const svg = d3.select('#graph-container svg');
    const {width, height} = svg.node().getBoundingClientRect();
    
    const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2));
    
    const link = svg.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(data.links)
        .enter().append('line')
        .attr('class', 'link')
        .attr('stroke-width', d => d.value);
    
    const node = svg.append('g')
        .attr('class', 'nodes')
        .selectAll('.node')
        .data(data.nodes)
        .enter().append('g')
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    node.append('circle')
        .attr('r', d => getNodeRadius(d))
        .attr('fill', d => getNodeColor(d.type));
    
    node.append('text')
        .attr('dx', 12)
        .attr('dy', '.35em')
        .text(d => d.name);
    
    node.append('title')
        .text(d => d.name);
    
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('transform', d => `translate(${d.x},${d.y})`);
    });
    
    function dragstarted(event, d) {
        if (!event.active) {
          simulation.alphaTarget(0.3).restart();
        }
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragended(event, d) {
        if (!event.active) {
          simulation.alphaTarget(0);
        }
        d.fx = null;
        d.fy = null;
    }
    
    // Add zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 10])
        .on('zoom', (event) => {
            svg.selectAll('g').attr('transform', event.transform);
        });
    
    svg.call(zoom);
}

function getNodeRadius(node) {
    const baseRadius = 5;
    
    switch (node.type) {
        case 'class':
            return baseRadius * 1.5;
        case 'function':
            return baseRadius * 1.2;
        case 'method':
            return baseRadius;
        case 'nested_class':
            return baseRadius * 1.3;
        case 'variable':
            return baseRadius * 0.8;
        default:
            return baseRadius;
    }
}

function getNodeColor(type) {
    switch (type) {
        case 'class':
            return '#4f46e5'; // Indigo
        case 'function':
            return '#2563eb'; // Blue
        case 'method':
            return '#3b82f6'; // Light blue
        case 'nested_class':
            return '#7c3aed'; // Violet
        case 'variable':
            return '#10b981'; // Green
        default:
            return '#6b7280'; // Gray
    }
}

function convertToGraphData(data) {
    const nodes = [];
    const links = [];
    const nodeMap = {};
    
    // Helper function to add a node if it doesn't exist
    function addNode(id, name, type, file, directory) {
        if (!nodeMap[id]) {
            const node = { id, name, type, file, directory };
            nodes.push(node);
            nodeMap[id] = node;
        }
        return nodeMap[id];
    }
    
    // Process the data based on its format
    if (isHierarchicalFormat(data)) {
        processHierarchicalData(data, '', null);
    } else {
        // Dictionary format
        for (const directory in data) {
            for (const file in data[directory]) {
                for (const namespace of data[directory][file]) {
                    processNamespace(namespace, file, directory, null);
                }
            }
        }
    }
    
    // Process hierarchical data
    function processHierarchicalData(data, path, parentId) {
        // Process packages
        if (data.packages) {
            for (const packageName in data.packages) {
                const packageData = data.packages[packageName];
                const packagePath = path ? `${path}.${packageName}` : packageName;
                const packageId = `package:${packagePath}`;
                
                addNode(packageId, packageName, 'package', '', path);
                
                if (parentId) {
                    links.push({ source: parentId, target: packageId, value: 1 });
                }
                
                processHierarchicalData(packageData, packagePath, packageId);
            }
        }
        
        // Process modules
        if (data.modules) {
            for (const moduleName in data.modules) {
                const moduleData = data.modules[moduleName];
                const filename = moduleData.filename || `${moduleName}.py`;
                const moduleId = `module:${path ? path + '.' : ''}${moduleName}`;
                
                addNode(moduleId, filename, 'module', filename, path);
                
                if (parentId) {
                    links.push({ source: parentId, target: moduleId, value: 1 });
                }
                
                // Process classes
                if (moduleData.classes) {
                    for (const className in moduleData.classes) {
                        const classData = moduleData.classes[className];
                        classData.name = className;
                        classData.type = 'class';
                        
                        processNamespace(classData, filename, path, moduleId);
                    }
                }
                
                // Process functions
                if (moduleData.functions) {
                    for (const func of moduleData.functions) {
                        processNamespace(func, filename, path, moduleId);
                    }
                }
                
                // Process variables
                if (moduleData.variables) {
                    for (const variable of moduleData.variables) {
                        processNamespace(variable, filename, path, moduleId);
                    }
                }
            }
        }
    }
    
    // Process a namespace (class, function, etc.)
    function processNamespace(namespace, file, directory, parentId) {
        const type = namespace.type || 'unknown';
        const name = namespace.name || 'unnamed';
        const id = `${type}:${directory}/${file}/${name}`;
        
        // Add the node
        const node = addNode(id, name, type, file, directory);
        
        // Connect to parent
        if (parentId) {
            links.push({ source: parentId, target: id, value: 1 });
        }
        
        // Process methods for classes
        if (type === 'class' && namespace.methods) {
            for (const method of namespace.methods) {
                processNamespace(method, file, directory, id);
            }
        }
        
        // Process nested classes
        if (type === 'class' && namespace.nested_classes) {
            if (Array.isArray(namespace.nested_classes)) {
                for (const nestedClass of namespace.nested_classes) {
                    processNamespace(nestedClass, file, directory, id);
                }
            } else {
                for (const className in namespace.nested_classes) {
                    const nestedClass = namespace.nested_classes[className];
                    nestedClass.name = className;
                    nestedClass.type = 'nested_class';
                    processNamespace(nestedClass, file, directory, id);
                }
            }
        }
        
        // Add inheritance links
        if (type === 'class' && namespace.bases && Array.isArray(namespace.bases)) {
            for (const base of namespace.bases) {
                // We can't always determine the exact ID of the base class, so this is a simplification
                // In a real implementation, this would need more sophisticated logic
                const baseId = `class:${directory}/${file}/${base.split('.').pop()}`;
                if (nodeMap[baseId]) {
                    links.push({ source: baseId, target: id, value: 2, type: 'inheritance' });
                }
            }
        }
    }
    
    return { nodes, links };
}

function flattenData(data) {
    const result = [];
    
    // Process based on data format
    if (isHierarchicalFormat(data)) {
        flattenHierarchicalData(data, '', result);
    } else {
        // Dictionary format
        for (const directory in data) {
            for (const file in data[directory]) {
                for (const namespace of data[directory][file]) {
                    flattenNamespace(namespace, file, directory, result);
                }
            }
        }
    }
    
    return result;
}

function flattenHierarchicalData(data, path, result) {
    // Process modules
    if (data.modules) {
        for (const moduleName in data.modules) {
            const moduleData = data.modules[moduleName];
            const filename = moduleData.filename || `${moduleName}.py`;
            
            // Process classes
            if (moduleData.classes) {
                for (const className in moduleData.classes) {
                    const classData = moduleData.classes[className];
                    classData.name = className;
                    classData.type = 'class';
                    
                    flattenNamespace(classData, filename, path, result);
                }
            }
            
            // Process functions
            if (moduleData.functions) {
                for (const func of moduleData.functions) {
                    flattenNamespace(func, filename, path, result);
                }
            }
            
            // Process variables
            if (moduleData.variables) {
                for (const variable of moduleData.variables) {
                    flattenNamespace(variable, filename, path, result);
                }
            }
        }
    }
    
    // Process packages recursively
    if (data.packages) {
        for (const packageName in data.packages) {
            const packageData = data.packages[packageName];
            const packagePath = path ? `${path}.${packageName}` : packageName;
            
            flattenHierarchicalData(packageData, packagePath, result);
        }
    }
}

function flattenNamespace(namespace, file, directory, result) {
    result.push({
        namespace,
        file,
        directory
    });
    
    // Flatten methods
    if (namespace.type === 'class' && namespace.methods) {
        for (const method of namespace.methods) {
            flattenNamespace(method, file, directory, result);
        }
    }
    
    // Flatten nested classes
    if (namespace.type === 'class' && namespace.nested_classes) {
        if (Array.isArray(namespace.nested_classes)) {
            for (const nestedClass of namespace.nested_classes) {
                flattenNamespace(nestedClass, file, directory, result);
            }
        } else {
            for (const className in namespace.nested_classes) {
                const nestedClass = namespace.nested_classes[className];
                nestedClass.name = className;
                nestedClass.type = 'nested_class';
                flattenNamespace(nestedClass, file, directory, result);
            }
        }
    }
}

function renderSearchResults(results) {
    if (!results || results.length === 0) {
        alert('No results found');
        return;
    }
    
    // Switch to list view
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    document.querySelector('[data-tab="list-view"]').classList.add('active');
    document.getElementById('list-view').classList.add('active');
    
    // Render the results
    const container = document.getElementById('list-container');
    
    let html = '<div class="search-results-header">Search Results</div><div class="list-view">';
    
    results.forEach(item => {
        const {namespace} = item;
        const type = namespace.type || 'unknown';
        const name = namespace.name || 'unnamed';
        
        html += `
            <div class="list-item search-result" data-type="${type}">
                <div class="list-item-header">
                    <div class="list-item-name">${name}</div>
                    <div class="list-item-type">${type}</div>
                </div>
                <div class="list-item-path">${item.directory}/${item.file}</div>
        `;
        
        if (type === 'function' || type === 'method') {
            html += `<div class="list-item-details">${namespace.signature || ''}</div>`;
        }
        
        if (namespace.docstring) {
            html += `<div class="list-item-docstring">${namespace.docstring}</div>`;
        }
        
        html += `</div>`;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function applyFilters() {
    // Get selected namespace types
    const enabledTypes = new Set();
    document.querySelectorAll('[data-filter="type"]:checked').forEach(checkbox => {
        enabledTypes.add(checkbox.value);
    });
    
    // Apply filters to list view
    document.querySelectorAll('#list-container .list-item').forEach(item => {
        const type = item.getAttribute('data-type');
        if (enabledTypes.has(type)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
    
    // Apply filters to tree view
    document.querySelectorAll('#tree-container .namespace-name').forEach(item => {
        const type = item.nextElementSibling.textContent;
        const node = item.closest('.tree-node');
        
        if (enabledTypes.has(type)) {
            node.style.display = '';
        } else {
            node.style.display = 'none';
        }
    });
}

function applyDisplayOptions() {
    const showInheritance = document.querySelector('[data-option="show_inheritance"]').checked;
    const showDecorators = document.querySelector('[data-option="show_decorators"]').checked;
    const showDocstrings = document.querySelector('[data-option="show_docstrings"]').checked;
    
    // Apply to list view
    document.querySelectorAll('#list-container .list-item-docstring').forEach(item => {
        item.style.display = showDocstrings ? '' : 'none';
    });
    
    // Apply to tree view
    document.querySelectorAll('#tree-container .docstring').forEach(item => {
        item.style.display = showDocstrings ? '' : 'none';
    });
    
    // Inheritance and decorators require re-rendering in some cases
    // This is a simplified implementation
}

function isHierarchicalFormat(data) {
    // Check if the data follows the hierarchical format
    return data && (data.packages || data.modules);
}

// Additional CSS to add to styles.css
document.head.insertAdjacentHTML('beforeend', `
<style>
.search-results-header {
    padding: 1rem;
    background-color: var(--primary-color);
    color: white;
    font-weight: bold;
    margin-bottom: 1rem;
}

.search-result {
    border-left: 3px solid var(--primary-color);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
}

.stat-item {
    background-color: var(--hover-color);
    padding: 0.75rem;
    border-radius: 4px;
    text-align: center;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary-color);
}

.stat-label {
    font-size: 0.8rem;
    color: var(--text-color);
}

.no-data {
    padding: 2rem;
    text-align: center;
    color: #64748b;
}

.error-message {
    padding: 1rem;
    background-color: #fee2e2;
    color: #b91c1c;
    border-radius: 4px;
    margin: 1rem;
}

.directory-name, .package-name {
    font-weight: bold;
    color: #6b7280;
}

.file-name, .module-name {
    font-weight: bold;
    color: #1f2937;
}

.namespace-name {
    font-weight: bold;
}

.namespace-name.class, .namespace-name.nested_class {
    color: #4f46e5;
}

.namespace-name.function, .namespace-name.method {
    color: #2563eb;
}

.namespace-name.variable {
    color: #10b981;
}

.namespace-type {
    font-size: 0.8rem;
    color: #6b7280;
    margin-left: 0.5rem;
}

.namespace-details {
    margin: 0.5rem 0 0.5rem 1rem;
    font-size: 0.9rem;
}

.signature {
    font-family: monospace;
    background-color: #f1f5f9;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    margin-bottom: 0.5rem;
}

.docstring {
    font-style: italic;
    color: #64748b;
}
</style>
`);