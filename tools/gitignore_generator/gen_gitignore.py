#!/usr/bin/env python3
"""A script to generate a comprehensive .gitignore file for Python projects with Cursor IDE support."""

import os
import sys


def generate_gitignore(output_path=".gitignore"):
    """Generate a .gitignore file with common patterns for Python projects and Cursor IDE.

    Args:
        output_path (str): Path where the .gitignore file will be created. Default is current directory.
    """
    gitignore_content = """# Python specific
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Distribution / packaging
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
pythonenv*

# IDE specific files
# Cursor IDE
.cursor/
.cursor-cache/
cursor.json

# VS Code (commonly used with Cursor)
.vscode/
*.code-workspace
.history/

# PyCharm
.idea/
*.iml
*.iws
*.ipr
.idea_modules/

# Spyder
.spyderproject
.spyproject

# Rope
.ropeproject

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# Poetry
poetry.lock

# PyInstaller
dist/
build/

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media

# Flask
instance/
.webassets-cache

# Scrapy
.scrapy

# Sphinx
docs/_build/
doc/_build/

# Celery
celerybeat-schedule
celerybeat.pid

# SageMath
.sage/

# Spyder
.spyproject/

# Rope project settings
.ropeproject/

# mkdocs
/site

# OS specific
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
"""

    try:
        with open(output_path, "w") as f:
            f.write(gitignore_content)
        print(f".gitignore file successfully created at {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"Error creating .gitignore file: {e}", file=sys.stderr)
        return False

    return True


if __name__ == "__main__":
    # If a path is provided as an argument, use it; otherwise, use the default
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
        generate_gitignore(output_path)
    else:
        generate_gitignore()
