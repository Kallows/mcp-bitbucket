# MCP Bitbucket Python 🦊

A Python implementation of an MCP server for Bitbucket integration. MCP (Model Context Protocol) enables secure, local tool access for AI applications. The server runs locally on the same machine as your AI application.

## Installation

```bash
# Install the server locally
git clone https://github.com/kallows/mcp-bitbucket.git
cd mcp-bitbucket

# Install dependencies using uv (recommended) or pip
uv install
# or
pip install -e .
```

## Tools Available

This MCP server provides the following Bitbucket integration tools:

- `bb_create_repository`: Create a new Bitbucket repository
  - Required: name (repository name)
  - Optional: description, workspace (defaults to kallows), project_key, is_private (default: true), has_issues (default: true)

- `bb_create_branch`: Create a new branch in a repository
  - Required: repo_slug, branch (name for the new branch)
  - Optional: workspace (defaults to kallows), start_point (defaults to main)

- `bb_delete_repository`: Delete a Bitbucket repository
  - Required: repo_slug
  - Optional: workspace (defaults to kallows)

- `bb_read_file`: Read a file from a repository
  - Required: repo_slug, path (file path in repository)
  - Optional: workspace (defaults to kallows), branch (defaults to main/master)

- `bb_write_file`: Create or update a file in a repository
  - Required: repo_slug, path, content
  - Optional: workspace (defaults to kallows), branch (defaults to main), message (commit message)

- `bb_create_issue`: Create an issue in a repository
  - Required: repo_slug, title, content
  - Optional: workspace (defaults to kallows), kind (bug/enhancement/proposal/task), priority (trivial/minor/major/critical/blocker)

- `bb_delete_issue`: Delete an issue from a repository
  - Required: repo_slug, issue_id
  - Optional: workspace (defaults to kallows)

- `bb_search_repositories`: Search Bitbucket repositories using query syntax
  - Required: query (e.g., 'name ~ "test"' or 'project.key = "PROJ"')
  - Optional: workspace (defaults to kallows), page (default: 1), pagelen (default: 10, max: 100)

- `bb_delete_file`: Delete a file from a repository
  - Required: repo_slug, path
  - Optional: workspace (defaults to kallows), branch (defaults to main), message (commit message)

- `bb_create_pull_request`: Create a pull request
  - Required: repo_slug, title, source_branch
  - Optional: workspace (defaults to kallows), destination_branch (defaults to main), description, close_source_branch (default: true)

- `bb_read_pull_request`: Get detailed information about a specific pull request
  - Required: repo_slug, pull_request_id
  - Optional: workspace (defaults to kallows)

- `bb_list_pull_requests`: List pull requests in a repository
  - Required: repo_slug
  - Optional: workspace (defaults to kallows), state (OPEN/MERGED/DECLINED/SUPERSEDED, default: OPEN), page (default: 1), pagelen (default: 10, max: 50)

- `bb_get_pull_request_diff`: Get the complete line-by-line diff for a pull request
  - Required: repo_slug, pull_request_id
  - Optional: workspace (defaults to kallows)
  - Returns: Full unified diff showing exact code changes

- `bb_get_pull_request_diffstat`: Get diff statistics and file change summary for a pull request
  - Required: repo_slug, pull_request_id
  - Optional: workspace (defaults to kallows)
  - Returns: Files changed, lines added/removed, and visual change indicators

## Environment Setup

The server requires Bitbucket credentials to be set up as environment variables:

```bash
export BITBUCKET_USERNAME="your-username"
export BITBUCKET_APP_PASSWORD="your-app-password"
```

### Creating Bitbucket App Password

1. Go to Bitbucket Settings → App passwords
2. Create a new app password with these permissions:
   - Repositories: Read, Write, Admin (for delete operations)
   - Pull requests: Read, Write
   - Issues: Read, Write
   - Account: Read (for workspace operations)

## Claude Desktop Configuration

Add this configuration to your `claude_desktop_config.json`:

### Windows
```json
{
  "mcpServers": {
    "bitbucket-api": {
      "command": "C:\\\\Users\\\\YOURUSERNAME\\\\.local\\\\bin\\\\uv.exe",
      "args": [
        "--directory",
        "D:\\\\mcp\\\\mcp-bitbucket",
        "run",
        "-m",
        "mcp_bitbucket.server"
      ],
      "env": {
        "BITBUCKET_USERNAME": "your-username",
        "BITBUCKET_APP_PASSWORD": "your-app-password"
      }
    }
  }
}
```

### Mac and Linux
```json
{
  "mcpServers": {
    "bitbucket-api": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/mcp-bitbucket",
        "-m", "mcp_bitbucket.server"
      ],
      "env": {
        "BITBUCKET_USERNAME": "your-username",
        "BITBUCKET_APP_PASSWORD": "your-app-password"
      }
    }
  }
}
```

**⚠️ Important:** You must restart Claude Desktop after modifying the configuration file.

## Usage

Once configured, the Bitbucket tools will be available in Claude Desktop. You can:

- Ask Claude to create repositories and branches
- Read and write files in your repositories
- Create and manage issues
- Search for repositories
- Create, read, and analyze pull requests
- Get detailed code diffs and change statistics
- Manage repository files

Example queries:
- "Create a new repository called 'my-project' in my personal workspace"
- "Create a new branch called 'feature-xyz' in the my-project repository"
- "Create a README.md file in my-project with some basic content"
- "Search for repositories that contain 'python' in the name"
- "List all open pull requests in my-project repository"
- "Show me the details of pull request #123 in my-project"
- "Get the diff for pull request #123 to see what code changes were made"
- "Show me the diff statistics for pull request #123 to see which files were changed"

## Pull Request Workflows

The MCP server provides comprehensive pull request functionality:

### Discovery and Analysis
1. **List PRs:** Use `bb_list_pull_requests` to see all pull requests (open, merged, declined)
2. **Get Details:** Use `bb_read_pull_request` to see PR information (title, description, author, branches, etc.)
3. **Quick Overview:** Use `bb_get_pull_request_diffstat` to see which files changed and how many lines
4. **Full Analysis:** Use `bb_get_pull_request_diff` to see exact line-by-line code changes

### Example Workflow
```
1. "List all open pull requests in my-project"
2. "Show me details for pull request #15"
3. "Get the diff statistics for PR #15 to see what files were changed"
4. "Show me the full diff for PR #15 to see the exact code changes"
```

The diff tools provide the same level of detail you'd get from `git diff` or the Bitbucket web interface, making code review and analysis seamless within your AI workflow.

## Workspace Configuration

The tools default to the "kallows" workspace, but you can:
- Specify a different workspace using the `workspace` parameter
- Use `workspace='~'` to work with your personal workspace
- Create repositories in team workspaces if you have permissions

## Running Tests

The project includes unit and integration tests:

```bash
# Run all tests
python -m unittest discover tests

# Run specific test files
python -m unittest tests.test_bb_api
python -m unittest tests.test_bb_integration

# Run with verbose output
python -m unittest discover tests -v
```

## Development

### Adding New Tools

1. Add the tool definition to `handle_list_tools()` in `server.py`
2. Add the implementation to `handle_call_tool()` in `server.py`
3. Add corresponding tests
4. Update this README

### Error Handling

The server includes comprehensive error handling:
- Permission errors with helpful guidance
- Network connectivity issues
- Invalid parameters and validation
- Bitbucket API rate limiting

## Project Structure

```
mcp-bitbucket/
├── README.md
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .python-version
├── src/
│   └── mcp_bitbucket/
│       ├── __init__.py
│       └── server.py
└── tests/
    ├── README.md
    ├── test_bb_api.py
    └── test_bb_integration.py
```

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues and questions:
- Check the Bitbucket API documentation
- Verify your app password permissions
- Review the test files for usage examples
- Create an issue in this repository