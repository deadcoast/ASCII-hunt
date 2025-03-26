import os
from typing import Any

try:
    import git
except ImportError:
    # Add fallback when git is not available
    git = None  # type: ignore

import numpy as np
from scipy import stats

# Import the missing extract_imports_from_content function
from src.import_miner.import_driller.import_extractor import \
    extract_imports_from_content

### 3. Bayesian Inference for Import Confidence


class BayesianImportConfidence:
    def __init__(self) -> None:
        """Initialize the BayesianImportConfidence object.

        The prior probabilities for import correctness are set to:

        - `prior_alpha`: 2 (correct examples)
        - `prior_beta`: 1 (incorrect examples)

        These values represent the initial confidence in the correctness of
        import statements, before any feedback is received.
        """
        self.prior_alpha = 2  # Correct examples
        self.prior_beta = 1  # Incorrect examples

    def update_confidence(
        self, suggestions: list[str], feedback: dict[str, bool]
    ) -> None:
        """Update confidence scores based on feedback.

        The feedback dictionary should have the following format:
        {
            'import_stmt1': True,
            'import_stmt2': False,
            ...
        }

        The confidence scores are updated by incrementing or decrementing
        the prior alpha and beta parameters based on the feedback.
        """
        for import_stmt, was_correct in feedback.items():
            if import_stmt in suggestions:
                # Update the beta distribution parameters
                if was_correct:
                    self.prior_alpha += 1
                else:
                    self.prior_beta += 1

    def get_confidence(self, suggestion: str, code_context: str) -> float:
        # Compute probability from beta distribution
        """Compute the confidence score for a suggestion in a given context.

        The confidence score is calculated as the mean of the beta distribution
        defined by the prior alpha and beta parameters.

        Parameters
        ----------
        suggestion : str
            The import statement to compute the confidence for.
        code_context : str
            The code context in which the import statement is suggested.

        Returns:
        -------
        confidence : float
            The confidence score in the range [0, 1].
        """
        # Calculate the beta distribution mean and return it as a float
        # Using type ignore as stats.beta.mean can return different types
        return float(stats.beta.mean(self.prior_alpha, self.prior_beta))  # type: ignore

    def sample_suggestions(
        self, suggestions: list[str], n_samples: int = 10
    ) -> list[str]:
        """Sample the suggestions using Thompson sampling.

        Parameters
        ----------
        suggestions : list[str]
            The list of import statements to sample from.
        n_samples : int, optional
            The number of samples to draw from the beta distribution.

        Returns:
        -------
        samples : list[str]
            The sorted list of import statements, sampled according to
            the confidence scores.
        """
        samples = np.random.beta(
            self.prior_alpha, self.prior_beta, size=(len(suggestions), n_samples)
        )
        mean_samples = np.mean(samples, axis=1)

        # Sort suggestions by sampled value
        sorted_idx = np.argsort(-mean_samples)
        return [suggestions[i] for i in sorted_idx]


## Advanced Import Tracking Techniques

### 1. Git Integration for Historical Analysis


def analyze_import_history(repo_path: str, file_path: str) -> list[dict[str, Any]]:
    """Analyze the evolution of import statements in a file over its Git history.

    Args:
        repo_path (str): The path to the Git repository.
        file_path (str): The path to the file within the repository to analyze.

    Returns:
        list[dict]: A list of dictionaries containing commit information and
            import statements for each commit. Each dictionary contains:
                - 'commit': The commit hash (str).
                - 'date': The datetime of the commit (datetime).
                - 'author': The name of the author (str).
                - 'imports': A list of import statements found in the file at
                  this commit (list).
    """
    if git is None:
        print("GitPython is not installed. Install it with: pip install GitPython")
        return []

    repo = git.Repo(repo_path)
    relative_path = os.path.relpath(file_path, repo_path)

    import_history = []
    for commit in repo.iter_commits(paths=relative_path, max_count=50):
        try:
            # Get the file content at this commit
            blob = commit.tree / relative_path
            content = blob.data_stream.read().decode("utf-8")

            # Extract imports
            imports = extract_imports_from_content(content)

            import_history.append(
                {
                    "commit": commit.hexsha,
                    "date": commit.committed_datetime,
                    "author": commit.author.name,
                    "imports": imports,
                }
            )
        except (OSError, UnicodeDecodeError, KeyError, AttributeError) as e:
            # File might not exist in this commit or have encoding issues
            # Log the specific error for debugging
            print(f"Error processing commit {commit.hexsha}: {e!s}")

    return import_history
