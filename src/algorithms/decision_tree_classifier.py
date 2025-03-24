def build_decision_tree_classifier(training_data):
    """
    Implements a decision tree classifier for UI components.

    training_data: List of (feature_vector, component_type) pairs
    """
    from sklearn import tree
    import numpy as np

    # Extract features and labels
    X = []  # Features
    y = []  # Labels

    for features, component_type in training_data:
        # Create numerical feature vector
        feature_vector = [
            features["aspect_ratio"],
            features["border_density"],
            features["content_density"],
            features["border_type"],
            features["has_text"],
            features["text_alignment"],
            features["special_char_count"],
        ]
        X.append(feature_vector)
        y.append(component_type)

    # Convert to NumPy arrays
    X = np.array(X)
    y = np.array(y)

    # Create and train decision tree
    clf = tree.DecisionTreeClassifier(
        criterion="entropy", max_depth=8, min_samples_split=2
    )
    clf.fit(X, y)

    return clf


def extract_ui_specific_features(component, grid):
    """
    Extract UI-specific features for decision tree classification.
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
