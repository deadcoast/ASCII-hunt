#!/usr/bin/env python3

import os
import re
import tempfile
import unittest
from unittest.mock import patch

from mermaid_connect import DiagramValidator


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


class TestDiagramProcessor(unittest.TestCase):
    def setUp(self):
        """Create temporary test files and initialize processor."""
        self.test_dir = tempfile.mkdtemp()

        # Create test files
        self.valid_file = os.path.join(self.test_dir, "valid.mmd")
        with open(self.valid_file, "w") as f:
            f.write("""graph TD
            TestComp["Test Component\\n(test.module)"]
            TestComp2["Test Component 2\\n(test.module2)"]
            TestComp --> TestComp2
            class TestComp testStyle""")

        self.invalid_file = os.path.join(self.test_dir, "invalid.mmd")
        with open(self.invalid_file, "w") as f:
            f.write("""graph TD
            InvalidComp["Invalid Component\\n(test.invalid)"]
            class InvalidComp invalidStyle""")

        self.processor = DiagramValidator(self.test_dir)

        # Capture console output
        self.console_output = []

        def mock_print(text=""):
            self.console_output.append(str(text))

        self.print_patcher = patch("rich.console.Console.print", mock_print)
        self.print_patcher.start()

    def tearDown(self):
        """Clean up temporary files."""
        self.print_patcher.stop()
        for f in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, f))
        os.rmdir(self.test_dir)

    def strip_ansi(self, text):
        """Remove ANSI color codes for comparison."""
        import re

        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", text)

    def test_step_one_input_collection(self):
        """Test STEP 1: Input component collection and display."""
        self.processor.collect_inputs()

        output = "\n".join(self.console_output)
        stripped_output = self.strip_ansi(output)

        # Verify header format
        self.assertIn("# -----------------", stripped_output)
        self.assertIn("# > sys.INPUT[IN] *", stripped_output)

        # Verify component listing
        self.assertIn("sys.[IN]: valid.mmd:TestComp[", stripped_output)
        self.assertIn("sys.[IN]: valid.mmd:TestComp2[", stripped_output)
        self.assertIn("sys.[IN]: invalid.mmd:InvalidComp[", stripped_output)

    def test_step_two_combination(self):
        """Test STEP 2: Diagram combination and output collection."""
        self.processor.combine_and_collect_outputs()

        # Verify combined file was created
        self.assertTrue(
            os.path.exists(os.path.join(self.test_dir, "combined_diagram.mmd"))
        )

        output = "\n".join(self.console_output)
        stripped_output = self.strip_ansi(output)

        # Verify header format
        self.assertIn("# -------------------", stripped_output)
        self.assertIn("# > sys.OUTPUT[OUT] *", stripped_output)

        # Verify component listing
        self.assertIn("sys.[OUT]: valid.mmd:TestComp[", stripped_output)
        self.assertIn("sys.[OUT]: valid.mmd:TestComp2[", stripped_output)

    def test_step_three_validation(self):
        """Test STEP 3: Component validation."""
        # Setup components
        self.processor.collect_inputs()
        self.processor.combine_and_collect_outputs()
        self.console_output.clear()

        self.processor.validate_components()
        output = "\n".join(self.console_output)
        stripped_output = self.strip_ansi(output)

        # Verify header format
        self.assertIn("# ------------------", stripped_output)
        self.assertIn("# > sys.VALIDATION *", stripped_output)

        # Verify validation format
        self.assertIn(
            "sys.[IN]: valid.mmd | [OUT]: valid.mmd ✅ -> [VALIDATED]", stripped_output
        )
        self.assertIn(
            "sys.[IN]: invalid.mmd | [OUT]: invalid.mmd ✅ -> [VALIDATED]",
            stripped_output,
        )

    def test_step_four_reporting(self):
        """Test STEP 4: Final report generation."""
        # Setup validation state
        self.processor.num_validated = 2
        self.processor.num_failed = 1
        self.processor.null_modules = ["failed.mmd"]

        self.processor.generate_report()
        output = "\n".join(self.console_output)
        stripped_output = self.strip_ansi(output)

        # Verify header format
        self.assertIn("# ---------------", stripped_output)
        self.assertIn("# > sys.REPORTS *", stripped_output)

        # Verify report content
        self.assertIn("sys.[✅]: 2", stripped_output)
        self.assertIn("sys.[❌]: 1", stripped_output)
        self.assertIn("sys.report: init == [---NULL OUTPUTS---]", stripped_output)
        self.assertIn("failed.mmd", stripped_output)

    def test_null_output_validation(self):
        """Test validation of a component with null output."""
        # Create a file that will fail validation
        null_file = os.path.join(self.test_dir, "null_test.mmd")
        with open(null_file, "w") as f:
            f.write("""graph TD
            NullComp["Null Component\\n(test.null)"]""")

        # Corrupt the component in combined output
        self.processor.input_components["null_test.mmd"] = {"NullComp"}
        self.processor.output_components["null_test.mmd"] = set()

        self.processor.validate_components()
        output = "\n".join(self.console_output)
        stripped_output = self.strip_ansi(output)

        # Verify null output format
        self.assertIn(
            "sys.[IN]: null_test.mmd | [OUT]: --- NULL --- ❌ -> [--- NULL ---]",
            stripped_output,
        )
        self.assertIn("null_test.mmd", self.processor.null_modules)

    def test_pass_output_validation(self):
        """Test validation of a component with successful output."""
        # Create a file that will pass validation
        pass_file = os.path.join(self.test_dir, "pass_test.mmd")
        with open(pass_file, "w") as f:
            f.write("""graph TD
            PassComp["Pass Component\\n(test.pass)"]""")

        # Set matching input and output
        comp = 'PassComp["Pass Component\\n(test.pass)"]'
        self.processor.input_components["pass_test.mmd"] = {comp}
        self.processor.output_components["pass_test.mmd"] = {comp}

        self.processor.validate_components()
        output = "\n".join(self.console_output)
        stripped_output = self.strip_ansi(output)

        # Verify pass output format
        self.assertIn(
            "sys.[IN]: pass_test.mmd | [OUT]: pass_test.mmd ✅ -> [VALIDATED]",
            stripped_output,
        )
        self.assertNotIn("pass_test.mmd", self.processor.null_modules)


if __name__ == "__main__":
    unittest.main(verbosity=2)
