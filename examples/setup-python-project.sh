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

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Add your dependencies here
EOF

# Create requirements-dev.txt
cat > requirements-dev.txt << 'EOF'
-r requirements.txt
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=0.990
EOF

# Create pyproject.toml
cat > pyproject.toml << EOF
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "$PROJECT_NAME"
version = "0.1.0"
description = "$DESCRIPTION"
requires-python = ">=3.7"

[tool.black]
line-length = 88
target-version = ['py37', 'py38', 'py39', 'py310', 'py311']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
EOF

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements-dev.txt

# Update README with project details
cat >> README.md << 'EOF'

## Development

### Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/
```

### Linting

```bash
flake8 src/ tests/
mypy src/
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
├── requirements.txt    # Production dependencies
├── requirements-dev.txt # Development dependencies
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
echo "  source venv/bin/activate"
echo "  python src/main.py"
