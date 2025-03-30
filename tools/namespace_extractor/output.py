# File: namespace_extractor/output.py
"""Output generation module for namespace extractor."""

import json
import os
from abc import ABC, abstractmethod
from typing import Any

import yaml

from .config import ExtractorConfig
from .formatter import FormattingOptions


class OutputGenerator(ABC):
    """Base class for output generators."""

    def __init__(
        self, config: ExtractorConfig, formatting_options: FormattingOptions
    ) -> None:
        """
        Initialize the output generator.

        Args:
            config: Extractor configuration
            formatting_options: Formatting options
        """
        self.config = config
        self.formatting_options = formatting_options

    @abstractmethod
    def generate(
        self,
        formatted_data: dict[str, dict[str, list[dict[str, Any]]]] | dict[str, Any],
    ) -> str:
        """
        Generate output content from formatted data.

        Args:
            formatted_data: Data prepared by a formatter

        Returns:
            String content to be written to output file
        """
        pass

    def save_to_file(self, content: str, output_path: str) -> None:
        """
        Save generated content to file.

        Args:
            content: Generated content
            output_path: Path to save the output
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(content)

        print(f"Output written to {output_path}")


class MarkdownOutputGenerator(OutputGenerator):
    """Generate markdown output from formatted data."""

    def generate(
        self,
        formatted_data: dict[str, dict[str, list[dict[str, Any]]]] | dict[str, Any],
    ) -> str:
        """
        Generate markdown representation.

        Args:
            formatted_data: Data prepared by a formatter

        Returns:
            Markdown string
        """
        # Starting content
        markdown = "# Python Namespace Extractions\n\n```python\n##GUARD_!_RAIL##\n\n"

        # Detect data format type
        if isinstance(formatted_data, dict) and all(
            isinstance(v, dict) for v in formatted_data.values()
        ):
            # Dictionary formatter data (directory -> filename -> namespaces)
            if all(
                all(isinstance(n, list) for n in file_dict.values())
                for file_dict in formatted_data.values()
            ):
                markdown += self._generate_from_dictionary(formatted_data)
            else:
                # Hierarchical formatter data
                markdown += self._generate_from_hierarchical(formatted_data)

        # Ending content
        markdown += "##GUARD_!_RAIL##\n```"

        return markdown

    def _generate_from_dictionary(
        self, formatted_data: dict[str, dict[str, list[dict[str, Any]]]]
    ) -> str:
        """
        Generate markdown from dictionary-formatted data.

        Args:
            formatted_data: Data prepared by DictionaryFormatter

        Returns:
            Markdown string
        """
        markdown = ""

        # Process each directory
        for directory, files in formatted_data.items():
            if directory:  # Skip empty directories
                markdown += f'"""\n{directory}\n"""\n'

            # Process each file in the directory
            for current_filename, namespaces in files.items():
                # Helper function to recursively process namespaces
                def process_namespace(
                    namespace: dict[str, Any],
                    indent: str = "",
                    current_file: str = current_filename,
                ) -> None:
                    nonlocal markdown

                    if namespace["type"] == "function":
                        # Handle standalone functions
                        prefix = f"# {current_file}\n{indent}" if indent else "# "
                        signature = namespace.get("signature", "")

                        # Add decorators
                        decorator_text = ""
                        if self.formatting_options.show_decorators and namespace.get(
                            "decorators"
                        ):
                            for decorator in namespace["decorators"]:
                                decorator_text += f"{indent}@{decorator}\n"

                        # Handle async functions
                        if namespace.get(
                            "is_async"
                        ) and not signature.strip().startswith("async "):
                            signature = f"async {signature}"

                        if signature.startswith("def "):
                            signature = signature[4:]  # Remove 'def ' prefix

                        if not indent:  # Top-level function
                            markdown += (
                                f"{decorator_text}# {current_file}\ndef {signature}:\n"
                            )

                            # Add docstring if available
                            if (
                                self.formatting_options.show_docstrings
                                and namespace.get("docstring")
                            ):
                                docstring = namespace["docstring"].split("\n")[
                                    0
                                ]  # First line only
                                markdown += f'    """{docstring}"""\n'

                        else:  # Method in a class
                            if decorator_text:
                                markdown += decorator_text

                            if namespace["name"] == "__init__":
                                markdown += f"{indent}def {signature}:\n\n"
                            else:
                                markdown += f"{prefix}def {signature}:\n"

                                # Add docstring if available
                                if (
                                    self.formatting_options.show_docstrings
                                    and namespace.get("docstring")
                                ):
                                    docstring = namespace["docstring"].split("\n")[
                                        0
                                    ]  # First line only
                                    markdown += f'{indent}    """{docstring}"""\n'

                    elif namespace["type"] == "class":
                        # Handle classes
                        prefix = f"\n{indent}" if indent else ""

                        # Add decorators
                        decorator_text = ""
                        if self.formatting_options.show_decorators and namespace.get(
                            "decorators"
                        ):
                            for decorator in namespace["decorators"]:
                                decorator_text += f"{indent}@{decorator}\n"

                        # Add base classes
                        bases_text = ""
                        if self.formatting_options.show_inheritance and namespace.get(
                            "bases"
                        ):
                            bases_text = f"({', '.join(namespace['bases'])})"

                        if not indent:  # Top-level class
                            markdown += (
                                f"{decorator_text}# {current_file}\n"
                                f"class {namespace['name']}{bases_text}:\n"
                            )

                            # Add docstring if available
                            if (
                                self.formatting_options.show_docstrings
                                and namespace.get("docstring")
                            ):
                                docstring = namespace["docstring"].split("\n")[
                                    0
                                ]  # First line only
                                markdown += f'    """{docstring}"""\n'
                        else:  # Nested class
                            if decorator_text:
                                markdown += decorator_text
                            markdown += (
                                f"{prefix}# {current_file}\n"
                                f"{indent}class {namespace['name']}{bases_text}:\n"
                            )

                            # Add docstring if available
                            if (
                                self.formatting_options.show_docstrings
                                and namespace.get("docstring")
                            ):
                                docstring = namespace["docstring"].split("\n")[
                                    0
                                ]  # First line only
                                nested_indent = indent + " " * 4
                                markdown += f'{nested_indent}"""{docstring}"""\n'

                        # Process nested classes first
                        for nested_class in namespace.get("nested_classes", []):
                            process_namespace(nested_class, indent + " " * 4)

                        # Process methods
                        for method in namespace.get("methods", []):
                            process_namespace(method, indent + " " * 4)

                        if not namespace.get("methods") and not namespace.get(
                            "nested_classes"
                        ):
                            markdown += f"{indent}    pass\n"

                    elif namespace["type"] == "variable" and namespace.get("name"):
                        # Handle module-level variables
                        value = namespace.get("value", "")
                        markdown += f"# {current_file}\n{namespace['name']} = {value}\n"

                # Process top-level namespaces
                for namespace in namespaces:
                    process_namespace(namespace)

                markdown += "\n"

        return markdown

    def _generate_from_hierarchical(self, formatted_data: dict[str, Any]) -> str:
        """
        Generate markdown from hierarchical-formatted data.

        Args:
            formatted_data: Data prepared by HierarchicalFormatter

        Returns:
            Markdown string
        """
        markdown = ""

        # Function to process package hierarchy
        def process_package(package_data: dict[str, Any], path: str = "") -> None:
            nonlocal markdown

            # Process modules in the package
            for module_name, module_data in package_data.get("modules", {}).items():
                filename = module_data.get("filename", f"{module_name}.py")

                # Add directory docstring if not already added
                if path and not markdown.endswith(f'"""\n{path}\n"""\n'):
                    markdown += f'"""\n{path}\n"""\n'

                # Process classes
                for class_name, class_data in module_data.get("classes", {}).items():
                    # Add decorators
                    if self.formatting_options.show_decorators and class_data.get(
                        "decorators"
                    ):
                        for decorator in class_data["decorators"]:
                            markdown += f"@{decorator}\n"

                    # Add class definition with base classes
                    bases_text = ""
                    if self.formatting_options.show_inheritance and class_data.get(
                        "bases"
                    ):
                        bases_text = f"({', '.join(class_data['bases'])})"

                    markdown += f"# {filename}\nclass {class_name}{bases_text}:\n"

                    # Add docstring if available
                    if self.formatting_options.show_docstrings and class_data.get(
                        "docstring"
                    ):
                        docstring = class_data["docstring"].split("\n")[
                            0
                        ]  # First line only
                        markdown += f'    """{docstring}"""\n'

                    # Process methods
                    for method in class_data.get("methods", []):
                        # Add method decorators
                        if self.formatting_options.show_decorators and method.get(
                            "decorators"
                        ):
                            for decorator in method["decorators"]:
                                markdown += f"    @{decorator}\n"

                        # Add method signature
                        signature = method.get("signature", "")
                        if signature.startswith("def "):
                            signature = signature[4:]  # Remove 'def ' prefix

                        # Handle async methods
                        if method.get("is_async") and not signature.strip().startswith(
                            "async "
                        ):
                            signature = f"async {signature}"

                        if method["name"] == "__init__":
                            markdown += f"    def {signature}:\n\n"
                        else:
                            markdown += f"    # {filename}\n    def {signature}:\n"

                            # Add docstring if available
                            if self.formatting_options.show_docstrings and method.get(
                                "docstring"
                            ):
                                docstring = method["docstring"].split("\n")[
                                    0
                                ]  # First line only
                                markdown += f'        """{docstring}"""\n'

                    # Process nested classes
                    for nested_name, nested_data in class_data.get(
                        "nested_classes", {}
                    ).items():
                        # Add nested class decorators
                        decorator_text = ""
                        if self.formatting_options.show_decorators and nested_data.get(
                            "decorators"
                        ):
                            for decorator in nested_data["decorators"]:
                                decorator_text += f"    @{decorator}\n"

                        # Add nested class definition with base classes
                        nested_bases_text = ""
                        if (
                            self.formatting_options.show_inheritance
                            and nested_data.get("bases")
                        ):
                            nested_bases_text = f"({', '.join(nested_data['bases'])})"

                        markdown += f"\n    # {filename}\n"
                        if decorator_text:
                            markdown += decorator_text

                        markdown += f"    class {nested_name}{nested_bases_text}:\n"

                        # Add docstring if available
                        if self.formatting_options.show_docstrings and nested_data.get(
                            "docstring"
                        ):
                            docstring = nested_data["docstring"].split("\n")[
                                0
                            ]  # First line only
                            markdown += f'        """{docstring}"""\n'

                        # Process nested class methods
                        for method in nested_data.get("methods", []):
                            # Add method decorators
                            if self.formatting_options.show_decorators and method.get(
                                "decorators"
                            ):
                                for decorator in method["decorators"]:
                                    markdown += f"        @{decorator}\n"

                            # Add method signature
                            signature = method.get("signature", "")
                            if signature.startswith("def "):
                                signature = signature[4:]  # Remove 'def ' prefix

                            # Handle async methods
                            if method.get(
                                "is_async"
                            ) and not signature.strip().startswith("async "):
                                signature = f"async {signature}"

                            markdown += (
                                f"        # {filename}\n        def {signature}:\n"
                            )

                            # Add docstring if available
                            if self.formatting_options.show_docstrings and method.get(
                                "docstring"
                            ):
                                docstring = method["docstring"].split("\n")[
                                    0
                                ]  # First line only
                                markdown += f'            """{docstring}"""\n'

                    markdown += "\n"

                # Process functions
                for function in module_data.get("functions", []):
                    # Add function decorators
                    if self.formatting_options.show_decorators and function.get(
                        "decorators"
                    ):
                        for decorator in function["decorators"]:
                            markdown += f"@{decorator}\n"

                    # Add function signature
                    signature = function.get("signature", "")
                    if signature.startswith("def "):
                        signature = signature[4:]  # Remove 'def ' prefix

                    # Handle async functions
                    if function.get("is_async") and not signature.strip().startswith(
                        "async "
                    ):
                        signature = f"async {signature}"

                    markdown += f"# {filename}\ndef {signature}:\n"

                    # Add docstring if available
                    if self.formatting_options.show_docstrings and function.get(
                        "docstring"
                    ):
                        docstring = function["docstring"].split("\n")[
                            0
                        ]  # First line only
                        markdown += f'    """{docstring}"""\n'

                # Process variables
                for variable in module_data.get("variables", []):
                    markdown += f"# {filename}\n{variable['name']} = {variable.get('value', '')}\n"

            # Process sub-packages
            for package_name, sub_package in package_data.get("packages", {}).items():
                new_path = f"{path}.{package_name}" if path else package_name
                process_package(sub_package, new_path)

        # Process from root
        process_package(formatted_data)

        return markdown


class JsonOutputGenerator(OutputGenerator):
    """Generate JSON output from formatted data."""

    def generate(
        self,
        formatted_data: dict[str, dict[str, list[dict[str, Any]]]] | dict[str, Any],
    ) -> str:
        """
        Generate JSON representation.

        Args:
            formatted_data: Data prepared by a formatter

        Returns:
            JSON string
        """
        return json.dumps(formatted_data, indent=self.config.indent_size)


class YamlOutputGenerator(OutputGenerator):
    """Generate YAML output from formatted data."""

    def generate(
        self,
        formatted_data: dict[str, dict[str, list[dict[str, Any]]]] | dict[str, Any],
    ) -> str:
        """
        Generate YAML representation.

        Args:
            formatted_data: Data prepared by a formatter

        Returns:
            YAML string
        """
        return yaml.dump(formatted_data, indent=self.config.indent_size)


class OutputGeneratorFactory:
    """Factory for creating appropriate output generator instances."""

    @staticmethod
    def create_output_generator(
        output_format: str,
        config: ExtractorConfig,
        formatting_options: FormattingOptions,
    ) -> OutputGenerator:
        """
        Create an output generator instance based on the specified format.

        Args:
            output_format: Type of output to generate
            config: Extractor configuration
            formatting_options: Formatting options

        Returns:
            OutputGenerator instance

        Raises:
            ValueError: If output_format is not recognized
        """
        if output_format == "markdown":
            return MarkdownOutputGenerator(config, formatting_options)
        elif output_format == "json":
            return JsonOutputGenerator(config, formatting_options)
        elif output_format == "yaml":
            return YamlOutputGenerator(config, formatting_options)
        else:
            raise ValueError(f"Unknown output format: {output_format}")

    def save_to_file(self, content: str, output_path: str) -> None:
        """Save generated content to file.

        Args:
            content: Generated content
            output_path: Path to save the output
        """
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(content)

        print(f"Output written to {output_path}")
