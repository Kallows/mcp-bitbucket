# MCP Bitbucket Python 🦊

A Python implementation of an MCP server for Bitbucket integration. MCP (Model Context Protocol) enables secure, local tool access for AI applications. The server runs locally on the same machine as your AI application.

## Installation

```bash
# Install the server locally
git clone https://github.com/kallows/mcp-bitbucket.git
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

## Project Structure

```
mcp-bitbucket/
├── README.md
├── pyproject.toml
├── src/
│   └── bitbucket_api/
│       ├── __init__.py
│       └── server.py
└── tests/
    ├── __init__.py
    ├── test_bb_api.py
    └── test_bb_integration.py
```