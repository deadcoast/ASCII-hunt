import os
import pickle

import numpy as np
import tensorflow as tf
from tensorflow.keras import Model, layers


class NeuralImportPredictor:
    def __init__(self, model_path: str | None = None):
        """Initialize a NeuralImportPredictor.

        Args:
            model_path: Optional path to load a pre-trained model.
        """
        self.tokenizer: tf.keras.preprocessing.text.Tokenizer | None = None
        self.model: Model | None = None
        self.symbol_to_index: dict[str, int] = {}
        self.index_to_path: dict[int, str] = {}

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)

    def build_model(
        self, vocab_size: int, max_seq_length: int, num_import_paths: int
    ) -> None:
        """Build a neural network model for import prediction."""
        # Input layer for tokenized code
        inputs = layers.Input(shape=(max_seq_length,))

        # Embedding layer
        embedding = layers.Embedding(
            input_dim=vocab_size, output_dim=128, input_length=max_seq_length
        )(inputs)

        # Bidirectional LSTM layers
        lstm1 = layers.Bidirectional(layers.LSTM(128, return_sequences=True))(embedding)
        lstm2 = layers.Bidirectional(layers.LSTM(64))(lstm1)

        # Dense layers
        dense1 = layers.Dense(256, activation="relu")(lstm2)
        dropout = layers.Dropout(0.5)(dense1)

        # Output layer - probability distribution over import paths
        outputs = layers.Dense(num_import_paths, activation="softmax")(dropout)

        # Create the model
        model = tf.keras.Model(inputs=inputs, outputs=outputs)

        # Compile the model
        model.compile(
            optimizer="adam",
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )

        self.model = model

    def train(
        self,
        code_samples: list[str],
        symbols: list[str],
        import_paths: list[str],
        epochs: int = 10,
    ) -> None:
        """Train the model on code samples with known import paths."""
        # Tokenize code samples
        if self.tokenizer is None:
            self.tokenizer = tf.keras.preprocessing.text.Tokenizer()
            self.tokenizer.fit_on_texts(code_samples)

        x = self.tokenizer.texts_to_sequences(code_samples)
        max_seq_length = max(len(seq) for seq in x)
        x = tf.keras.preprocessing.sequence.pad_sequences(x, maxlen=max_seq_length)

        # Create mapping from symbols to import paths
        for symbol, path in zip(symbols, import_paths, strict=False):
            if symbol not in self.symbol_to_index:
                index = len(self.symbol_to_index)
                self.symbol_to_index[symbol] = index
                self.index_to_path[index] = path

        # Convert import paths to indices
        y = np.array([self.symbol_to_index[symbol] for symbol in symbols])

        # Build the model if it doesn't exist
        if self.model is None:
            vocab_size = len(self.tokenizer.word_index) + 1
            num_import_paths = len(self.symbol_to_index)
            self.build_model(vocab_size, max_seq_length, num_import_paths)

        # Ensure model exists after building
        if self.model is None:
            raise RuntimeError("Failed to build or load model")

        # Train the model
        self.model.fit(x, y, epochs=epochs, batch_size=32, validation_split=0.2)

    def predict_import_path(
        self, code_context: str, symbol: str
    ) -> list[tuple[str, float]]:
        """Predict the most likely import path for a symbol in a code context."""
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model not trained or loaded")

        # Tokenize the code context
        x = self.tokenizer.texts_to_sequences([code_context])
        x = tf.keras.preprocessing.sequence.pad_sequences(
            x, maxlen=self.model.input_shape[1]
        )

        # Predict the import path
        predictions = self.model.predict(x)[0]

        # Get the top 5 predictions
        top_indices = np.argsort(predictions)[-5:][::-1]

        results = []
        for idx in top_indices:
            if idx in self.index_to_path:
                path = self.index_to_path[idx]
                confidence = float(predictions[idx])
                results.append((path, confidence))

        return results

    def save_model(self, model_path: str) -> None:
        """Save the trained model and vocabulary."""
        if self.model is None:
            raise ValueError("No model to save. Train or load a model first.")

        # Save the Keras model
        self.model.save(f"{model_path}_model")

        # Save the tokenizer, symbol mappings
        with open(f"{model_path}_tokenizer.pkl", "wb") as f:
            pickle.dump(self.tokenizer, f)

        with open(f"{model_path}_mappings.pkl", "wb") as f:
            pickle.dump(
                {
                    "symbol_to_index": self.symbol_to_index,
                    "index_to_path": self.index_to_path,
                },
                f,
            )

    def load_model(self, model_path: str) -> None:
        """Load a trained model."""
        # Load the Keras model
        self.model = tf.keras.models.load_model(f"{model_path}_model")

        # Load the tokenizer
        with open(f"{model_path}_tokenizer.pkl", "rb") as f:
            self.tokenizer = pickle.load(f)

        # Load the mappings
        with open(f"{model_path}_mappings.pkl", "rb") as f:
            mappings = pickle.load(f)
            self.symbol_to_index = mappings["symbol_to_index"]
            self.index_to_path = mappings["index_to_path"]
