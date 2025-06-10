# MCP Bitbucket Python 🦊

A Python implementation of an MCP server for Bitbucket integration. MCP (Model Context Protocol) enables secure, local tool access for AI applications. The server runs locally on the same machine as your AI application.

<a href="https://glama.ai/mcp/servers/@Kallows/mcp-bitbucket">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@Kallows/mcp-bitbucket/badge" alt="Bitbucket Python MCP server" />
</a>

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
- Create pull requests
- Manage repository files

Example queries:
- "Create a new repository called 'my-project' in my personal workspace"
- "Create a new branch called 'feature-xyz' in the my-project repository"
- "Create a README.md file in my-project with some basic content"
- "Search for repositories that contain 'python' in the name"

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