"""Layout Management Module."""


class LayoutManager:
    def __init__(self):
        """Initialize the LayoutManager with all necessary layout handlers.

        The LayoutManager has a dictionary of layout handlers, each associated
        with a specific layout type. The handlers are responsible for generating
        the layout code for components with the corresponding layout type.

        The layout handlers are:
        - 'default': self._generate_default_layout
        - 'grid': self._generate_grid_layout
        - 'flex': self._generate_flex_layout
        - 'absolute': self._generate_absolute_layout
        - 'relative': self._generate_relative_layout
        - 'sticky': self._generate_sticky_layout
        - 'pack': self._generate_pack_layout
        - 'place': self._generate_place_layout
        """
        self.layout_handlers = {
            "default": self._generate_default_layout,
            "grid": self._generate_grid_layout,
            "flex": self._generate_flex_layout,
            "absolute": self._generate_absolute_layout,
            "relative": self._generate_relative_layout,
            "sticky": self._generate_sticky_layout,
            "pack": self._generate_pack_layout,
            "place": self._generate_place_layout,
        }

    def register_layout_handler(self, layout_type, handler):
        """Register a layout handler for a specific layout type."""
        self.layout_handlers[layout_type] = handler

    def generate_layout_code(self, component, children, indent="", options=None):
        """Generate layout code for a component and its children."""
        if options is None:
            options = {}

        # Get layout type
        layout_type = component.properties.get("layout", "default")

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
            x = child.properties.get("x", 0)
            y = child.properties.get("y", 0)

            # Generate positioning code
            var_name = f"{child.type.lower()}_{child.id}"
            code_parts.append(f"{indent}{var_name}.place(x={x}, y={y})")

        return "\n".join(code_parts)

    def _generate_grid_layout(self, component, children, indent, options):
        """Generate grid layout code."""
        code_parts = []
        for child in children:
            row = child.properties.get("row", 0)
            col = child.properties.get("column", 0)
            rowspan = child.properties.get("rowspan", 1)
            colspan = child.properties.get("colspan", 1)
            sticky = child.properties.get("sticky", "")

            var_name = f"{child.type.lower()}_{child.id}"
            code_parts.append(
                f"{indent}{var_name}.grid(row={row}, column={col}, "
                f"rowspan={rowspan}, columnspan={colspan}, sticky='{sticky}')"
            )
        return "\n".join(code_parts)

    def _generate_flex_layout(self, component, children, indent, options):
        """Generate flex layout code."""
        code_parts = []
        for child in children:
            expand = child.properties.get("expand", 1)
            fill = child.properties.get("fill", "both")

            var_name = f"{child.type.lower()}_{child.id}"
            code_parts.append(
                f"{indent}{var_name}.pack(expand={expand}, fill='{fill}')"
            )
        return "\n".join(code_parts)

    def _generate_absolute_layout(self, component, children, indent, options):
        """Generate absolute layout code."""
        code_parts = []
        for child in children:
            x = child.properties.get("x", 0)
            y = child.properties.get("y", 0)
            width = child.properties.get("width", None)
            height = child.properties.get("height", None)

            var_name = f"{child.type.lower()}_{child.id}"
            if width is not None and height is not None:
                code_parts.append(
                    f"{indent}{var_name}.place(x={x}, y={y}, width={width}, height={height})"
                )
            else:
                code_parts.append(f"{indent}{var_name}.place(x={x}, y={y})")
        return "\n".join(code_parts)

    def _generate_relative_layout(self, component, children, indent, options):
        """Generate relative layout code."""
        code_parts = []
        for child in children:
            relx = child.properties.get("relx", 0.0)
            rely = child.properties.get("rely", 0.0)
            relwidth = child.properties.get("relwidth", None)
            relheight = child.properties.get("relheight", None)

            var_name = f"{child.type.lower()}_{child.id}"
            if relwidth is not None and relheight is not None:
                code_parts.append(
                    f"{indent}{var_name}.place(relx={relx}, rely={rely}, "
                    f"relwidth={relwidth}, relheight={relheight})"
                )
            else:
                code_parts.append(f"{indent}{var_name}.place(relx={relx}, rely={rely})")
        return "\n".join(code_parts)

    def _generate_sticky_layout(self, component, children, indent, options):
        """Generate sticky layout code."""
        code_parts = []
        for child in children:
            sticky = child.properties.get("sticky", "nsew")
            padx = child.properties.get("padx", 0)
            pady = child.properties.get("pady", 0)

            var_name = f"{child.type.lower()}_{child.id}"
            code_parts.append(
                f"{indent}{var_name}.grid(sticky='{sticky}', padx={padx}, pady={pady})"
            )
        return "\n".join(code_parts)

    def _generate_pack_layout(self, component, children, indent, options):
        """Generate pack layout code."""
        code_parts = []
        for child in children:
            side = child.properties.get("side", "top")
            fill = child.properties.get("fill", "none")
            expand = child.properties.get("expand", 0)

            var_name = f"{child.type.lower()}_{child.id}"
            code_parts.append(
                f"{indent}{var_name}.pack(side='{side}', fill='{fill}', expand={expand})"
            )
        return "\n".join(code_parts)

    def _generate_place_layout(self, component, children, indent, options):
        """Generate place layout code."""
        code_parts = []
        for child in children:
            x = child.properties.get("x", 0)
            y = child.properties.get("y", 0)
            anchor = child.properties.get("anchor", "nw")

            var_name = f"{child.type.lower()}_{child.id}"
            code_parts.append(
                f"{indent}{var_name}.place(x={x}, y={y}, anchor='{anchor}')"
            )
        return "\n".join(code_parts)
