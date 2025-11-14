# ClaudeUp

Automate GitHub repository creation for Claude Code Web.

## What it does

- Creates a GitHub repository
- Installs the Claude GitHub App
- Initializes local git repository
- Creates initial files (README, .gitignore)
- Commits and pushes to the repository's default branch

## Prerequisites

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Git
- GitHub personal access token with `repo` scope
- [Claude GitHub App](https://github.com/apps/claude) installed on your account

## Installation

Install uv (recommended):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install claudeup:

```bash
uv pip install -e .
```

Or use directly:

```bash
uv pip install -r requirements.txt
./claudeup my-project
```

## Setup

### 1. GitHub Token

Create a token at [GitHub Settings > Tokens](https://github.com/settings/tokens) with `repo` scope.

```bash
export GITHUB_TOKEN=your_token_here
```

Add to `~/.bashrc` or `~/.zshrc` for persistence.

### 2. Claude App Installation ID

Get your installation ID once:

1. Visit [GitHub Settings > Installations](https://github.com/settings/installations)
2. Click "Configure" next to the Claude app
3. Copy the number from the URL: `/installations/XXXXXXXX`
4. Set environment variable:

```bash
export CLAUDE_INSTALLATION_ID=12345678
```

Add to `~/.bashrc` or `~/.zshrc` for persistence.

## Usage

Basic:

```bash
claudeup my-project
claudeup my-project -d "Project description"
claudeup my-project -p ~/projects/my-project
```

With installation ID override:

```bash
claudeup my-project --installation-id 12345678
```

Create public repository:

```bash
claudeup my-project --public
```

## Options

```
claudeup <repo_name> [options]

Arguments:
  repo_name             Repository name

Options:
  -d, --description     Repository description
  -p, --path            Path to initialize repository
  --token               GitHub token (or use GITHUB_TOKEN env var)
  --installation-id     App installation ID (or use CLAUDE_INSTALLATION_ID env var)
  --public              Create public repository (default: private)
  --no-app              Skip installing GitHub App
  --app-slug            Custom app slug (default: claude)
```

## Troubleshooting

**"Error: GitHub token not provided"**

Set the `GITHUB_TOKEN` environment variable or use `--token`.

**"Warning: GitHub App not found"**

Classic GitHub PATs can't list app installations. Set `CLAUDE_INSTALLATION_ID` environment variable or use `--installation-id`.

**Permission denied on push**

Ensure your token has `repo` scope and git is configured correctly.

## License

MIT
