from setuptools import find_packages, setup

setup(
    name="mermaid_connect",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "rich",
        "pyyaml",
        "networkx",
    ],
)
