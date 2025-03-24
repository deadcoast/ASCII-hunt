COMPONENT_PROPERTIES = {
    "Window": {
        "required": ["title", "width", "height"],
        "optional": ["minimizable", "maximizable", "closable", "modal"],
        "defaults": {
            "minimizable": True,
            "maximizable": True,
            "closable": True,
            "modal": False,
        },
    },
    "Button": {
        "required": ["text"],
        "optional": ["enabled", "default", "width", "height"],
        "defaults": {"enabled": True, "default": False},
    },
    # Definitions for other component types...
}
