"""
CONFIG.PY

This configuration file defines constant paths and utility functions for Silk,
including retrieving the current directory and joining paths.
When packaged, `get_dir_path` points to the installation directory (e.g., `~/venv/Silk/Silk/`),
ensuring access to non-Python files like `schema.json`.
"""

import os


def get_dir_path() -> str:
    """Returns the path to the Silk run directory."""
    return os.path.dirname(os.path.abspath(__file__))


def join_paths(path1: str, path2: str) -> str:
    """Joins two paths together."""
    return os.path.join(path1, path2)


DEFAULT_PATH = os.getcwd()
WEAVER_DIR = join_paths(get_dir_path(), "Weavers/Chain")
SCHEMA_FILE = join_paths(get_dir_path(), "Web/schema.sql")
PROMPT_DIR = join_paths(get_dir_path(), "prompts")
