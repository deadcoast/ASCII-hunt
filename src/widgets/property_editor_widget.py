"""This is a widget that displays the properties of a component.
It is used to display the properties of a component in a tree view.
"""

from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QAbstractItemView, QTreeView, QVBoxLayout, QWidget


class PropertyEditorWidget(QWidget):
    def __init__(self, parent=None):
        """Initialize a PropertyEditorWidget.

        :param parent: the parent widget
        :type parent: QWidget
        """
        super().__init__(parent)
        self.component = None
        self.property_model = QStandardItemModel()
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI elements for the PropertyEditorWidget.

        This method creates a QVBoxLayout and adds a QTreeView to it.
        The QTreeView displays the properties of the component.
        """
        layout = QVBoxLayout(self)

        # Create tree view for properties
        self.property_view = QTreeView()
        self.property_view.setModel(self.property_model)
        self.property_view.setAlternatingRowColors(True)
        self.property_view.setEditTriggers(QAbstractItemView.AllEditTriggers)

        layout.addWidget(self.property_view)

    def set_component(self, component):
        """Set the component to display the properties of.

        :param component: The component to display the properties of.
        :type component: Component
        """
        self.component = component
        self.update_property_model()

    def update_property_model(self):
        """Update the property model for the component.

        This method updates the property model of the PropertyEditorWidget to
        reflect the properties of the component. It clears the model and then
        adds the component type and properties to the model.
        """
        self.property_model.clear()

        if not self.component:
            return

        # Set up headers
        self.property_model.setHorizontalHeaderLabels(["Property", "Value"])

        # Add component type
        type_item = QStandardItem("Type")
        type_value = QStandardItem(self.component.type)
        type_value.setEditable(False)
        self.property_model.appendRow([type_item, type_value])

        # Add component properties
        for key, value in self.component.properties.items():
            property_item = QStandardItem(key)
            value_item = QStandardItem(str(value))
            self.property_model.appendRow([property_item, value_item])
