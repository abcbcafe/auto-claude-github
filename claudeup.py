#!/usr/bin/env python3
"""
ClaudeUp - Automate GitHub repository creation for Claude Code Web

Automates:
1. Creating a GitHub repository
2. Installing the Claude GitHub App
3. Initializing local git repository
4. Creating initial files and pushing
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install with: pip install requests")
    sys.exit(1)


class ClaudeUp:
    """Automate GitHub repository setup for Claude Code Web sessions."""

    def __init__(self, token: str):
        """
        Initialize ClaudeUp.

        Args:
            token: GitHub personal access token
        """
        self.token = token
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def create_repository(
        self,
        repo_name: str,
        description: str = "",
        private: bool = True,
    ) -> dict:
        """
        Create a new GitHub repository.

        Args:
            repo_name: Name of the repository
            description: Repository description
            private: Whether the repository should be private

        Returns:
            Repository data from GitHub API
        """
        url = f"{self.api_base}/user/repos"
        data = {
            "name": repo_name,
            "description": description,
            "private": private,
            "auto_init": False,  # We'll initialize locally
        }

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 201:
            print(f"Repository '{repo_name}' created successfully")
            return response.json()
        elif response.status_code == 422:
            error_msg = response.json().get("message", "Unknown error")
            print(f"Error: {error_msg}")
            if "already exists" in error_msg.lower():
                print(f"Repository '{repo_name}' already exists")
                return self.get_repository(repo_name)
            raise Exception(f"Failed to create repository: {error_msg}")
        else:
            raise Exception(
                f"Failed to create repository: {response.status_code} - {response.text}"
            )

    def get_repository(self, repo_name: str) -> dict:
        """Get repository information."""
        # Get the authenticated user first
        user_response = requests.get(
            f"{self.api_base}/user", headers=self.headers
        )
        if user_response.status_code != 200:
            raise Exception("Failed to get user information")

        username = user_response.json()["login"]
        url = f"{self.api_base}/repos/{username}/{repo_name}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get repository: {response.status_code}")

    def list_installations(self) -> list:
        """
        List GitHub App installations for the authenticated user.

        Returns:
            List of installation objects
        """
        url = f"{self.api_base}/user/installations"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            return data.get("installations", [])
        else:
            print(f"Warning: Failed to list installations: {response.status_code}")
            return []

    def find_app_installation(self, app_slug: str) -> Optional[dict]:
        """
        Find a specific GitHub App installation by app slug.

        Args:
            app_slug: The slug/name of the GitHub App

        Returns:
            Installation object if found, None otherwise
        """
        installations = self.list_installations()

        for installation in installations:
            app = installation.get("app_slug") or installation.get("account", {}).get("login", "")
            if app_slug.lower() in app.lower():
                return installation

        return None

    def add_repo_to_app_installation(self, installation_id: int, repo_id: int) -> bool:
        """
        Add a repository to a GitHub App installation.

        Args:
            installation_id: The installation ID of the GitHub App
            repo_id: The repository ID

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.api_base}/user/installations/{installation_id}/repositories/{repo_id}"
        response = requests.put(url, headers=self.headers)

        if response.status_code in [204]:
            return True
        elif response.status_code == 304:
            # Repository already added
            return True
        else:
            return False

    def install_github_app(
        self,
        repo_data: dict,
        app_slug: str = "claude",
        installation_id: Optional[int] = None,
    ) -> bool:
        """
        Install a GitHub App on the repository.

        Args:
            repo_data: Repository data from GitHub API
            app_slug: The slug/name of the GitHub App to install
            installation_id: Optional installation ID to use directly

        Returns:
            True if successful, False otherwise
        """
        # If installation ID is provided, use it directly
        if installation_id:
            repo_id = repo_data.get("id")
            if not repo_id:
                print("Warning: Could not get repository ID")
                return False

            success = self.add_repo_to_app_installation(installation_id, repo_id)
            if success:
                print(f"Added repository to GitHub App installation (ID: {installation_id})")
                return True
            else:
                print("Warning: Failed to add repository to GitHub App installation")
                print(f"Verify the installation ID is correct: {installation_id}")
                print("Check your app settings at: https://github.com/settings/installations")
                return False

        # Otherwise, try to find the app installation
        installation = self.find_app_installation(app_slug)

        if not installation:
            print(f"Warning: GitHub App '{app_slug}' not found in your installations")
            print("")
            print("Classic GitHub PATs cannot list app installations.")
            print("To fix this, you have two options:")
            print("")
            print("Option 1: Provide the installation ID")
            print("  1. Visit: https://github.com/settings/installations")
            print("  2. Click 'Configure' next to the Claude app")
            print("  3. Look at the URL - it ends with /installations/XXXXXXXX")
            print(f"  4. Run: claudeup --installation-id XXXXXXXX {repo_data.get('name', '')}")
            print("")
            print("Option 2: Manually add the repository")
            print("  1. Visit: https://github.com/settings/installations")
            print("  2. Click 'Configure' next to the Claude app")
            print(f"  3. Add the repository: {repo_data.get('full_name', '')}")
            return False

        installation_id = installation.get("id")
        repo_id = repo_data.get("id")

        if not installation_id or not repo_id:
            print("Warning: Could not get installation ID or repository ID")
            return False

        # Add repository to the app installation
        success = self.add_repo_to_app_installation(installation_id, repo_id)

        if success:
            app_name = installation.get("app_slug", app_slug)
            print(f"Added repository to '{app_name}' GitHub App installation")
            return True
        else:
            print("Warning: Failed to add repository to GitHub App installation")
            print("You may need to manually add the repository in the app settings")
            return False

    def init_local_repo(self, path: Path, repo_data: dict):
        """
        Initialize local git repository.

        Args:
            path: Path to initialize repository in
            repo_data: Repository data from GitHub API
        """
        os.chdir(path)

        # Initialize git if not already initialized
        if not (path / ".git").exists():
            subprocess.run(["git", "init"], check=True)
            print(f"Initialized git repository in {path}")

        # Set remote
        clone_url = repo_data["clone_url"]
        # Convert to SSH URL if using HTTPS
        if clone_url.startswith("https://github.com/"):
            ssh_url = clone_url.replace(
                "https://github.com/", "git@github.com:"
            )
        else:
            ssh_url = clone_url

        # Check if remote exists
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Remote exists, update it
            subprocess.run(["git", "remote", "set-url", "origin", ssh_url], check=True)
            print(f"Updated remote 'origin' to {ssh_url}")
        else:
            # Add new remote
            subprocess.run(["git", "remote", "add", "origin", ssh_url], check=True)
            print(f"Added remote 'origin': {ssh_url}")

    def create_initial_files(self, path: Path, repo_name: str, description: str, instructions: Optional[str] = None):
        """Create initial repository files."""
        # Create README.md
        readme_path = path / "README.md"
        if not readme_path.exists():
            readme_content = f"""# {repo_name}

{description if description else 'A project created with ClaudeUp'}

## Getting Started

[Add your getting started instructions here]
"""
            readme_path.write_text(readme_content)
            print("Created README.md")

        # Create .gitignore
        gitignore_path = path / ".gitignore"
        if not gitignore_path.exists():
            gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment variables
.env
.env.local
"""
            gitignore_path.write_text(gitignore_content)
            print("Created .gitignore")

        # Create .claude/TASK.md with instructions if provided
        if instructions:
            claude_dir = path / ".claude"
            claude_dir.mkdir(exist_ok=True)
            task_path = claude_dir / "TASK.md"
            task_content = f"""# Initial Task

{instructions}

---
*This file was automatically created by ClaudeUp. You can delete it after completing the task.*
"""
            task_path.write_text(task_content)
            print("Created .claude/TASK.md with your instructions")

    def commit_and_push(self, branch: str = "main"):
        """Create initial commit and push to GitHub."""
        # Add all files
        subprocess.run(["git", "add", "."], check=True)

        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True,
        )

        if result.returncode == 0:
            print("No changes to commit")
            return

        # Commit
        subprocess.run(
            ["git", "commit", "-m", "Initial commit via ClaudeUp"],
            check=True,
        )
        print("Created initial commit")

        # Create and checkout branch if not on it
        current_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        if current_branch != branch:
            # Check if branch exists
            branch_exists = subprocess.run(
                ["git", "rev-parse", "--verify", branch],
                capture_output=True,
            ).returncode == 0

            if branch_exists:
                subprocess.run(["git", "checkout", branch], check=True)
            else:
                subprocess.run(["git", "checkout", "-b", branch], check=True)
            print(f"Switched to branch '{branch}'")

        # Push to remote
        subprocess.run(
            ["git", "push", "-u", "origin", branch],
            check=True,
        )
        print(f"Pushed to remote branch '{branch}'")

    def setup(
        self,
        repo_name: str,
        description: str = "",
        path: Optional[Path] = None,
        install_app: bool = True,
        app_slug: str = "claude",
        installation_id: Optional[int] = None,
        instructions: Optional[str] = None,
    ):
        """
        Complete setup workflow.

        Args:
            repo_name: Name of the repository
            description: Repository description
            path: Path to initialize repository (defaults to current directory)
            install_app: Whether to install the Claude GitHub App
            app_slug: The slug/name of the GitHub App to install
            installation_id: Optional GitHub App installation ID
            instructions: Optional instructions to save for Claude Code web
        """
        if path is None:
            path = Path.cwd()
        else:
            path = Path(path).resolve()
            path.mkdir(parents=True, exist_ok=True)

        print(f"\nClaudeUp - Setting up repository '{repo_name}'...\n")

        # Create repository
        repo_data = self.create_repository(repo_name, description)

        # Install GitHub App
        if install_app:
            self.install_github_app(repo_data, app_slug, installation_id)

        # Initialize local repository
        self.init_local_repo(path, repo_data)

        # Create initial files
        self.create_initial_files(path, repo_name, description, instructions)

        # Commit and push
        try:
            self.commit_and_push()
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to push to remote: {e}")
            print("You can manually push later with: git push -u origin main")

        print(f"\nRepository setup complete!")
        print(f"URL: {repo_data['html_url']}")
        print(f"Path: {path}")

        # Display Claude Code web instructions if instructions were provided
        if instructions:
            print(f"\n{'='*60}")
            print("NEXT STEPS: Start Claude Code Web Session")
            print(f"{'='*60}")
            print(f"\n1. Open Claude Code web: https://claude.ai/code")
            print(f"2. Select or search for your repository: {repo_data['full_name']}")
            print(f"3. Your task has been saved to .claude/TASK.md")
            print(f"\n   You can copy-paste this task to Claude Code web:")
            print(f"\n   {'-'*56}")
            print(f"   {instructions}")
            print(f"   {'-'*56}")
            print(f"\nAlternatively, you can ask Claude to read .claude/TASK.md")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ClaudeUp - Automate GitHub repository creation for Claude Code Web"
    )
    parser.add_argument(
        "repo_name",
        help="Name of the repository to create",
    )
    parser.add_argument(
        "instructions",
        nargs="?",
        default=None,
        help="Optional instructions to send to Claude Code web",
    )
    parser.add_argument(
        "-d",
        "--description",
        default="",
        help="Repository description",
    )
    parser.add_argument(
        "-p",
        "--path",
        help="Path to initialize repository (defaults to current directory)",
    )
    parser.add_argument(
        "--token",
        help="GitHub personal access token (or set GITHUB_TOKEN environment variable)",
    )
    parser.add_argument(
        "--no-app",
        action="store_true",
        help="Skip installing GitHub App",
    )
    parser.add_argument(
        "--app-slug",
        default="claude",
        help="GitHub App slug to install (default: claude)",
    )
    parser.add_argument(
        "--installation-id",
        type=int,
        help="GitHub App installation ID (or set CLAUDE_INSTALLATION_ID env var)",
    )
    parser.add_argument(
        "--public",
        action="store_true",
        help="Create a public repository (default is private)",
    )

    args = parser.parse_args()

    # Get GitHub token
    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GitHub token not provided")
        print("  Set GITHUB_TOKEN environment variable or use --token flag")
        print("\nTo create a token:")
        print("  1. Go to https://github.com/settings/tokens")
        print("  2. Generate a new token with 'repo' scope")
        print("  3. Set it as: export GITHUB_TOKEN=your_token_here")
        sys.exit(1)

    # Get installation ID from args or environment variable
    installation_id = args.installation_id
    if installation_id is None:
        env_installation_id = os.environ.get("CLAUDE_INSTALLATION_ID")
        if env_installation_id:
            try:
                installation_id = int(env_installation_id)
            except ValueError:
                print(f"Warning: CLAUDE_INSTALLATION_ID env var is not a valid number: {env_installation_id}")

    # Create ClaudeUp instance
    claudeup = ClaudeUp(token)

    # Run setup
    try:
        claudeup.setup(
            repo_name=args.repo_name,
            description=args.description,
            path=Path(args.path) if args.path else None,
            install_app=not args.no_app,
            app_slug=args.app_slug,
            installation_id=installation_id,
            instructions=args.instructions,
        )
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
