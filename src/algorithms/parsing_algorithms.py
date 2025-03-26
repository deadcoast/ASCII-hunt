"""Parsing Algorithms Module."""

from typing import Any

import numpy as np
from numpy.typing import NDArray


class DistanceCalculator:
    """A class that calculates distances between components."""

    def __init__(self):
        """Initialize the DistanceCalculator class.

        This class is used to calculate distances between components.
        """

    def calculate_distance_matrix(
        self, features: list[dict[str, Any]]
    ) -> NDArray[np.float64]:
        """Calculate the distance matrix between components based on their features.

        Parameters
        ----------
        features : List[Dict[str, Any]]
            List of feature vectors for components

        Returns:
        -------
        NDArray[np.float64]
            The distance matrix between components
        """
        n = len(features)
        distance_matrix = np.zeros((n, n), dtype=np.float64)

        for i in range(n):
            for j in range(i + 1, n):
                # Convert feature dictionaries to float arrays
                feat_i = np.array(list(features[i].values()), dtype=np.float64)
                feat_j = np.array(list(features[j].values()), dtype=np.float64)

                # Calculate Euclidean distance between feature vectors
                diff = feat_i - feat_j
                distance = np.sqrt(np.sum(diff * diff))

                distance_matrix[i, j] = distance_matrix[j, i] = distance

        return distance_matrix


def needleman_wunsch(seq1, seq2, match_score=2, mismatch_penalty=-1, gap_penalty=-2):
    """Implements the Needleman-Wunsch algorithm for global sequence alignment.

    Parameters
    ----------
    seq1, seq2 : str
        The two sequences to be aligned.
    match_score : int
        The score for aligning two matching characters.
    mismatch_penalty : int
        The penalty for aligning two mismatching characters.
    gap_penalty : int
        The penalty for creating a gap in the alignment.

    Returns:
    -------
    score : int
        The optimal alignment score.
    align1 : str
        The aligned sequence 1.
    align2 : str
        The aligned sequence 2.
    """
    n, m = len(seq1), len(seq2)

    # Initialize score matrix
    score = np.zeros((n + 1, m + 1))

    # Initialize first row and column with gap penalties
    score[0, :] = np.arange(m + 1) * gap_penalty
    score[:, 0] = np.arange(n + 1) * gap_penalty

    # Fill the score matrix
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            match = score[i - 1, j - 1] + (
                match_score if seq1[i - 1] == seq2[j - 1] else mismatch_penalty
            )
            delete = score[i - 1, j] + gap_penalty
            insert = score[i, j - 1] + gap_penalty
            score[i, j] = max(match, delete, insert)

    # Traceback to find the optimal alignment
    align1, align2 = [], []
    i, j = n, m

    while i > 0 or j > 0:
        if (
            i > 0
            and j > 0
            and score[i, j]
            == score[i - 1, j - 1]
            + (match_score if seq1[i - 1] == seq2[j - 1] else mismatch_penalty)
        ):
            align1.append(seq1[i - 1])
            align2.append(seq2[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and score[i, j] == score[i - 1, j] + gap_penalty:
            align1.append(seq1[i - 1])
            align2.append("-")
            i -= 1
        else:
            align1.append("-")
            align2.append(seq2[j - 1])
            j -= 1

    # Reverse the alignments
    align1 = align1[::-1]
    align2 = align2[::-1]

    return score[n, m], "".join(align1), "".join(align2)


def levenshtein_distance(str1, str2):
    """Implements the Levenshtein distance (edit distance) algorithm."""
    n, m = len(str1), len(str2)

    # Create a matrix to store the edit distances
    dp = np.zeros((n + 1, m + 1), dtype=int)

    # Initialize the first row and column
    dp[0, :] = np.arange(m + 1)
    dp[:, 0] = np.arange(n + 1)

    # Fill the matrix
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i, j] = dp[i - 1, j - 1]
            else:
                dp[i, j] = min(
                    dp[i - 1, j] + 1,  # deletion
                    dp[i, j - 1] + 1,  # insertion
                    dp[i - 1, j - 1] + 1,  # substitution
                )

    return dp[n, m]


def longest_common_subsequence(str1, str2):
    """Implements the Longest Common Subsequence algorithm.

    Parameters
    ----------
    str1, str2 : str
        The two strings to be compared.

    Returns:
    -------
    lcs : str
        The longest common subsequence of str1 and str2.
    """
    n, m = len(str1), len(str2)

    # Create a matrix to store the lengths of LCS
    L = np.zeros((n + 1, m + 1), dtype=int)

    # Fill the matrix
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if str1[i - 1] == str2[j - 1]:
                L[i, j] = L[i - 1, j - 1] + 1
            else:
                L[i, j] = max(L[i - 1, j], L[i, j - 1])

    # Reconstruct the LCS
    lcs = []
    i, j = n, m

    while i > 0 and j > 0:
        if str1[i - 1] == str2[j - 1]:
            lcs.append(str1[i - 1])
            i -= 1
            j -= 1
        elif L[i - 1, j] >= L[i, j - 1]:
            i -= 1
        else:
            j -= 1

    return "".join(reversed(lcs))


def pattern_match_with_dp(pattern, grid, threshold=0.8):
    """Uses dynamic programming to find pattern matches in a grid.

    Parameters
    ----------
    pattern : 2D list of str
        The pattern to be matched.
    grid : 2D array of str
        The grid to search for the pattern.
    threshold : float, optional
        The minimum similarity required for a match, by default 0.8.

    Returns:
    -------
    matches : list of dict
        A list of dictionaries containing the position (x, y) and similarity of each match.
    """
    height, width = grid.shape
    pattern_height, pattern_width = len(pattern), len(pattern[0])

    matches = []

    # Convert pattern to string for each row
    pattern_rows = ["".join(row) for row in pattern]

    # Sliding window search through the grid
    for y in range(height - pattern_height + 1):
        for x in range(width - pattern_width + 1):
            # Extract sub-grid
            sub_grid = grid[y : y + pattern_height, x : x + pattern_width]

            # Convert sub-grid to string for each row
            sub_grid_rows = ["".join(row) for row in sub_grid]

            # Calculate similarity using Levenshtein distance for each row
            similarity_scores = []
            for i in range(pattern_height):
                max_len = max(len(pattern_rows[i]), len(sub_grid_rows[i]))
                if max_len == 0:
                    similarity_scores.append(1.0)  # Empty rows are identical
                else:
                    distance = levenshtein_distance(pattern_rows[i], sub_grid_rows[i])
                    similarity = 1.0 - (distance / max_len)
                    similarity_scores.append(similarity)

            # Average similarity across all rows
            avg_similarity = sum(similarity_scores) / len(similarity_scores)

            # If similarity is above threshold, consider it a match
            if avg_similarity >= threshold:
                matches.append({"position": (x, y), "similarity": avg_similarity})

    return matches
