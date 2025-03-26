"""Import correction model for analyzing and fixing Python imports."""

import re
from typing import Any

import numpy as np
import tensorflow as tf
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow import keras

# Local imports for integration
from ..import_driller.import_extractor import extract_imports_from_content


class ImportCorrectionModel:
    """A model for correcting and suggesting Python import statements.

    This model is trained on code with missing imports and their correct
    import statements. It uses two vectorizers to represent code and
    symbols, and a nearest neighbors model to predict the correct import
    for a given code snippet.

    Attributes:
        code_vectorizer: TfidfVectorizer for code snippets
        symbol_vectorizer: TfidfVectorizer for symbol names
        model: NearestNeighbors model for prediction
        training_data: List of (code, imports) for training
        n_import_sources: Number of possible import sources
        import_to_index: Mapping from import statements to indices
        _code_vocab_size: Size of code vocabulary after fitting
        _symbol_vocab_size: Size of symbol vocabulary after fitting
    """

    def __init__(self) -> None:
        """Initialize an ImportCorrectionModel."""
        self.code_vectorizer = TfidfVectorizer(analyzer="word", ngram_range=(1, 3))
        self.symbol_vectorizer = TfidfVectorizer()
        self.model: keras.Model | None = None
        self.training_data: list[dict[str, Any]] = []
        self.n_import_sources: int = 0
        self.import_to_index: dict[str, int] = {}
        # Initialize vocabulary sizes after fitting
        self._code_vocab_size: int = 0
        self._symbol_vocab_size: int = 0

    def preprocess_code(self, code: str) -> str:
        """Preprocess code by removing existing imports and normalizing.

        This helps to avoid bias when training the model and allows it to focus on
        the code itself, rather than being distracted by the existing imports.

        Args:
            code: Code snippet to preprocess.

        Returns:
            Preprocessed code snippet with imports removed and tokens normalized.
        """
        # Extract existing imports for reference
        existing_imports = extract_imports_from_content(code)

        # Remove existing imports to avoid bias
        code = re.sub(r"^\s*(import|from)[^\n]*", "", code, flags=re.MULTILINE)
        # Tokenize and normalize
        tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_]*", code)
        return " ".join(tokens)

    def build_model(self) -> keras.Model:
        """Build the neural network model for import correction.

        This method constructs and compiles a neural network model that predicts
        the probability distribution over possible import sources given code and
        symbol inputs.

        Returns:
            The compiled neural network model ready for training.
        """
        # Update vocabulary sizes after vectorizers are fitted
        self._code_vocab_size = (
            len(self.code_vectorizer.vocabulary_)
            if hasattr(self.code_vectorizer, "vocabulary_")
            else 100
        )
        self._symbol_vocab_size = (
            len(self.symbol_vectorizer.vocabulary_)
            if hasattr(self.symbol_vectorizer, "vocabulary_")
            else 50
        )

        # Input for code
        code_input = keras.layers.Input(shape=(self._code_vocab_size,))
        # Input for symbol
        symbol_input = keras.layers.Input(shape=(self._symbol_vocab_size,))

        # Process code context
        code_dense = keras.layers.Dense(256, activation="relu")(code_input)
        code_dropout = keras.layers.Dropout(0.3)(code_dense)

        # Process symbol
        symbol_dense = keras.layers.Dense(64, activation="relu")(symbol_input)
        symbol_dropout = keras.layers.Dropout(0.3)(symbol_dense)

        # Combine
        combined = keras.layers.Concatenate()([code_dropout, symbol_dropout])
        combined_dense = keras.layers.Dense(128, activation="relu")(combined)
        combined_dropout = keras.layers.Dropout(0.4)(combined_dense)

        # Output is a probability distribution over possible import sources
        output = keras.layers.Dense(self.n_import_sources, activation="softmax")(
            combined_dropout
        )

        self.model = keras.Model(inputs=[code_input, symbol_input], outputs=output)
        self.model.compile(
            optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
        )
        return self.model

    def collect_feedback(
        self,
        code_sample: str,
        symbol: str,
        predicted_import: str,
        actual_import: str,
        success: bool,
    ) -> None:
        """Collect feedback on the model's import predictions.

        Args:
            code_sample: The code snippet being analyzed.
            symbol: The symbol for which the import is predicted.
            predicted_import: The import predicted by the model.
            actual_import: The correct import for the symbol.
            success: A boolean indicating if the prediction was correct.
        """
        self.training_data.append(
            {
                "code": self.preprocess_code(code_sample),
                "symbol": symbol,
                "predicted": predicted_import,
                "actual": actual_import,
                "success": success,
            }
        )

    def retrain_on_feedback(self) -> None:
        """Retrain the import correction model based on collected feedback.

        This method uses the feedback collected during import predictions to
        retrain the model. It processes the training data by extracting code
        snippets and symbols, vectorizes them, and creates target vectors
        representing the desired import predictions.

        The model is trained to reinforce successful predictions and penalize
        incorrect ones, improving its accuracy over time.
        """
        if not self.training_data:
            return

        # Extract features
        codes = [item["code"] for item in self.training_data]
        symbols = [item["symbol"] for item in self.training_data]

        # Vectorize and update vocabulary sizes
        code_features = self.code_vectorizer.fit_transform(codes)
        symbol_features = self.symbol_vectorizer.fit_transform(symbols)
        self._code_vocab_size = len(self.code_vectorizer.vocabulary_)
        self._symbol_vocab_size = len(self.symbol_vectorizer.vocabulary_)

        # Rebuild model with updated vocabulary sizes if needed
        if self.model is None:
            self.build_model()

        # Create targets (one-hot encoded import sources)
        targets = []
        for item in self.training_data:
            target = np.zeros(self.n_import_sources)
            if item["success"]:
                # Reinforce successful prediction
                target[self.import_to_index[item["actual"]]] = 1.0
            else:
                # Penalize unsuccessful prediction
                target[self.import_to_index[item["predicted"]]] = -0.5
                if item["actual"] in self.import_to_index:
                    target[self.import_to_index[item["actual"]]] = 1.0

            targets.append(target)

        # Convert sparse matrices to dense numpy arrays
        code_features_dense = (
            code_features.toarray()
            if isinstance(code_features, csr_matrix)
            else np.array(code_features)
        )
        symbol_features_dense = (
            symbol_features.toarray()
            if isinstance(symbol_features, csr_matrix)
            else np.array(symbol_features)
        )
        targets_array = np.array(targets)

        # Convert numpy arrays to tensors
        code_tensor = tf.convert_to_tensor(code_features_dense, dtype=tf.float32)
        symbol_tensor = tf.convert_to_tensor(symbol_features_dense, dtype=tf.float32)
        targets_tensor = tf.convert_to_tensor(targets_array, dtype=tf.float32)

        # Train the model
        if self.model is not None:
            self.model.fit(
                [code_tensor, symbol_tensor],
                targets_tensor,
                epochs=5,
                batch_size=32,
                verbose=0,
            )
