#!/bin/bash
# Example: Setup a complete Python project with ClaudeUp

set -e

PROJECT_NAME="${1:-my-python-project}"
DESCRIPTION="${2:-A Python project created with ClaudeUp}"

echo "Setting up Python project: $PROJECT_NAME"

# Create repository with ClaudeUp
claudeup "$PROJECT_NAME" -d "$DESCRIPTION"

# Navigate to project
cd "$PROJECT_NAME"

# Create Python project structure
mkdir -p src tests docs

# Create additional Python files
cat > src/__init__.py << 'EOF'
"""Main package initialization."""

__version__ = "0.1.0"
EOF

cat > src/main.py << 'EOF'
"""Main application entry point."""


def main():
    """Main function."""
    print("Hello from ClaudeUp project!")


if __name__ == "__main__":
    main()
EOF

cat > tests/__init__.py << 'EOF'
"""Tests package initialization."""
EOF

cat > tests/test_main.py << 'EOF'
"""Tests for main module."""

import pytest
from src.main import main


def test_main(capsys):
    """Test main function."""
    main()
    captured = capsys.readouterr()
    assert "Hello from ClaudeUp project!" in captured.out
EOF

# Create pyproject.toml with modern uv configuration
cat > pyproject.toml << EOF
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "$PROJECT_NAME"
version = "0.1.0"
description = "$DESCRIPTION"
requires-python = ">=3.8"
dependencies = [
    # Add your dependencies here
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
]

[tool.ruff]
line-length = 88
target-version = "py38"

[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = []

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
EOF

# Create virtual environment with uv
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies with uv
uv pip install -e ".[dev]"

# Update README with project details
cat >> README.md << 'EOF'

## Development

### Setup

This project uses [uv](https://docs.astral.sh/uv/) for fast dependency management.

1. Install uv (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

### Running Tests

```bash
uv run pytest tests/
```

### Code Formatting & Linting

```bash
# Format and lint with ruff
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

### Quick Commands

```bash
# Run the application
uv run python src/main.py

# Run tests with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Install a new dependency
uv pip install <package-name>

# Update all dependencies
uv pip install --upgrade -e ".[dev]"
```

## Project Structure

```
.
├── src/                 # Source code
│   ├── __init__.py
│   └── main.py
├── tests/              # Test files
│   ├── __init__.py
│   └── test_main.py
├── docs/               # Documentation
├── pyproject.toml      # Project configuration
└── README.md          # This file
```
EOF

# Commit the new structure
git add .
git commit -m "Add Python project structure and development setup"
git push

echo ""
echo "✅ Python project setup complete!"
echo "   Project: $PROJECT_NAME"
echo "   Location: $(pwd)"
echo ""
echo "To get started:"
echo "  cd $PROJECT_NAME"
echo "  source .venv/bin/activate"
echo "  uv run python src/main.py"
