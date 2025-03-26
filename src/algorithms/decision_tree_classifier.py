import numpy as np
from sklearn import tree


def build_decision_tree_classifier(
    training_data: list[tuple[dict, str]],
) -> tree.DecisionTreeClassifier:
    """Builds and trains a decision tree classifier from labeled component data.

    Parameters
    ----------
    training_data : List[Tuple[Dict, str]]
        A list of tuples containing feature dictionaries and corresponding component type strings.

    Returns:
    -------
    tree.DecisionTreeClassifier
        A trained decision tree classifier.

    Notes:
    -----
    The feature dictionaries must contain the following keys:

    - aspect_ratio: float
    - border_density: float
    - content_density: float
    - border_type: int
    - has_text: bool
    - text_alignment: int
    - special_char_count: int

    The classifier is trained using the `criterion="entropy"` argument, with a maximum tree depth of 8 and a minimum of 2 samples required to split an internal node.
    """
    features_list: list[list[float]] = []  # Features
    labels_list: list[str] = []  # Labels

    for features, component_type in training_data:
        # Create numerical feature vector
        feature_vector = [
            float(features["aspect_ratio"]),
            float(features["border_density"]),
            float(features["content_density"]),
            float(features["border_type"]),
            float(features["has_text"]),
            float(features["text_alignment"]),
            float(features["special_char_count"]),
        ]
        features_list.append(feature_vector)
        labels_list.append(component_type)

    # Convert to NumPy arrays for training, using different variables
    x_train = np.array(features_list)
    y_train = np.array(labels_list)

    # Create and train decision tree
    clf = tree.DecisionTreeClassifier(
        criterion="entropy", max_depth=8, min_samples_split=2
    )
    clf.fit(x_train, y_train)

    return clf


def extract_ui_specific_features(component, grid):
    """Extract UI-specific features for decision tree classification.

    Parameters
    ----------
    component : dict
        A dictionary representing the component with keys for "interior",
        "boundary", and "bounding_box".
    grid : np.ndarray
        A 2D NumPy array representing the UI grid.

    Returns:
    -------
    dict
        A dictionary of extracted features including:
        - 'border_type': int, type of border (single, double, heavy, rounded, or unknown).
        - 'is_button': int, 1 if the component matches button-like characteristics, otherwise 0.
        - 'is_text_field': int, 1 if the component matches text field characteristics, otherwise 0.
        - 'is_checkbox': int, indicates checkbox state (0 for none, 1 for unchecked, 2 for checked).
        - 'special_char_count': int, count of special characters found in the component.
    """
    features = {}

    # Get component data
    interior = component["interior"]
    boundary = component["boundary"]
    bounding_box = component["bounding_box"]
    x_min, y_min, x_max, y_max = bounding_box

    # Extract border type from boundary characters
    border_chars = [grid[y, x] for x, y in boundary]
    border_char_set = set(border_chars)

    if set("┌┐└┘│─").issubset(border_char_set):
        features["border_type"] = 1  # Single line
    elif set("╔╗╚╝║═").issubset(border_char_set):
        features["border_type"] = 2  # Double line
    elif set("┏┓┗┛┃━").issubset(border_char_set):
        features["border_type"] = 3  # Heavy line
    elif set("╭╮╰╯").issubset(border_char_set):
        features["border_type"] = 4  # Rounded
    else:
        features["border_type"] = 0  # Unknown or no border

    # Check for button-like characteristics
    content_chars = [grid[y, x] for x, y in interior]
    content_text = "".join(content_chars).strip()

    # Button patterns
    features["is_button"] = 0
    if (content_text.startswith("[") and content_text.endswith("]")) or (
        len(content_text) < 15 and component["width"] / component["height"] >= 2
    ):
        features["is_button"] = 1

    # Check for text field characteristics
    underscores = content_chars.count("_")
    empty_space = content_chars.count(" ")

    features["is_text_field"] = 0
    if underscores > 5 or (empty_space > 5 and component["width"] > 10):
        features["is_text_field"] = 1

    # Check for checkbox characteristics
    features["is_checkbox"] = 0
    if "□" in content_chars or "☐" in content_chars or "[ ]" in content_text:
        features["is_checkbox"] = 1
    elif "■" in content_chars or "☑" in content_chars or "[X]" in content_text:
        features["is_checkbox"] = 2  # Checked state

    # Count special characters
    special_chars = set("●○▼▶♢◆⊕⊖")
    features["special_char_count"] = sum(1 for c in content_chars if c in special_chars)

    return features
