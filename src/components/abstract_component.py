class AbstractComponent:
    def __init__(self, component_id, component_type):
        self.id = component_id
        self.type = component_type
        self.properties = {}
        self.children = []
        self.parent = None
        self.relationships = []

    def add_property(self, key, value):
        self.properties[key] = value

    def add_child(self, component):
        component.parent = self
        self.children.append(component)

    def add_relationship(self, relationship_type, target_component):
        self.relationships.append((relationship_type, target_component))

    def get_descendants(self):
        result = []
        for child in self.children:
            result.append(child)
            result.extend(child.get_descendants())
        return result

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type,
            "properties": self.properties,
            "children": [child.serialize() for child in self.children],
            "relationships": [
                (rel_type, comp.id) for rel_type, comp in self.relationships
            ],
        }

    @classmethod
    def deserialize(cls, data, component_map=None):
        if component_map is None:
            component_map = {}

        component = cls(data["id"], data["type"])
        component.properties = data["properties"].copy()
        component_map[data["id"]] = component

        for child_data in data["children"]:
            child = cls.deserialize(child_data, component_map)
            component.add_child(child)

        # Defer relationship resolution until all components are created
        relationship_data = [
            (rel_type, target_id) for rel_type, target_id in data["relationships"]
        ]

        if len(relationship_data) > 0:
            for rel_type, target_id in relationship_data:
                if target_id in component_map:
                    component.add_relationship(rel_type, component_map[target_id])

        return component
