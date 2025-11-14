# ClaudeUp 🚀

**Automate GitHub repository creation for Claude Code Web**

ClaudeUp eliminates the tedious manual steps required to set up a new GitHub repository for use with Claude Code Web. Built with modern Python tooling and [uv](https://docs.astral.sh/uv/) for blazingly fast performance.

With a single command, it:

- ✅ Creates a new private GitHub repository
- ✅ Initializes it locally with git
- ✅ **Installs the Claude GitHub App** (for proper Claude Code Web integration)
- ✅ Sets up initial files (README, .gitignore)
- ✅ Creates and pushes the initial commit
- ⚡ **Uses uv for 10-100x faster dependency management**

## Quick Start

### Prerequisites

- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer
- Git installed and configured
- A GitHub personal access token with `repo` scope
- **Claude GitHub App installed** on your account (install at [GitHub Apps](https://github.com/apps/claude) if you haven't already)

### Installation

#### Install uv (if you haven't already)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Or with homebrew
brew install uv
```

#### Option 1: Install with uv (Recommended)

```bash
uv pip install -e .
```

After installation, you can use `claudeup` command directly:

```bash
claudeup my-awesome-project
```

#### Option 2: Use directly

```bash
# Install dependencies
uv pip install -r requirements.txt

# Run directly
./claudeup my-awesome-project
# or
uv run claudeup.py my-awesome-project
```

### Setup GitHub Token

ClaudeUp needs a GitHub personal access token to create repositories and manage collaborators.

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a name (e.g., "ClaudeUp")
4. Select the `repo` scope (full control of private repositories)
5. Generate and copy the token

Set it as an environment variable:

```bash
export GITHUB_TOKEN=your_token_here
```

Or add to your `~/.bashrc` or `~/.zshrc` for persistence:

```bash
echo 'export GITHUB_TOKEN=your_token_here' >> ~/.bashrc
source ~/.bashrc
```

### Get Your Claude App Installation ID (One-time setup)

Because classic GitHub tokens can't list app installations, you'll need to provide the installation ID. **Do this once:**

1. Visit [GitHub Settings > Installations](https://github.com/settings/installations)
2. Click "Configure" next to the Claude app
3. Look at the URL in your browser - it ends with `/installations/XXXXXXXX`
4. Copy that number (e.g., `12345678`)
5. Add it to your `~/.bashrc` or `~/.zshrc`:

```bash
export CLAUDE_INSTALLATION_ID=12345678
```

6. Reload your shell:

```bash
source ~/.bashrc  # or source ~/.zshrc
```

**That's it!** ClaudeUp will automatically use this environment variable. No need to pass `--installation-id` every time.

Alternatively, you can pass it manually each time: `claudeup my-project --installation-id 12345678`

## Usage

### Basic Usage

```bash
# Create a new repository (uses CLAUDE_INSTALLATION_ID from environment)
claudeup my-project

# Create with a description
claudeup my-project -d "A cool new project"

# Create in a specific directory
claudeup my-project -p ~/projects/my-project

# Override environment with specific installation ID
claudeup my-project --installation-id 12345678

# Pass token directly (not recommended for security)
claudeup my-project --token ghp_yourtokenhere
```

### Advanced Options

```bash
# Skip installing GitHub App (not recommended)
claudeup my-project --no-app

# Use a custom GitHub App slug
claudeup my-project --app-slug my-custom-claude-app

# Create a public repository (default is private)
claudeup my-project --public

# Add a collaborator user (legacy method, not recommended)
claudeup my-project --add-collaborator --claude-username my-custom-bot

# Combine options
claudeup my-project \
  -d "My awesome project" \
  -p ~/projects/new-project \
  --app-slug claude
```

### Command-Line Options

```
positional arguments:
  repo_name             Name of the repository to create

optional arguments:
  -h, --help            Show this help message and exit
  -d, --description     Repository description
  -p, --path            Path to initialize repository (defaults to current directory)
  --token               GitHub personal access token (or set GITHUB_TOKEN env var)
  --installation-id     GitHub App installation ID (or set CLAUDE_INSTALLATION_ID env var)
  --no-app              Skip installing GitHub App (not recommended)
  --app-slug            GitHub App slug to install (default: claude)
  --add-collaborator    Add a collaborator user (legacy method, not recommended)
  --claude-username     GitHub username to add as collaborator (default: claude-code-app)
  --public              Create a public repository (default is private)
```

## What ClaudeUp Does

When you run ClaudeUp, here's what happens:

1. **Creates GitHub Repository**: Uses the GitHub API to create a new private repository under your account
2. **Installs Claude GitHub App**: Adds the repository to your Claude GitHub App installation (requires the app to be installed on your account first)
3. **Initializes Local Git**: Sets up a git repository in the specified directory
4. **Adds Remote**: Configures the GitHub repository as the remote origin
5. **Creates Initial Files**:
   - `README.md` with project name and description
   - `.gitignore` with common exclusions for Python, IDEs, and OS files
6. **Commits and Pushes**: Creates an initial commit and pushes to the main branch

## Examples

### Start a new Python project

```bash
claudeup ml-experiment -d "Machine learning experiment with Claude"
cd ml-experiment
# Start coding!
```

### Create multiple projects

```bash
for project in web-app api-server data-pipeline; do
  claudeup $project -p ~/projects/$project
done
```

### Use in a script

```bash
#!/bin/bash
# setup-project.sh

PROJECT_NAME="$1"
DESCRIPTION="$2"

if [ -z "$PROJECT_NAME" ]; then
  echo "Usage: $0 <project-name> [description]"
  exit 1
fi

# Create repo with ClaudeUp
claudeup "$PROJECT_NAME" -d "$DESCRIPTION"

# Add additional setup
cd "$PROJECT_NAME"
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Troubleshooting

### "Error: GitHub token not provided"

Make sure you've set the `GITHUB_TOKEN` environment variable:

```bash
export GITHUB_TOKEN=your_token_here
```

Or pass it directly with `--token`:

```bash
claudeup my-project --token ghp_yourtokenhere
```

### "Warning: GitHub App 'claude' not found in your installations"

This warning appears because classic GitHub Personal Access Tokens cannot list app installations (a GitHub API limitation). To fix:

**Solution 1: Set the environment variable (Recommended)**

1. Visit [GitHub Settings > Installations](https://github.com/settings/installations)
2. Click "Configure" next to the Claude app
3. Look at the URL - it ends with `/installations/XXXXXXXX`
4. Add to your `~/.bashrc` or `~/.zshrc`: `export CLAUDE_INSTALLATION_ID=XXXXXXXX`
5. Reload: `source ~/.bashrc`
6. Run claudeup again: `claudeup my-repo`

**Solution 2: Pass it on the command line**

Run: `claudeup my-repo --installation-id XXXXXXXX`

**Solution 3: Manually add the repository**

1. Visit [GitHub Settings > Installations](https://github.com/settings/installations)
2. Click "Configure" next to the Claude app
3. Under "Repository access", add your new repository

**Solution 4: Skip app installation (not recommended)**

Use `--no-app` to skip app installation entirely

### "Repository already exists"

If the repository name already exists on GitHub, ClaudeUp will notify you and attempt to use the existing repository for local setup.

### "Failed to add repository to GitHub App installation"

This can happen if:
- The app doesn't have permission to access the repository
- The app installation is configured for "selected repositories" and hasn't been set up properly
- Your token doesn't have the required `repo` scope

To fix:
1. Check your app installation settings at: https://github.com/settings/installations
2. Ensure the app has access to all repositories or add the specific repository
3. Verify your token has the `repo` scope

### Permission denied on push

If you get permission errors when pushing, make sure:
1. Your GitHub token has the `repo` scope
2. You have write access to the repository
3. Your git is configured with the correct credentials

## Configuration

### Custom Default Settings

You can create a configuration file at `~/.claudeup.json`:

```json
{
  "claude_username": "my-custom-claude-bot",
  "default_private": true,
  "default_description": "Created with ClaudeUp"
}
```

### SSH vs HTTPS

By default, ClaudeUp uses SSH URLs for git remotes (`git@github.com:user/repo.git`). If you prefer HTTPS, modify the `init_local_repo` method in `claudeup.py`.

## Development

### Running Tests

```bash
# Install dev dependencies
uv pip install --dev

# Run tests
uv run pytest tests/
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security Notes

- **Never commit your GitHub token** to version control
- Store tokens in environment variables or secure credential managers
- Use tokens with minimal required scopes
- Rotate tokens regularly
- Consider using GitHub Apps for organization-wide deployments

## License

MIT License - feel free to use this in your projects!

## FAQ

**Q: What's the difference between installing the GitHub App and adding a collaborator?**

A: Installing the GitHub App is the **proper way** for Claude Code Web integration. It gives Claude proper app-level permissions. Adding a collaborator is a legacy method that adds a user account with push access and is no longer needed or recommended.

**Q: Do I need to install the Claude GitHub App first?**

A: Yes! Before running claudeup:
1. Install the Claude GitHub App at https://github.com/apps/claude
2. Get your installation ID from https://github.com/settings/installations (look at the URL)
3. Set `export CLAUDE_INSTALLATION_ID=your_id` in your shell config
4. Run claudeup - it will automatically use the environment variable

**Q: Why do I need to provide the installation ID?**

A: Classic GitHub Personal Access Tokens (required for creating repos) cannot list GitHub App installations due to API limitations. Setting the `CLAUDE_INSTALLATION_ID` environment variable once bypasses this limitation - you never have to think about it again.

**Q: What permissions does ClaudeUp need?**

A: ClaudeUp needs a GitHub token with the `repo` scope to create repositories and add repositories to app installations.

**Q: Can I use this for organization repositories?**

A: Yes! Just make sure your token has access to the organization and you have permission to create repositories.

**Q: Does this work with GitHub Enterprise?**

A: Currently, ClaudeUp is designed for github.com. For GitHub Enterprise, you'd need to modify the `api_base` URL in the code.

**Q: Can I use this in CI/CD?**

A: Yes! Just make sure to pass the token securely (e.g., via encrypted environment variables).

## Why uv?

ClaudeUp uses [uv](https://docs.astral.sh/uv/) instead of pip because it's:

- **10-100x faster** than pip for package installation
- **Written in Rust** for maximum performance
- **Drop-in replacement** for pip with better dependency resolution
- **Modern tooling** that's becoming the standard in Python
- **Better caching** for repeated installations

## Related Tools

- [uv](https://docs.astral.sh/uv/) - Fast Python package installer (used by ClaudeUp)
- [GitHub CLI (gh)](https://cli.github.com/) - Official GitHub command-line tool
- [Ruff](https://docs.astral.sh/ruff/) - Fast Python linter (recommended for projects)
- [hub](https://hub.github.com/) - Extended git command-line tool
- [git-extras](https://github.com/tj/git-extras) - Additional git utilities

## Support

If you encounter issues or have questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review [GitHub's API documentation](https://docs.github.com/en/rest)
3. Open an issue on the repository

---

Made with ❤️ for Claude Code Web users
