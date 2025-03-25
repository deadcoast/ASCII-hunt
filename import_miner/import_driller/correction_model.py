import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow import keras


class ImportCorrectionModel:
    def __init__(self):
        """
        Initialize an ImportCorrectionModel.

        This model is trained on code with missing imports and their correct
        import statements. It uses two vectorizers to represent code and
        symbols, and a nearest neighbors model to predict the correct import
        for a given code snippet.

        :param code_vectorizer: TfidfVectorizer for code snippets
        :param symbol_vectorizer: TfidfVectorizer for symbol names
        :param model: NearestNeighbors model
        :param training_data: List of (code, imports) for training
        """
        self.code_vectorizer = TfidfVectorizer(analyzer="word", ngram_range=(1, 3))
        self.symbol_vectorizer = TfidfVectorizer()
        self.model = None
        self.training_data = []

    def preprocess_code(self, code):
        # Remove existing imports to avoid bias
        """
        Preprocess code by removing existing imports and normalizing.

        This helps to avoid bias when training the model and allows it to focus on
        the code itself, rather than being distracted by the existing imports.

        :param code: Code snippet to preprocess
        :return: Preprocessed code snippet
        """
        code = re.sub(r"^\s*(import|from)[^\n]*", "", code, flags=re.MULTILINE)
        # Tokenize and normalize
        tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_]*", code)
        return " ".join(tokens)

    def build_model(self):
        # Input for code
        """
        Build the import correction model.

        The model takes two inputs: the code context and the symbol to be imported.
        The code context is processed with a dense layer and dropout, and the symbol
        is processed with a dense layer and dropout. The two are then combined and
        processed with two more dense layers with dropout. The output is a
        probability distribution over the possible import sources.

        The model is compiled with the Adam optimizer and categorical cross-entropy
        loss, and is trained to maximize accuracy.

        :return: The constructed model
        """
        code_input = keras.layers.Input(shape=(self.code_vectorizer.vocabulary_size_,))
        # Input for symbol
        symbol_input = keras.layers.Input(
            shape=(self.symbol_vectorizer.vocabulary_size_,)
        )

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

    def collect_feedback(
        self, code_sample, symbol, predicted_import, actual_import, success
    ):
        """
        Collect feedback on the model's import predictions.

        This method records feedback on the model's performance by storing the
        code sample, the symbol in question, the predicted import, the actual
        correct import, and whether the prediction was successful. The feedback
        is used for training to improve the model.

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

    def retrain_on_feedback(self):
        """
        Retrain the import correction model based on collected feedback.

        This method uses the feedback collected during import predictions to
        retrain the model. It processes the training data by extracting code
        snippets and symbols, vectorizes them, and creates target vectors
        representing the desired import predictions. Successful predictions are
        reinforced, while incorrect predictions are penalized. The model is then
        trained using these features and targets to improve its accuracy in
        predicting correct imports.

        The method assumes that feedback data has been collected and stored in
        `self.training_data`. If no training data is available, the method returns
        without performing any retraining.
        """

        if not self.training_data:
            return

        # Extract features
        codes = [item["code"] for item in self.training_data]
        symbols = [item["symbol"] for item in self.training_data]

        # Vectorize
        code_features = self.code_vectorizer.fit_transform(codes)
        symbol_features = self.symbol_vectorizer.fit_transform(symbols)

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

        targets = np.array(targets)

        # Train the model
        self.model.fit(
            [code_features, symbol_features],
            targets,
            epochs=5,
            batch_size=32,
            verbose=0,
        )
