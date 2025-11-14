# Changelog

All notable changes to ClaudeUp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-14

### Added
- Initial release of ClaudeUp
- Automated GitHub repository creation
- Automatic private repository setup
- Collaborator management (add Claude to repos)
- Local git initialization and remote setup
- Initial file creation (README.md, .gitignore)
- Automatic commit and push to main branch
- CLI interface with argparse
- Support for custom repository descriptions
- Support for custom installation paths
- Environment variable support for GitHub token
- Shell wrapper script for easy execution
- Comprehensive README with examples
- Setup.py for pip installation

### Features
- Create private repositories by default (with --public option)
- Add collaborators via GitHub API
- Initialize local git repositories
- Set up git remotes automatically
- Create and push initial commits
- Customizable Claude username
- Skip collaborator option (--no-collaborator)
- Detailed console output with status indicators
- Error handling and helpful error messages

### Security
- GitHub token via environment variable
- No token storage in code
- .gitignore includes token files
- Secure API communication
