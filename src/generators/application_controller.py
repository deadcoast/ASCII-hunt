"""Application Controller Module."""

from managers.backend_manager import BackendManager


class ApplicationController:
    def __init__(self, main_window):
        """
        Initialize the ApplicationController.

        This method sets up the main application window, a backend manager for
        processing ASCII art, and the current file, grid data, and component
        information.

        :param main_window: The main application window.
        :type main_window: QMainWindow
        """
        self.main_window = main_window
        self.backend = BackendManager()
        self.current_file = None
        self.grid_data = []
        self.components = []
        self.setup_connections()

    def setup_connections(self):
        # Connect UI signals to controller methods
        """
        Connect the UI signals to the corresponding controller methods.

        This method connects the main application window's UI signals to the
        corresponding methods in the ApplicationController.

        """
        self.main_window.action_new.triggered.connect(self.new_file)
        self.main_window.action_open.triggered.connect(self.open_file)
        self.main_window.action_save.triggered.connect(self.save_file)
        self.main_window.action_recognize.triggered.connect(self.run_recognition)
        self.main_window.action_generate_code.triggered.connect(self.generate_code)

    def new_file(self):
        # Create new empty grid
        """
        Create a new empty grid for the application.

        This method will create a new, empty, ASCII grid for the application.
        It will also reset the current file and component model.

        """
        pass

    def open_file(self):
        # Open and load ASCII file
        """
        Open a file dialog for the user to select an ASCII file.

        This method will prompt the user to select an ASCII file to open. The
        file contents will be read and stored as the current grid data.

        """
        pass

    def save_file(self):
        # Save current ASCII grid to file
        """
        Save the current ASCII grid to a file.

        This method will prompt the user to select a save location and filename.
        The current grid data will be written to the selected file.

        """
        pass

    def run_recognition(self):
        """Run component recognition on current grid."""
        self.components = self.backend.process_ascii_grid(self.grid_data)
        self.main_window.update_component_display(self.components)

    def generate_code(self):
        """Generate code for recognized components."""
        framework = self.main_window.get_selected_framework()
        options = self.main_window.get_generation_options()

        code = self.backend.generate_code(self.components, framework, options)
        self.main_window.display_generated_code(code)
