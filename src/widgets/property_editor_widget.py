   class PropertyEditorWidget(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self.component = None
           self.property_model = QStandardItemModel()
           self.setup_ui()

       def setup_ui(self):
           layout = QVBoxLayout(self)

           # Create tree view for properties
           self.property_view = QTreeView()
           self.property_view.setModel(self.property_model)
           self.property_view.setAlternatingRowColors(True)
           self.property_view.setEditTriggers(QAbstractItemView.AllEditTriggers)

           layout.addWidget(self.property_view)

       def set_component(self, component):
           self.component = component
           self.update_property_model()

       def update_property_model(self):
           self.property_model.clear()

           if not self.component:
               return

           # Set up headers
           self.property_model.setHorizontalHeaderLabels(['Property', 'Value'])

           # Add component type
           type_item = QStandardItem('Type')
           type_value = QStandardItem(self.component.type)
           type_value.setEditable(False)
           self.property_model.appendRow([type_item, type_value])

           # Add component properties
           for key, value in self.component.properties.items():
               property_item = QStandardItem(key)
               value_item = QStandardItem(str(value))
               self.property_model.appendRow([property_item, value_item])