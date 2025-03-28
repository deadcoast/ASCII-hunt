# BACK END DEPENDENCY GRAPH

```mermaid
graph TD
    subgraph Core Engine
        Engine[engine/__init__.py] --> Pipeline[engine/pipeline.py]
        Engine --> Config[engine/config.py]
        Engine --> Plugin[engine/plugin.py]
    end

    subgraph Data Layer
        Data[engine/data/__init__.py]
        Data --> Grid[engine/data/grid.py]
        Data --> Model[engine/data/model.py]
        Data --> Cache[engine/data/cache.py]

        Grid --> GridOps[engine/data/grid_ops.py]
        Model --> ModelOps[engine/data/model_ops.py]
    end

    subgraph Analysis
        Analysis[engine/analysis/__init__.py]
        Analysis --> Pattern[engine/analysis/pattern.py]
        Analysis --> Feature[engine/analysis/feature.py]
        Analysis --> Component[engine/analysis/component.py]

        Pattern --> Matchers[engine/analysis/matchers.py]
        Feature --> Extractors[engine/analysis/extractors.py]
        Component --> Classifiers[engine/analysis/classifiers.py]
    end

    subgraph Hierarchy
        Hierarchy[engine/hierarchy/__init__.py]
        Hierarchy --> Container[engine/hierarchy/container.py]
        Hierarchy --> Layout[engine/hierarchy/layout.py]
        Hierarchy --> Relations[engine/hierarchy/relations.py]
    end

    subgraph Generation
        Generation[engine/generation/__init__.py]
        Generation --> Template[engine/generation/template.py]
        Generation --> Renderer[engine/generation/renderer.py]
        Generation --> Framework[engine/generation/framework.py]
    end

    subgraph Common
        Common[engine/common/__init__.py]
        Common --> Types[engine/common/types.py]
        Common --> Utils[engine/common/utils.py]
        Common --> Constants[engine/common/constants.py]
    end

    %% Core Dependencies
    Pipeline --> Data
    Pipeline --> Analysis
    Pipeline --> Hierarchy
    Pipeline --> Generation

    %% Analysis Dependencies
    Pattern --> Data
    Feature --> Data
    Component --> Data

    %% Hierarchy Dependencies
    Container --> Data
    Layout --> Data
    Relations --> Data

    %% Generation Dependencies
    Template --> Common
    Renderer --> Common
    Framework --> Common

    %% Shared Dependencies
    Data --> Common
    Analysis --> Common
    Hierarchy --> Common
    Generation --> Common
```

Key Import Rules to Prevent Circular Dependencies:

2. Back-end Rules:

   - Common modules can be imported by any module but cannot import from other modules
   - Data layer modules can only import from common
   - Analysis modules can import from data and common only
   - Hierarchy modules can import from data and common only
   - Generation modules can import from common only
   - Pipeline is the only module that can import from all other modules

3. General Guidelines:
   - Use dependency injection where possible
   - Implement interfaces/abstract classes in base modules
   - Keep utility functions in their respective utils modules
   - Use event systems for cross-module communication
   - Implement factories for complex object creation
