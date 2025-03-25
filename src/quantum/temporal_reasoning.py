import ast
import datetime
import os
import pickle

import numpy as np
import temporal_logic
from git import Repo
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler


class TemporalImportReasoner:
    def __init__(self, repo_path: str, model_path: str | None = None) -> None:
        """Initialize the temporal import reasoner."""
        self.repo_path = repo_path
        self.repo = Repo(repo_path)
        self.temporal_graph: dict = {}
        self.import_evolution: dict = {}
        self.temporal_rules: dict = {}
        self.feature_scaler = StandardScaler()
        self.prediction_model = RandomForestClassifier(n_estimators=100)
        self.label_encoder = LabelEncoder()

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.build_temporal_model()

    def _iter_blobs(self, tree) -> list:
        """Iterate through all blobs in a git tree."""
        blobs = []
        for item in tree.traverse():
            if item.type == "blob":
                blobs.append(item)
        return blobs

    def _extract_imports(self, content: str) -> list:
        """Extract import statements from Python code content."""
        try:
            tree = ast.parse(content)
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(
                            {
                                "type": "import",
                                "module": name.name,
                                "alias": name.asname,
                            }
                        )
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    level = node.level
                    for name in node.names:
                        imports.append(
                            {
                                "type": "from",
                                "module": "." * level + module,
                                "name": name.name,
                                "alias": name.asname,
                            }
                        )
            return imports
        except Exception:
            return []

    def _import_to_str(self, imp: dict) -> str:
        """Convert import dict to string representation."""
        if imp["type"] == "import":
            result = f"import {imp['module']}"
            if imp.get("alias"):
                result += f" as {imp['alias']}"
        else:  # from import
            result = f"from {imp['module']} import {imp['name']}"
            if imp.get("alias"):
                result += f" as {imp['alias']}"
        return result

    def _extract_transition_features(self, transition: dict) -> list:
        """Extract features from a transition for the prediction model."""
        features = []

        # Time-based features
        features.append(transition["time_delta"])
        features.append(len(transition["added"]))
        features.append(len(transition["removed"]))

        # Calculate change rate
        total_changes = len(transition["added"]) + len(transition["removed"])
        change_rate = total_changes / max(transition["time_delta"], 1)
        features.append(change_rate)

        return features

    def _estimate_time_to_need(self, file_path: str, import_str: str) -> float:
        """Estimate time until an import will be needed."""
        if file_path not in self.temporal_rules:
            return float("inf")

        min_time = float("inf")
        for rule in self.temporal_rules[file_path]:
            if rule["conclusion"] == import_str:
                min_time = min(min_time, rule["avg_time_delta"])

        return min_time

    def load_model(self, model_path: str) -> None:
        """Load the temporal model from a file."""
        try:
            with open(model_path, "rb") as f:
                data = pickle.load(f)
                self.temporal_graph = data["temporal_graph"]
                self.import_evolution = data["import_evolution"]
                self.temporal_rules = data["temporal_rules"]
                self.feature_scaler = data["feature_scaler"]
                self.prediction_model = data["prediction_model"]
                if "label_encoder" in data:
                    self.label_encoder = data["label_encoder"]
        except Exception as e:
            print(f"Error loading model: {e}")
            self.build_temporal_model()

    def save_model(self, model_path: str) -> None:
        """Save the temporal model to a file."""
        data = {
            "temporal_graph": self.temporal_graph,
            "import_evolution": self.import_evolution,
            "temporal_rules": self.temporal_rules,
            "feature_scaler": self.feature_scaler,
            "prediction_model": self.prediction_model,
            "label_encoder": self.label_encoder,
        }
        with open(model_path, "wb") as f:
            pickle.dump(data, f)

    def apply_imports(self, file_path: str, imports: list) -> None:
        """Apply a list of imports to a file."""
        try:
            with open(file_path) as f:
                content = f.read()

            tree = ast.parse(content)

            # Remove existing imports
            new_body = [
                node
                for node in tree.body
                if not isinstance(node, (ast.Import, ast.ImportFrom))
            ]

            # Add new imports at the beginning
            import_nodes = []
            for imp in imports:
                if imp["type"] == "import":
                    names = [ast.alias(name=imp["module"], asname=imp.get("alias"))]
                    import_nodes.append(ast.Import(names=names))
                else:  # from import
                    module = imp["module"].lstrip(".")
                    level = len(imp["module"]) - len(module)
                    names = [ast.alias(name=imp["name"], asname=imp.get("alias"))]
                    import_nodes.append(
                        ast.ImportFrom(module=module or None, names=names, level=level)
                    )

            tree.body = import_nodes + new_body

            # Write back to file
            with open(file_path, "w") as f:
                f.write(ast.unparse(tree))

        except Exception as e:
            print(f"Error applying imports to {file_path}: {e}")

    def build_temporal_model(self):
        """Build a temporal model of how imports evolve over time."""
        print("Building temporal import evolution model...")

        # Get all commits
        commits = list(self.repo.iter_commits("master"))
        commits.reverse()  # Start with oldest

        # Track import patterns over time
        file_imports = {}  # file_path -> {commit_hash -> imports}

        for i, commit in enumerate(commits):
            if i % 100 == 0:
                print(f"Processing commit {i} of {len(commits)}")

            commit_date = datetime.datetime.fromtimestamp(commit.committed_date)

            try:
                # Get the commit tree
                tree = commit.tree

                # Find all Python files
                for blob in self._iter_blobs(tree):
                    if blob.path.endswith(".py"):
                        try:
                            # Extract imports
                            content = blob.data_stream.read().decode("utf-8")
                            imports = self._extract_imports(content)

                            # Store in temporal model
                            if blob.path not in file_imports:
                                file_imports[blob.path] = {}

                            file_imports[blob.path][commit.hexsha] = {
                                "imports": imports,
                                "date": commit_date,
                            }
                        except Exception:
                            # Skip files that can't be parsed
                            pass
            except Exception as e:
                # Skip problematic commits
                print(f"Skipping commit {commit.hexsha}: {e}")

        # Analyze import evolution
        for file_path, commit_data in file_imports.items():
            if len(commit_data) < 2:
                continue  # Skip files with only one commit

            # Sort commits by date
            sorted_commits = sorted(commit_data.items(), key=lambda x: x[1]["date"])

            # Analyze transitions
            transitions = []

            for i in range(1, len(sorted_commits)):
                prev_commit, prev_data = sorted_commits[i - 1]
                curr_commit, curr_data = sorted_commits[i]

                prev_imports = set(
                    self._import_to_str(imp) for imp in prev_data["imports"]
                )
                curr_imports = set(
                    self._import_to_str(imp) for imp in curr_data["imports"]
                )

                added = curr_imports - prev_imports
                removed = prev_imports - curr_imports

                if added or removed:
                    transitions.append(
                        {
                            "from_commit": prev_commit,
                            "to_commit": curr_commit,
                            "from_date": prev_data["date"],
                            "to_date": curr_data["date"],
                            "added": list(added),
                            "removed": list(removed),
                            "time_delta": (
                                curr_data["date"] - prev_data["date"]
                            ).total_seconds(),
                        }
                    )

            if transitions:
                self.import_evolution[file_path] = transitions

        # Extract temporal rules
        self._extract_temporal_rules()

        # Train the prediction model
        self._train_prediction_model()

        print("Temporal model built successfully.")

    def _extract_temporal_rules(self):
        """Extract temporal logic rules from import evolution data."""
        # Initialize rule structures
        for file_path, transitions in self.import_evolution.items():
            if file_path not in self.temporal_rules:
                self.temporal_rules[file_path] = []

            # Find patterns like "if import X is added, import Y is added within N commits"
            import_sequences = {}

            for i, transition in enumerate(transitions):
                for added_import in transition["added"]:
                    if added_import not in import_sequences:
                        import_sequences[added_import] = []

                    import_sequences[added_import].append(i)

            # Extract rules from sequences
            for import_a, seq_a in import_sequences.items():
                for import_b, seq_b in import_sequences.items():
                    if import_a != import_b:
                        # Check if import_b follows import_a within 3 transitions
                        follows_count = 0
                        total_follows = 0

                        for idx_a in seq_a:
                            for idx_b in seq_b:
                                if 0 < idx_b - idx_a <= 3:
                                    follows_count += 1
                                    time_delta = (
                                        transitions[idx_b]["from_date"]
                                        - transitions[idx_a]["to_date"]
                                    ).total_seconds()
                                    total_follows += 1

                        if follows_count >= 2 and follows_count / len(seq_a) > 0.5:
                            # Create a temporal rule
                            rule = {
                                "type": "follows",
                                "premise": import_a,
                                "conclusion": import_b,
                                "confidence": follows_count / len(seq_a),
                                "avg_time_delta": total_follows / follows_count
                                if total_follows
                                else 0,
                            }

                            # Create a temporal logic formula
                            rule["formula"] = temporal_logic.Eventually(
                                temporal_logic.Atom(f"has_import({import_b})"),
                                bound=datetime.timedelta(
                                    seconds=rule["avg_time_delta"]
                                ),
                            )

                            self.temporal_rules[file_path].append(rule)

    def _train_prediction_model(self):
        """Train a machine learning model to predict future import needs."""
        features = []
        labels = []

        for file_path, transitions in self.import_evolution.items():
            for i in range(len(transitions) - 1):
                curr = transitions[i]
                next_transition = transitions[i + 1]

                # Features from current state
                current_features = self._extract_transition_features(curr)

                # Label is the imports added in the next transition
                for added_import in next_transition["added"]:
                    features.append(current_features)
                    labels.append(added_import)

        if not features:
            print("No features extracted for prediction model")
            return

        # Scale features
        X = np.array(features)
        self.feature_scaler.fit(X)
        X_scaled = self.feature_scaler.transform(X)

        self.label_encoder = LabelEncoder()
        y = self.label_encoder.fit_transform(labels)

        # Train the model
        self.prediction_model.fit(X_scaled, y)

    def predict_future_imports(self, file_path, content, time_horizon=None):
        """Predict what imports may be needed in the future based on temporal patterns."""
        current_imports = self._extract_imports(content)
        current_import_strs = set(self._import_to_str(imp) for imp in current_imports)

        # Get current features
        if self.import_evolution.get(file_path):
            latest_transition = self.import_evolution[file_path][-1]
            features = self._extract_transition_features(latest_transition)
        else:
            # No history, use default features
            features = np.zeros(10)  # Match feature dimension

        # Scale features
        features_scaled = self.feature_scaler.transform([features])

        # Predict probabilities for all possible imports
        proba = self.prediction_model.predict_proba(features_scaled)[0]

        # Get top predictions
        top_indices = np.argsort(proba)[-10:][::-1]  # Top 10

        predictions = []
        for idx in top_indices:
            import_str = self.label_encoder.inverse_transform([idx])[0]
            probability = proba[idx]

            if import_str not in current_import_strs and probability > 0.3:
                predictions.append(
                    {
                        "import": import_str,
                        "probability": probability,
                        "estimated_time": self._estimate_time_to_need(
                            file_path, import_str
                        ),
                    }
                )

        # Apply temporal rules
        if file_path in self.temporal_rules:
            for rule in self.temporal_rules[file_path]:
                if (
                    rule["premise"] in current_import_strs
                    and rule["conclusion"] not in current_import_strs
                ):
                    # Check if this rule's conclusion is already in predictions
                    existing = [
                        p for p in predictions if p["import"] == rule["conclusion"]
                    ]

                    if existing:
                        # Increase confidence based on rule
                        existing[0]["probability"] = max(
                            existing[0]["probability"], rule["confidence"]
                        )
                        existing[0]["rule_based"] = True
                    else:
                        # Add new prediction from rule
                        predictions.append(
                            {
                                "import": rule["conclusion"],
                                "probability": rule["confidence"],
                                "estimated_time": datetime.timedelta(
                                    seconds=rule["avg_time_delta"]
                                ),
                                "rule_based": True,
                            }
                        )

        return predictions
