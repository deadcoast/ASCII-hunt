import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


class MLImportSuggester:
    def __init__(self):
        """Initialize an MLImportSuggester.

        This class uses a TF-IDF vectorizer to convert code samples into feature vectors
        and a nearest neighbors model to suggest imports based on code similarity.

        Attributes:
            vectorizer: A TfidfVectorizer instance for transforming code samples.
            nn_model: A NearestNeighbors model for finding similar code samples.
            import_database: A list that stores correct imports for training.
        """
        self.vectorizer = TfidfVectorizer(analyzer="word", ngram_range=(1, 3))
        self.nn_model: NearestNeighbors | None = None
        self.import_database: list[list[str]] = []

    def train(self, code_samples: list[str], correct_imports: list[list[str]]) -> None:
        """Train the MLImportSuggester model using provided code samples and their correct imports.

        This method transforms code samples into feature vectors using a TF-IDF vectorizer
        and trains a nearest neighbors model to find similar code patterns.

        Args:
            code_samples: A list of code snippets to be used for training.
            correct_imports: A list of correct import statements corresponding
                           to each code snippet.
        """
        X = self.vectorizer.fit_transform(code_samples)

        # Train nearest neighbors model
        self.nn_model = NearestNeighbors(n_neighbors=5, algorithm="ball_tree")
        self.nn_model.fit(X)

        # Store import database
        self.import_database = correct_imports

    def suggest_imports(self, new_code: str) -> list[tuple[str, float]]:
        """Suggest imports for new code based on similar patterns.

        This method takes new code as input, transforms it into a feature vector
        using the trained vectorizer, finds similar code patterns using the
        nearest neighbors model, and weights the import suggestions by similarity.

        Args:
            new_code: The new code for which to suggest imports.

        Returns:
            A list of suggested imports, sorted by confidence,
            where each tuple contains the import statement and
            its confidence score.

        Raises:
            RuntimeError: If the model has not been trained yet.
        """
        if self.nn_model is None:
            raise RuntimeError(
                "Model must be trained before suggesting imports. Call train() first."
            )

        code_vector = self.vectorizer.transform([new_code])

        # Find similar code patterns
        # At this point nn_model is guaranteed to be a NearestNeighbors instance
        distances, indices = self.nn_model.kneighbors(code_vector)  # type: ignore

        # Weight suggestions by similarity
        weighted_suggestions = {}
        total_weight = np.sum(1.0 / (distances + 0.1))

        for i, idx in enumerate(indices[0]):
            weight = 1.0 / (distances[0][i] + 0.1) / total_weight
            for imp in self.import_database[idx]:
                if imp not in weighted_suggestions:
                    weighted_suggestions[imp] = 0
                weighted_suggestions[imp] += weight

        # Return suggestions sorted by confidence
        return sorted(weighted_suggestions.items(), key=lambda x: x[1], reverse=True)
