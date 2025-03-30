"""Application Main Window Module."""

from typing import Any

from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Assuming other widgets might be used later
# from .ascii_grid_widget import ASCIIGridWidget
# from .property_editor_widget import PropertyEditorWidget


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the MainWindow."""
        super().__init__(parent)
        self.setWindowTitle("ASCII HUNT - UI Translator")
        self.setGeometry(100, 100, 1200, 800)  # x, y, width, height

        self._create_actions()
        self._create_menus()
        self._create_status_bar()
        self._create_central_widget()

        # Placeholder for components recognized by the backend
        self.components: list[dict[str, Any]] = []

    def _close_app(self) -> None:
        """Helper method to close the application, ensures None return type for connect."""
        self.close()

    def _create_actions(self) -> None:
        """Create the main actions for menus and toolbars."""
        # File actions
        self.action_new = QAction("&New", self)
        self.action_new.setStatusTip("Create a new ASCII file")
        self.action_open = QAction("&Open...", self)
        self.action_open.setStatusTip("Open an existing ASCII file")
        self.action_save = QAction("&Save", self)
        self.action_save.setStatusTip("Save the current ASCII file")
        self.action_save_as = QAction("Save &As...", self)
        self.action_save_as.setStatusTip("Save the current ASCII file with a new name")
        self.action_exit = QAction("E&xit", self)
        self.action_exit.setStatusTip("Exit the application")
        # Connect to the wrapper method
        self.action_exit.triggered.connect(self._close_app)

        # Recognition/Generation actions
        self.action_recognize = QAction("&Recognize Components", self)
        self.action_recognize.setStatusTip(
            "Run component recognition on the current grid"
        )
        self.action_generate_code = QAction("&Generate Code", self)
        self.action_generate_code.setStatusTip(
            "Generate UI code from recognized components"
        )

    def _create_menus(self) -> None:
        """Create the main menu bar."""
        # Access the menuBar using the method
        menu_bar = self.menuBar()  # QMenuBar instance

        if menu_bar:  # Check if menu_bar is not None
            # File menu
            file_menu = menu_bar.addMenu("&File")
            if file_menu:  # Check if file_menu is not None
                file_menu.addAction(self.action_new)
                file_menu.addAction(self.action_open)
                file_menu.addAction(self.action_save)
                file_menu.addAction(self.action_save_as)
                file_menu.addSeparator()
                file_menu.addAction(self.action_exit)

            # Process menu
            process_menu = menu_bar.addMenu("&Process")
            if process_menu:  # Check if process_menu is not None
                process_menu.addAction(self.action_recognize)
                process_menu.addAction(self.action_generate_code)

    def _create_status_bar(self) -> None:
        """Create the status bar."""
        # Set the status bar
        status_bar_instance = QStatusBar(self)
        self.setStatusBar(status_bar_instance)
        if current_status_bar := self.statusBar():
            current_status_bar.showMessage("Ready")

    def _create_central_widget(self) -> None:
        """Create the central widget and layout."""
        # Main central widget setup (can be refined later)
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Placeholder for ASCII Grid - replace with ASCIIGridWidget later
        self.ascii_editor_placeholder = QTextEdit()
        self.ascii_editor_placeholder.setPlaceholderText(
            "ASCII Grid will appear here..."
        )
        layout.addWidget(self.ascii_editor_placeholder, 1)  # Make it take more space

        # Placeholder for generated code display
        self.code_display_placeholder = QTextEdit()
        self.code_display_placeholder.setReadOnly(True)
        self.code_display_placeholder.setPlaceholderText(
            "Generated code will appear here..."
        )
        layout.addWidget(self.code_display_placeholder, 1)

        # Framework selector
        self.framework_combo = QComboBox()
        self.framework_combo.addItems(
            ["Tkinter", "PyQt5", "Textual"]
        )  # Example frameworks
        layout.addWidget(self.framework_combo)

        self.setCentralWidget(central_widget)

    # --- Methods expected by ApplicationController ---

    def update_component_display(self, components: list[dict[str, Any]]) -> None:
        """Update the UI to display recognized components.

        Args:
            components: A list of dictionaries representing recognized components.
        """
        self.components = components
        if status_bar := self.statusBar():
            status_bar.showMessage(
                f"Recognition complete. {len(components)} components found."
            )
        # TODO: Implement actual display logic, e.g., updating a tree view or overlays
        print(f"Received components: {components}")  # Placeholder

    def get_selected_framework(self) -> str:
        """Get the currently selected target UI framework from the UI.

        Returns:
            The name of the selected framework (e.g., "Tkinter").
        """
        return self.framework_combo.currentText()

    def get_generation_options(self) -> dict[str, Any]:
        """Get any code generation options specified in the UI.

        Returns:
            A dictionary of options.
        """
        # TODO: Add UI elements for options if needed
        return {}

    def display_generated_code(self, code: str) -> None:
        """Display the generated code in the UI.

        Args:
            code: The generated code string.
        """
        self.code_display_placeholder.setPlainText(code)
        if status_bar := self.statusBar():
            status_bar.showMessage("Code generation complete.")

    # --- Placeholder methods for File I/O (to be connected by Controller) ---

    def prompt_open_file(self) -> str | None:
        """Show an open file dialog and return the selected path."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open ASCII File",
            "",
            "ASCII Files (*.txt);;All Files (*)",
            options=options,
        )
        return file_name or None

    def prompt_save_file(self) -> str | None:
        """Show a save file dialog and return the selected path."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save ASCII File",
            "",
            "ASCII Files (*.txt);;All Files (*)",
            options=options,
        )
        return file_name or None

    def show_message(self, title: str, message: str) -> None:
        """Display a simple message box."""
        QMessageBox.information(self, title, message)

    def show_error(self, title: str, message: str) -> None:
        """Display an error message box."""
        QMessageBox.critical(self, title, message)

    # Add methods to get/set text from the ascii_editor_placeholder if needed
    def get_ascii_text(self) -> str:
        return self.ascii_editor_placeholder.toPlainText()

    def set_ascii_text(self, text: str) -> None:
        self.ascii_editor_placeholder.setPlainText(text)


# Example of how to run this window (usually done in a main script)
# if __name__ == '__main__':
#     import sys
#     from PyQt5.QtWidgets import QApplication
#     app = QApplication(sys.argv)
#     main_win = MainWindow()
#     main_win.show()
#     sys.exit(app.exec_())
