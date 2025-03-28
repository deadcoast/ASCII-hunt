#!/usr/bin/env python3


class DiagramError(Exception):
    """Base class for diagram-related errors."""

    pass


class FileError(DiagramError):
    """Error related to file operations."""

    pass


class ValidationError(DiagramError):
    """Error related to diagram validation."""

    pass


class SyntaxError(DiagramError):
    """Error related to Mermaid syntax."""

    pass
