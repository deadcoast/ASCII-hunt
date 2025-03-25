### 1. Machine Learning with scikit-learn

import ast
import importlib.abc
import importlib.util
import inspect
import marshal
import os
import py_compile
import re
import statistics
import subprocess
import sys
import types
from ast import NodeTransformer
from types import ModuleType

import community as community_louvain
import git
import libcst as cst
import networkx as nx
import numpy as np
import sourcery
import symexec
import sympy as sp
import yaml
from libcst.metadata import ScopeProvider
from mypy import api as mypy_api
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork
from scipy import stats
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from tensorflow import keras
