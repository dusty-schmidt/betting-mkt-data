# uv Cheat Sheet

`uv` is a fast Python package installer and resolver.

## Basics

| Command | Description |
|---------|-------------|
| `uv init` | Initialize a new project (creates `pyproject.toml`). |
| `uv sync` | Install dependencies from `pyproject.toml` into `.venv`. |
| `uv add <package>` | Add a package to `pyproject.toml` and install it. |
| `uv remove <package>` | Remove a package. |
| `uv run <command>` | Run a command in the project's virtual environment (e.g., `uv run python run.py`). |

## Dependencies

| Command | Description |
|---------|-------------|
| `uv add --dev <package>` | Add a development dependency (e.g., `pytest`). |
| `uv sync --extra <name>` | Install optional dependencies (e.g., `uv sync --extra test`). |

## Python Versions

| Command | Description |
|---------|-------------|
| `uv python install 3.12` | Install a specific Python version. |
| `uv venv --python 3.12` | Create a virtual environment with a specific version. |

## Workflow Example

```bash
# Start fresh
uv init

# Add dependencies
uv add flask pydantic

# Run your app
uv run python run.py

# Run tests
uv add --dev pytest
uv run pytest
```
