"""Utility functions for the HUNT DSL."""

import logging
import pprint  # For visualization
from typing import Any, TypeVar

# Define logger for this module
logger = logging.getLogger(__name__)

# Constants for string length limits
_MAX_REPR_LEN_SUMMARY = 80
_MAX_REPR_LEN_WARNING = 50

# Type variable for generic functions like _clean
T = TypeVar("T")


def assert_constraints(_params: dict[str, Any]) -> bool:
    """Assert constraints based on DSL 'trap', 'req', 'prohib'.

    Args:
        _params: Parameters for constraint checking
                 (e.g., {'rules': [callable1, ...], 'data': ...})

    Returns:
        bool: True if all constraints pass, False otherwise.
    """
    rules = _params.get("rules", [])
    data = _params.get("data", {})
    all_passed = True
    if not isinstance(rules, list):
        logger.error("Invalid 'rules' parameter type: %s", type(rules))
        return False

    for i, rule in enumerate(rules):
        try:
            # Example: rule could be a callable or a dict describing the check
            if callable(rule):
                if not rule(data):
                    rule_name = getattr(rule, "__name__", f"callable rule #{i + 1}")
                    logger.warning("Constraint failed: %s on data %s", rule_name, data)
                    all_passed = False
                    # In a real scenario, 'req'/'prohib' might raise an exception here
            else:
                logger.warning("Rule #%d is not callable, skipping.", i + 1)
                # Add more complex rule checking logic here if rules are dicts/etc.
        except Exception:
            # G201: Use logger.exception for errors with traceback
            logger.exception("Error evaluating rule #%d", i + 1)
            all_passed = False

    return all_passed


# --- Helper functions for bulk_merge ---


def _merge_lists(sources: list, mode: str) -> list:
    """Helper to merge list sources."""
    merged_data: list = []
    for source in sources:
        if isinstance(source, list):
            if mode == "concatenate":
                merged_data.extend(source)  # Simple concatenation
            elif mode == "unique":  # Example of another mode
                for item in source:
                    if item not in merged_data:
                        merged_data.append(item)
            # Add other list merging strategies here
        else:
            logger.warning("Skipping non-list source during list merge.")
    return merged_data


def _merge_dicts(sources: list, mode: str) -> dict:
    """Helper to merge dictionary sources."""
    merged_data_dict: dict = {}
    for source in sources:
        if isinstance(source, dict):
            if mode == "update":  # Overwrite keys from later sources
                merged_data_dict.update(source)
            # Add other dict merging strategies (e.g., deep merge)
        else:
            logger.warning("Skipping non-dict source during dict merge.")
    return merged_data_dict


# --- End Helper functions ---


def bulk_merge(_params: dict[str, Any]) -> list | dict:
    """Merge multiple data sources based on DSL 'HARVEST'.

    Args:
        _params: Parameters for merging (e.g., {'sources': [data1, data2, ...],
                 'mode': 'concatenate' | 'update'})

    Returns:
        Union[List, Dict]: Merged data structure.
    """
    sources = _params.get("sources", [])
    mode = _params.get("mode", "concatenate")  # Default mode

    if not isinstance(sources, list):
        logger.error("Invalid 'sources' parameter type: %s", type(sources))
        return []

    if not sources:
        return []

    # Determine target type based on the first source
    first_source = sources[0]
    if isinstance(first_source, list):
        return _merge_lists(sources, mode)
    if isinstance(first_source, dict):
        return _merge_dicts(sources, mode)

    logger.error("Unsupported source type for merging: %s", type(first_source))
    return []  # Or raise error


def extract_target(_params: dict[str, Any]) -> dict | None:
    """Extract a specific target based on DSL 'pluck'.

    Args:
        _params: Parameters for extraction
                 (e.g., {
                     'data': [{'id': 1, 'name': 'A'}, {'id': 2, 'name': 'B'}],
                     'target_key': 'id',
                     'target_value': 2
                 })

    Returns:
        Optional[Dict]: Extracted dictionary item if found, else None.
    """
    data = _params.get("data", [])
    target_key = _params.get("target_key")
    target_value = _params.get("target_value")

    if not isinstance(data, list):
        logger.warning("'data' for extraction is not a list: %s", type(data))
        return None
    if target_key is None or target_value is None:
        logger.warning("Missing 'target_key' or 'target_value' for extraction.")
        return None

    found = None
    for item in data:
        try:
            if isinstance(item, dict) and item.get(target_key) == target_value:
                found = item
                break
            # Add logic here if data is not list of dicts (e.g., list of objects)
        except Exception:
            # LOG007: Changed to logger.error as exc_info=False was used
            # TRY401: Removed redundant 'e' from log arguments
            logger.exception("Error accessing key '%s' in item %s", target_key, item)
            continue  # Skip problematic item

    if found is None:
        logger.debug("Target not found: key='%s', value='%s'", target_key, target_value)
    return found


def generate_code(_params: dict[str, Any]) -> str:
    """Generate code representation based on DSL 'COOK'.

    Args:
        _params: Parameters for code generation
                 (e.g., {
                     'data': {'class': 'Button', 'props': {'text': 'OK'}},
                     'format': 'python'
                 })

    Returns:
        str: Generated code string.
    """
    data = _params.get("data", {})
    code_format = _params.get("format", "repr")  # Default to repr

    try:
        if code_format == "python":
            # Example: Generate pseudo-Python instantiation
            if isinstance(data, dict):
                class_name = data.get("class", "UnknownClass")
                props = data.get("props", {})
                prop_str = ", ".join(f"{k}={v!r}" for k, v in props.items())
                return f"{class_name}({prop_str})"
            return repr(data)
        if code_format == "json":
            import json  # Import moved inside block

            return json.dumps(data, indent=2)
        if code_format == "repr":
            return repr(data)
        # Default case if format is not recognized
        logger.warning("Unsupported code format: %s. Using str().", code_format)
        return str(data)
    except Exception:
        # G201: Use logger.exception for errors with traceback
        logger.exception("Error generating code for format %s", code_format)
        # TRY401: Removed redundant 'e' from return string, using generic message
        return "# Error generating code"


def organize_tags(_params: dict[str, Any]) -> dict[str, list[Any]]:
    """Organize data by tags based on DSL 'GATHER'.

    Args:
        _params: Parameters for organization
                 (e.g., {
                     'data': [{'id': 1, 'tags': ['a', 'b']}, {'id': 2, 'tags': ['b']}],
                     'tag_key': 'tags' # Optional: key containing tags
                 })

    Returns:
        Dict[str, List[Any]]: Data organized by tag.
    """
    data = _params.get("data", [])
    tag_key = _params.get("tag_key", "tags")  # Key where tags are stored
    organized: dict[str, list[Any]] = {}

    if not isinstance(data, list):
        logger.warning("'data' for tag organization is not a list: %s", type(data))
        return {}

    for item in data:
        try:
            if isinstance(item, dict):
                tags = item.get(tag_key, [])
                if isinstance(tags, list):
                    for tag in tags:
                        if isinstance(tag, str):
                            organized.setdefault(tag, []).append(item)
                        else:
                            logger.debug(
                                "Skipping non-string tag: %s in item %s",
                                tag,
                                item.get("id", item),
                            )
                elif tags:  # Handle single tag case if needed
                    logger.debug(
                        "Tags field '%s' is not a list in item %s",
                        tag_key,
                        item.get("id", item),
                    )
            # Add logic if items are not dicts but have tags
        except Exception:
            # LOG007: Changed to logger.error as exc_info=False was used
            # TRY401: Removed redundant 'e' from log arguments
            logger.exception("Error processing tags for item %s", item)
            continue  # Skip problematic item
    return organized


def setup_logging(_params: dict[str, Any]) -> None:
    """Set up logging based on DSL 'track'.

    Configures the module-specific logger, not the root logger.

    Args:
        _params: Parameters for logging setup
                 (e.g., {'level': 'INFO', 'format': '%(message)s'})
    """
    log_level_str = _params.get("level", "WARNING").upper()
    log_level = getattr(logging, log_level_str, logging.WARNING)
    log_format = _params.get(
        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure the module-specific logger
    logger.setLevel(log_level)

    # Avoid adding multiple handlers if called again
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False  # Prevent messages going to root logger
    else:
        # Optionally update existing handler's level/formatter
        # Explicitly type handler in loop to satisfy mypy
        handler: logging.Handler
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(log_level)
                formatter = logging.Formatter(log_format)
                handler.setFormatter(formatter)
            else:
                # Handle other handler types if necessary, or just log
                logger.debug(
                    "Skipping configuration for handler type: %s", type(handler)
                )

    # Use the configured logger
    logger.info("Module logger '%s' configured to level %s", logger.name, log_level_str)


# Bind T to the 'data' value within _params
def simplify_output(_params: dict[str, Any]) -> Any:
    """Simplify the output data structure based on DSL 'boil'.

    Args:
        _params: Parameters for simplification
                 (e.g., {
                     'data': {'a': 1, 'b': None, 'c': [None, 2]},
                     'mode': 'remove_none' | 'flatten' # Example modes
                 })

    Returns:
        Any: Simplified data structure.
    """
    data = _params.get("data", {})
    mode = _params.get("mode", "remove_none")

    try:
        if mode == "remove_none":
            # Define _clean helper here, accessible by both dict and list cases below
            # Return type is Any to handle recursive complexities
            def _clean(item: Any) -> Any:
                if isinstance(item, dict):
                    # Recursively clean dict, returning a dict
                    cleaned_dict = {k: _clean(v) for k, v in item.items()}
                    return {k: v for k, v in cleaned_dict.items() if v is not None}
                if isinstance(item, list):
                    # Recursively clean list, returning a list
                    cleaned_list = [_clean(i) for i in item]
                    return [i for i in cleaned_list if i is not None]
                # Return item as is if not dict or list, or if it's not None
                return item if item is not None else None

            return _clean(data)

        if mode == "flatten":  # Example of another mode
            # Implement flattening logic here if needed
            logger.warning("Flatten mode not yet implemented.")
            return data
        logger.warning("Unsupported simplification mode: %s.", mode)
        return data
    except Exception:
        # G201: Use logger.exception for errors with traceback
        logger.exception("Error simplifying data for mode %s", mode)
        return data


def visualize_output(_params: dict[str, Any]) -> str:
    """Create a visual representation based on DSL 'RACK'.

    Args:
        _params: Parameters for visualization
                 (e.g., {
                     'data': {'type': 'Button', 'coords': (1,1,5,1)},
                     'mode': 'pretty' | 'ascii_summary'
                 })

    Returns:
        str: Visual representation (e.g., pretty-printed string).
    """
    data = _params.get("data", {})
    mode = _params.get("mode", "pretty")

    try:
        if mode == "pretty":
            return pprint.pformat(data, indent=2, width=100)
        if mode == "ascii_summary":
            # Example: Create a simple text summary
            if isinstance(data, dict):
                lines = [f"Data Summary ({type(data).__name__}):"]
                lines.extend(
                    # PLR2004: Use constant for magic number 80
                    f"  {k}: {repr(v)[:_MAX_REPR_LEN_SUMMARY]}"
                    f"{'...' if len(repr(v)) > _MAX_REPR_LEN_SUMMARY else ''}"
                    for k, v in data.items()
                )
                return "\n".join(lines)
            return repr(data)
        # Default case
        logger.warning("Unsupported visualization mode: %s. Using repr().", mode)
        return repr(data)
    except Exception:
        # G201: Use logger.exception for errors with traceback
        logger.exception("Error visualizing data for mode %s", mode)
        return "# Error visualizing data"


def warn_soft(_params: dict[str, Any]) -> list[str]:
    """Generate soft warnings based on DSL 'scent'.

    Args:
        _params: Parameters for warning generation (e.g., {
                     'data': [{'id': 1, 'label': None}],
                     'conditions': [
                         lambda d: 'Missing label' if d.get('label') is None else None
                     ]
                 })

    Returns:
        List[str]: List of generated warning messages.
    """
    data = _params.get("data", [])  # Assume data is iterable (e.g., list of components)
    conditions = _params.get("conditions", [])
    warnings = []

    if not isinstance(conditions, list):
        logger.error("Invalid 'conditions' parameter type: %s", type(conditions))
        return ["Error: Invalid conditions parameter"]

    items_to_check = data if isinstance(data, list) else [data]

    for i, condition in enumerate(conditions):
        if not callable(condition):
            logger.warning("Condition #%d is not callable, skipping.", i + 1)
            continue

        for item in items_to_check:
            try:
                if warning_msg := condition(item):
                    # E501 reformatted, PLR2004: Use constant for magic number 50
                    item_repr = repr(item)[:_MAX_REPR_LEN_WARNING]
                    if len(repr(item)) > _MAX_REPR_LEN_WARNING:
                        item_repr += "..."
                    full_warning = f"Soft warning: {warning_msg} (item: {item_repr})"
                    warnings.append(full_warning)
                    logger.warning(full_warning)  # Also log the warning
            except Exception:
                # LOG007: Changed to logger.error as exc_info=False was used
                # TRY401: Removed redundant 'e' from log arguments
                logger.exception(
                    "Error evaluating condition #%d on item %s", i + 1, item
                )
                # Optionally add an error message to warnings list

    # Ensure a list is always returned, even if empty
    return warnings
