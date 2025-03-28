"""Component Properties Module."""

from typing import Any, Union

# Define the expected types for component properties
COMPONENT_PROPERTIES = {
    "id": str,
    "type": str,
    "title": str,
    "width": int,
    "height": int,
    "x": int,
    "y": int,
    "text": str,
    "enabled": bool,
    "visible": bool,
    "style": dict[str, str],
    "children": list[Any],
    "relationships": list[tuple],
    "bg": str,
    "fg": str,
    "font": str,
    "value": Union[str, int, float],
    "checked": bool,
    "selected": bool,
    "items": list[str],
    "data": Union[list[Any], dict[str, Any]],
    "source": str,
    "template": str,
    "layout": dict[str, Any],
    "behavior": dict[str, Any],
    "performance": dict[str, Any],
    "accessibility": dict[str, Any],
    "usability": dict[str, Any],
    "interaction": dict[str, Any],
    "visualization": dict[str, Any],
    "animation": dict[str, Any],
}
