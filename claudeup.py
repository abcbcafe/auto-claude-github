#!/usr/bin/env python3
"""
ClaudeUp - Automate GitHub repository creation for Claude Code Web

This script automates the process of:
1. Creating a new private GitHub repository
2. Initializing it locally
3. Adding Claude as a collaborator
4. Setting up initial files and pushing
"""

import argparse
import json
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

    def __init__(self, token: str, claude_username: str = "claude-code-app"):
        """
        Initialize ClaudeUp.

        Args:
            token: GitHub personal access token
            claude_username: GitHub username to add as collaborator
        """
        self.token = token
        self.claude_username = claude_username
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
            print(f"✓ Repository '{repo_name}' created successfully")
            return response.json()
        elif response.status_code == 422:
            error_msg = response.json().get("message", "Unknown error")
            print(f"✗ Error: {error_msg}")
            if "already exists" in error_msg.lower():
                print(f"  Repository '{repo_name}' already exists")
                # Try to get the existing repo
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

    def add_collaborator(self, repo_full_name: str, username: str) -> bool:
        """
        Add a collaborator to the repository.

        Args:
            repo_full_name: Full repository name (owner/repo)
            username: GitHub username to add as collaborator

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.api_base}/repos/{repo_full_name}/collaborators/{username}"
        data = {"permission": "push"}

        response = requests.put(url, headers=self.headers, json=data)

        if response.status_code in [201, 204]:
            print(f"✓ Added '{username}' as collaborator")
            return True
        elif response.status_code == 404:
            print(f"⚠ Warning: User '{username}' not found on GitHub")
            print(f"  You may need to manually add the collaborator later")
            return False
        else:
            print(
                f"⚠ Warning: Failed to add collaborator: {response.status_code}"
            )
            print(f"  You may need to manually add '{username}' as a collaborator")
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
            print(f"✓ Initialized git repository in {path}")

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
            print(f"✓ Updated remote 'origin' to {ssh_url}")
        else:
            # Add new remote
            subprocess.run(["git", "remote", "add", "origin", ssh_url], check=True)
            print(f"✓ Added remote 'origin': {ssh_url}")

    def create_initial_files(self, path: Path, repo_name: str, description: str):
        """Create initial repository files."""
        # Create README.md
        readme_path = path / "README.md"
        if not readme_path.exists():
            readme_content = f"""# {repo_name}

{description if description else 'A project created with ClaudeUp'}

## About

This repository was automatically set up using ClaudeUp for use with Claude Code Web.

## Getting Started

[Add your getting started instructions here]
"""
            readme_path.write_text(readme_content)
            print(f"✓ Created README.md")

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
            print(f"✓ Created .gitignore")

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
            print("ℹ No changes to commit")
            return

        # Commit
        subprocess.run(
            ["git", "commit", "-m", "Initial commit via ClaudeUp"],
            check=True,
        )
        print(f"✓ Created initial commit")

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
            print(f"✓ Switched to branch '{branch}'")

        # Push to remote
        subprocess.run(
            ["git", "push", "-u", "origin", branch],
            check=True,
        )
        print(f"✓ Pushed to remote branch '{branch}'")

    def setup(
        self,
        repo_name: str,
        description: str = "",
        path: Optional[Path] = None,
        add_collaborator: bool = True,
    ):
        """
        Complete setup workflow.

        Args:
            repo_name: Name of the repository
            description: Repository description
            path: Path to initialize repository (defaults to current directory)
            add_collaborator: Whether to add Claude as collaborator
        """
        if path is None:
            path = Path.cwd()
        else:
            path = Path(path).resolve()
            path.mkdir(parents=True, exist_ok=True)

        print(f"\n🚀 ClaudeUp - Setting up repository '{repo_name}'...\n")

        # Create repository
        repo_data = self.create_repository(repo_name, description)

        # Add collaborator
        if add_collaborator and self.claude_username:
            self.add_collaborator(repo_data["full_name"], self.claude_username)

        # Initialize local repository
        self.init_local_repo(path, repo_data)

        # Create initial files
        self.create_initial_files(path, repo_name, description)

        # Commit and push
        try:
            self.commit_and_push()
        except subprocess.CalledProcessError as e:
            print(f"⚠ Warning: Failed to push to remote: {e}")
            print(f"  You can manually push later with: git push -u origin main")

        print(f"\n✅ Repository setup complete!")
        print(f"   URL: {repo_data['html_url']}")
        print(f"   Path: {path}")


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
        "--claude-username",
        default="claude-code-app",
        help="GitHub username to add as collaborator (default: claude-code-app)",
    )
    parser.add_argument(
        "--no-collaborator",
        action="store_true",
        help="Skip adding collaborator",
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

    # Create ClaudeUp instance
    claudeup = ClaudeUp(token, args.claude_username)

    # Run setup
    try:
        claudeup.setup(
            repo_name=args.repo_name,
            description=args.description,
            path=Path(args.path) if args.path else None,
            add_collaborator=not args.no_collaborator,
        )
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
