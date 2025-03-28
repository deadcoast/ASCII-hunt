# FRONT END DEPENDENCY GRAPH

```mermaid
graph TD
    subgraph Frontend Core
        App[app.py] --> UI[ui/__init__.py]
        UI --> Components[ui/components/__init__.py]
        UI --> Views[ui/views/__init__.py]
        UI --> State[ui/state.py]
        UI --> Events[ui/events.py]
    end

    subgraph Components
        Components --> Base[ui/components/base.py]
        Components --> Editor[ui/components/editor.py]
        Components --> Inspector[ui/components/inspector.py]
        Components --> Preview[ui/components/preview.py]
        Components --> Toolbar[ui/components/toolbar.py]

        Base --> Types[ui/types.py]
        Editor --> Grid[ui/components/grid.py]
        Editor --> Tools[ui/components/tools.py]
        Inspector --> Properties[ui/components/properties.py]
    end

    subgraph Views
        Views --> MainView[ui/views/main.py]
        Views --> EditorView[ui/views/editor.py]
        Views --> InspectorView[ui/views/inspector.py]
        Views --> PreviewView[ui/views/preview.py]
    end

    subgraph State Management
        State --> Store[ui/state/store.py]
        Store --> Actions[ui/state/actions.py]
        Store --> Reducers[ui/state/reducers.py]
        Events --> EventBus[ui/events/bus.py]
    end

    subgraph Utils
        Utils[ui/utils/__init__.py]
        Utils --> Geometry[ui/utils/geometry.py]
        Utils --> Validation[ui/utils/validation.py]
        Utils --> Constants[ui/utils/constants.py]
    end
```

1. Front-end Rules:

   - Components can only import from base.py and utils
   - Views can import components but not vice versa
   - State can be imported by any module but cannot import from other modules
   - Utils should have no dependencies on other modules
