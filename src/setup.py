from setuptools import find_packages, setup

setup(
    name="DIAGRAMS_FOR_TESTING_SCRIPT",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "rich",
        "pyyaml",
        "networkx",
    ],
)
