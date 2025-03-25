import numpy as np
import tensorflow as tf
import torch
from scipy import optimize
from sklearn.manifold import TSNE
import networkx as nx
import sympy as sp
import jax
import jax.numpy as jnp
from typing import Dict, List, Tuple, Set, Any, Optional, Union, Callable
import math
from collections import defaultdict
import re
import ast
import os
import sys
import time
import random
import hashlib
from dataclasses import dataclass, field
from functools import partial, lru_cache
import multiprocessing
from concurrent.futures import ThreadPoolExecutor


class NonlinearManifoldMapper:
    """Maps imports onto a nonlinear manifold to identify structural relationships."""

    def __init__(self, embedding_dim=128, manifold_dim=32):
        self.embedding_dim = embedding_dim
        self.manifold_dim = manifold_dim
        self.projection_matrices = self._initialize_projections()

    def _initialize_projections(self):
        """Initialize a set of random projection matrices."""
        projections = []

        # Create several random projection matrices for ensemble mapping
        for _ in range(5):
            matrix = np.random.normal(0, 1, (self.embedding_dim, self.manifold_dim))
            # Orthogonalize using QR decomposition
            q, _ = np.linalg.qr(matrix)
            projections.append(q)

        return projections

    def compute_manifold_coordinates(self, tensor):
        """Project a tensor onto the nonlinear manifold."""
        # Flatten the tensor to a vector
        flattened = tensor.flatten()

        # Ensure the vector has the right dimensionality
        if len(flattened) < self.embedding_dim:
            padded = np.zeros(self.embedding_dim)
            padded[: len(flattened)] = flattened
            flattened = padded
        elif len(flattened) > self.embedding_dim:
            flattened = flattened[: self.embedding_dim]

        # Apply nonlinear projections
        manifold_coords = []

        for proj_matrix in self.projection_matrices:
            # Linear projection
            linear_proj = np.dot(flattened, proj_matrix)

            # Apply nonlinearity (sinusoidal) to create curved manifold
            nonlinear_proj = np.sin(linear_proj * np.pi / 2)

            manifold_coords.append(nonlinear_proj)

        # Concatenate all projections
        return np.concatenate(manifold_coords)

    def compute_manifold_distance(self, coords1, coords2):
        """Compute distance between points on the manifold."""
        # Split coordinates by projection
        n_projections = len(self.projection_matrices)
        proj_dim = len(coords1) // n_projections

        # Compute distance for each projection
        distances = []

        for i in range(n_projections):
            start = i * proj_dim
            end = (i + 1) * proj_dim

            # Compute geodesic-inspired distance on nonlinear manifold
            diff = coords1[start:end] - coords2[start:end]

            # Adjust for the nonlinear curvature of the manifold
            curvature_factor = 0.5 * (
                np.mean(np.abs(coords1[start:end]))
                + np.mean(np.abs(coords2[start:end]))
            )

            # Scale by curvature to approximate geodesic distance
            curved_distance = np.sqrt(np.sum(diff**2)) * (1 + 0.2 * curvature_factor)
            distances.append(curved_distance)

        # Take the minimum distance across projections (approximates true geodesic)
        return np.min(distances)

    def find_nearest_neighbors(self, reference_coords, all_coords, k=5):
        """Find the k nearest neighbors on the manifold."""
        distances = []

        for i, coords in enumerate(all_coords):
            dist = self.compute_manifold_distance(reference_coords, coords)
            distances.append((i, dist))

        # Sort by distance
        sorted_neighbors = sorted(distances, key=lambda x: x[1])

        # Return indices of nearest neighbors
        return [idx for idx, _ in sorted_neighbors[:k]]
