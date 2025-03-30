"""Layout Management Module."""

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ComponentProtocol(Protocol):
    """Defines the expected structure for component objects."""

    properties: dict[str, Any]  # Allow Any for property values for now
    type: str
    id: Any  # ID could be int, str, etc.


class LayoutManager:
    """Manages layout generation strategies for UI components."""

    # Define type alias at class level for handler functions
    LayoutHandler = Callable[
        [
            ComponentProtocol,  # component
            list[ComponentProtocol],  # children
            str,  # indent
            dict[str, Any] | None,  # options
        ],
        str,
    ]  # return type

    def __init__(self) -> None:
        """Initialize the LayoutManager with default handlers."""
        # Type hint for the dictionary using the class-level alias
        self.layout_handlers: dict[str, LayoutManager.LayoutHandler] = {
            "default": self._generate_default_layout,
            "grid": self._generate_grid_layout,
            "flex": self._generate_flex_layout,
            "absolute": self._generate_absolute_layout,
            "relative": self._generate_relative_layout,
            "sticky": self._generate_sticky_layout,
            "pack": self._generate_pack_layout,
            "place": self._generate_place_layout,
        }

    def register_layout_handler(
        self,
        layout_type: str,
        handler: Callable,  # Keep Callable for flexibility
    ) -> None:
        """Register a layout handler for a specific layout type."""
        # Runtime check might be needed if strict type adherence required
        # Ensure handler matches LayoutHandler signature if possible
        self.layout_handlers[layout_type] = handler

    def generate_layout_code(
        self,
        component: ComponentProtocol,
        children: list[ComponentProtocol],
        indent: str = "",
        options: dict[str, Any] | None = None,
    ) -> str:
        """Generate layout code for a component and its children."""
        if options is None:
            options = {}

        # Get layout type from component properties
        layout_type = getattr(component, "properties", {}).get("layout", "default")

        if handler := self.layout_handlers.get(layout_type):
            # Generate layout code by calling the retrieved handler directly
            return handler(component, children, indent, options)
        # Use default positioning if no specific handler found
        return self._generate_default_layout(component, children, indent, options)

    # --- Layout Generation Helper Methods ---
    # Note: Added type hints and prefixed unused args with _

    def _generate_default_layout(
        self,
        _component: ComponentProtocol,
        children: list[ComponentProtocol],
        indent: str,
        _options: dict[str, Any] | None,
    ) -> str:
        """Generate default layout code with absolute positioning."""
        code_parts = []
        for child in children:
            props = getattr(child, "properties", {})
            x = props.get("x", 0)
            y = props.get("y", 0)
            var_name = f"{getattr(child, 'type', 'widget').lower()}_{getattr(child, 'id', 'unknown')}"
            code_parts.append(f"{indent}{var_name}.place(x={x}, y={y})")
        return "\n".join(code_parts)

    def _generate_grid_layout(
        self,
        _component: ComponentProtocol,
        children: list[ComponentProtocol],
        indent: str,
        _options: dict[str, Any] | None,
    ) -> str:
        """Generate grid layout code."""
        code_parts = []
        for child in children:
            props = getattr(child, "properties", {})
            row = props.get("row", 0)
            col = props.get("column", 0)
            rowspan = props.get("rowspan", 1)
            colspan = props.get("colspan", 1)
            sticky = props.get("sticky", "")
            var_name = f"{getattr(child, 'type', 'widget').lower()}_{getattr(child, 'id', 'unknown')}"
            grid_args = (
                f"row={row}, column={col}, rowspan={rowspan}, "
                f"columnspan={colspan}, sticky='{sticky}'"
            )
            code_parts.append(f"{indent}{var_name}.grid({grid_args})")
        return "\n".join(code_parts)

    def _generate_flex_layout(
        self,
        _component: ComponentProtocol,
        children: list[ComponentProtocol],
        indent: str,
        _options: dict[str, Any] | None,
    ) -> str:
        """Generate flex layout code (using pack for simplicity)."""
        code_parts = []
        for child in children:
            props = getattr(child, "properties", {})
            expand = props.get("expand", 1)
            fill = props.get("fill", "both")
            var_name = f"{getattr(child, 'type', 'widget').lower()}_{getattr(child, 'id', 'unknown')}"
            pack_args = f"expand={expand}, fill='{fill}'"
            code_parts.append(f"{indent}{var_name}.pack({pack_args})")
        return "\n".join(code_parts)

    def _generate_absolute_layout(
        self,
        _component: ComponentProtocol,
        children: list[ComponentProtocol],
        indent: str,
        _options: dict[str, Any] | None,
    ) -> str:
        """Generate absolute layout code (using place)."""
        code_parts = []
        for child in children:
            props = getattr(child, "properties", {})
            x = props.get("x", 0)
            y = props.get("y", 0)
            width = props.get("width", None)
            height = props.get("height", None)
            var_name = f"{getattr(child, 'type', 'widget').lower()}_{getattr(child, 'id', 'unknown')}"
            place_args = f"x={x}, y={y}"
            if width is not None:
                place_args += f", width={width}"
            if height is not None:
                place_args += f", height={height}"
            code_parts.append(f"{indent}{var_name}.place({place_args})")
        return "\n".join(code_parts)

    def _generate_relative_layout(
        self,
        _component: ComponentProtocol,
        children: list[ComponentProtocol],
        indent: str,
        _options: dict[str, Any] | None,
    ) -> str:
        """Generate relative layout code (using place with rel coords)."""
        code_parts = []
        for child in children:
            props = getattr(child, "properties", {})
            relx = props.get("relx", 0.0)
            rely = props.get("rely", 0.0)
            relwidth = props.get("relwidth", None)
            relheight = props.get("relheight", None)
            var_name = f"{getattr(child, 'type', 'widget').lower()}_{getattr(child, 'id', 'unknown')}"
            place_args = f"relx={relx}, rely={rely}"
            if relwidth is not None:
                place_args += f", relwidth={relwidth}"
            if relheight is not None:
                place_args += f", relheight={relheight}"
            code_parts.append(f"{indent}{var_name}.place({place_args})")
        return "\n".join(code_parts)

    def _generate_sticky_layout(
        self,
        _component: ComponentProtocol,
        children: list[ComponentProtocol],
        indent: str,
        _options: dict[str, Any] | None,
    ) -> str:
        """Generate sticky layout code (using grid)."""
        code_parts = []
        for child in children:
            props = getattr(child, "properties", {})
            sticky = props.get("sticky", "nsew")
            padx = props.get("padx", 0)
            pady = props.get("pady", 0)
            var_name = f"{getattr(child, 'type', 'widget').lower()}_{getattr(child, 'id', 'unknown')}"
            row = props.get("row", 0)
            col = props.get("column", 0)
            grid_args = (
                f"row={row}, column={col}, sticky='{sticky}', padx={padx}, pady={pady}"
            )
            code_parts.append(f"{indent}{var_name}.grid({grid_args})")
        return "\n".join(code_parts)

    def _generate_pack_layout(
        self,
        _component: ComponentProtocol,
        children: list[ComponentProtocol],
        indent: str,
        _options: dict[str, Any] | None,
    ) -> str:
        """Generate pack layout code."""
        code_parts = []
        for child in children:
            props = getattr(child, "properties", {})
            side = props.get("side", "top")
            fill = props.get("fill", "none")
            expand = props.get("expand", 0)
            padx = props.get("padx", 0)
            pady = props.get("pady", 0)
            var_name = f"{getattr(child, 'type', 'widget').lower()}_{getattr(child, 'id', 'unknown')}"
            pack_args = (
                f"side='{side}', fill='{fill}', expand={expand}, "
                f"padx={padx}, pady={pady}"
            )
            code_parts.append(f"{indent}{var_name}.pack({pack_args})")
        return "\n".join(code_parts)

    def _generate_place_layout(
        self,
        _component: ComponentProtocol,
        children: list[ComponentProtocol],
        indent: str,
        _options: dict[str, Any] | None,
    ) -> str:
        """Generate place layout code."""
        code_parts = []
        for child in children:
            props = getattr(child, "properties", {})
            x = props.get("x", 0)
            y = props.get("y", 0)
            anchor = props.get("anchor", "nw")
            var_name = f"{getattr(child, 'type', 'widget').lower()}_{getattr(child, 'id', 'unknown')}"
            place_args = f"x={x}, y={y}, anchor='{anchor}'"
            code_parts.append(f"{indent}{var_name}.place({place_args})")
        return "\n".join(code_parts)
