# File: setup.py (project root)
"""Setup script for namespace_extractor package."""

from setuptools import find_packages, setup

setup(
    name="namespace_extractor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=5.1",
        "tqdm>=4.50.0",
    ],
    entry_points={
        "console_scripts": [
            "namespace-extractor=namespace_extractor.__main__:main",
        ],
    },
    author="Python Developer",
    author_email="developer@example.com",
    description="A tool to extract and document Python code structure",
    keywords="python, ast, documentation, extraction",
    python_requires=">=3.6",
)
