"""ASCII Hunt Package.

ASCII Hunt is a tool for converting ASCII art into UI components and code.
"""

import os
import sys

# Ensure that the parent directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Explicitly re-export public modules and names
from src.import_miner.import_driller.advanced_import_finder import (
    AdvancedImportFinder, SymbolTracker)
from src.import_miner.import_driller.cross_language_resolver import \
    CrossLanguageImportResolver

__version__ = "0.1.0"
__author__ = "ASCII Hunt Team"
__license__ = "MIT"

__all__ = [
    "AdvancedImportFinder",
    "CrossLanguageImportResolver",
    "SymbolTracker",
]
