import asyncio
import os
import base64
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import requests
from requests.auth import HTTPBasicAuth
import json

# Initialize server
server = Server("bitbucket-api")

# Environment variables for Bitbucket authentication
BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.getenv("BITBUCKET_APP_PASSWORD")

if not all([BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD]):
    raise ValueError(
        "Missing required environment variables: BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD"
    )

def format_permission_error(response_text):
    """Format permission errors into user-friendly messages."""
    try:
        error_data = json.loads(response_text)
        if "error" in error_data:
            required = error_data["error"].get("detail", {}).get("required", [])
            granted = error_data["error"].get("detail", {}).get("granted", [])
            
            message = [
                "Permission Error:",
                f"Required permissions: {', '.join(required)}",
                f"Granted permissions: {', '.join(granted)}",
                "\nTo fix this:",
                "1. Go to Bitbucket Settings > App passwords",
                "2. Create a new app password with the required permissions",
                "3. Update your BITBUCKET_APP_PASSWORD environment variable"
            ]
            return "\n".join(message)
    except:
        pass
    return response_text

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools for Bitbucket integration."""
    return [
        # types.Tool(
        #     name="bb_create_repository",
        #     description="Create a new repository in Bitbucket",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "project_key": {
        #                 "type": "string",
        #                 "description": "The project key where the repository will be created (optional for personal repos)"
        #             },
        #             "name": {
        #                 "type": "string",
        #                 "description": "Repository name"
        #             },
        #             "description": {
        #                 "type": "string",
        #                 "description": "Repository description"
        #             },
        #             "is_private": {
        #                 "type": "boolean",
        #                 "description": "Whether the repository should be private",
        #                 "default": True
        #             },
        #             "workspace": {
        #                 "type": "string",
        #                 "description": "Target workspace (defaults to kallows, can use ~ for personal workspace)",
        #                 "default": "kallows"
        #             }
        #         },
        #         "required": ["name"]
        #     }
        # ),



        types.Tool(
            name="bb_create_repository",
            description="Create a new repository in Bitbucket",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "The project key where the repository will be created (optional for personal repos)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Repository name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Repository description"
                    },
                    "is_private": {
                        "type": "boolean",
                        "description": "Whether the repository should be private",
                        "default": True
                    },
                    "has_issues": {
                        "type": "boolean",
                        "description": "Whether to initialize the repository with issue tracking enabled",
                        "default": True
                    },
                    "workspace": {
                        "type": "string",
                        "description": "Target workspace (defaults to kallows, can use ~ for personal workspace)",
                        "default": "kallows"
                    }
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="bb_create_branch",
            description="Create a new branch in a Bitbucket repository",
            inputSchema={
                "type": "object", 
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Repository workspace (defaults to kallows)",
                        "default": "kallows"
                    },
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository slug/name"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Name for the new branch"
                    },
                    "start_point": {
                        "type": "string", 
                        "description": "Branch/commit to create from (defaults to main)",
                        "default": "main"
                    }
                },
                "required": ["repo_slug", "branch"]
            }
        ),        
        types.Tool(
            name="bb_delete_repository",
            description="Delete a repository from Bitbucket", # TODO: only works with delete repo priv, see if app password can get delete repo privilege
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_slug": {
                        "type": "string",
                        "description": "The repository slug to delete"
                    },
                    "workspace": {
                        "type": "string",
                        "description": "Target workspace (defaults to kallows, can use ~ for personal workspace)",
                        "default": "kallows"
                    }
                },
                "required": ["repo_slug"]
            }
        ),
        types.Tool(
            name="bb_read_file",
            description="Read a file from a Bitbucket repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Repository workspace (defaults to kallows)",
                        "default": "kallows"
                    },
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository slug/name"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to the file in the repository"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name (defaults to main/master)",
                        "default": "main"
                    }
                },
                "required": ["repo_slug", "path"]
            }
        ),
        types.Tool(
            name="bb_write_file",
            description="Write/update a file in a Bitbucket repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Repository workspace (defaults to kallows)",
                        "default": "kallows"
                    },
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository slug/name"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path where to create/update the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    },
                    "message": {
                        "type": "string",
                        "description": "Commit message",
                        "default": "Update file via MCP"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name (defaults to main/master)",
                        "default": "main"
                    }
                },
                "required": ["repo_slug", "path", "content"]
            }
        ),
        types.Tool(
            name="bb_create_issue",
            description="Create an issue in a Bitbucket repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Repository workspace (defaults to kallows)",
                        "default": "kallows"
                    },
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository slug/name"
                    },
                    "title": {
                        "type": "string",
                        "description": "Issue title"
                    },
                    "content": {
                        "type": "string",
                        "description": "Issue content/description"
                    },
                    "kind": {
                        "type": "string",
                        "description": "Issue type (bug, enhancement, proposal, task)",
                        "default": "task"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Issue priority (trivial, minor, major, critical, blocker)",
                        "default": "minor"
                    }
                },
                "required": ["repo_slug", "title", "content"]
            }
        ),
        types.Tool(
            name="bb_delete_issue",
            description="Delete an issue from a Bitbucket repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Repository workspace (defaults to kallows)",
                        "default": "kallows"
                    },
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository slug/name"
                    },
                    "issue_id": {
                        "type": "string",
                        "description": "ID of the issue to delete"
                    }
                },
                "required": ["repo_slug", "issue_id"]
            }
        ),
        types.Tool(
            name="bb_search_repositories",
            description="Search repositories in Bitbucket using Bitbucket's query syntax. Search by name (name ~ \"pattern\"), project key (project.key = \"PROJ\"), language (language = \"python\"), or dates (updated_on >= \"2024-01-19\"). NOTE: All dates must be in ISO 8601 format (YYYY-MM-DD). For searching files within repositories, use Bitbucket's code search in the web interface.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Workspace to search in (defaults to kallows)",
                        "default": "kallows"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'name ~ \"test\"' or 'project.key = \"PROJ\"')"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 1
                    },
                    "pagelen": {
                        "type": "integer",
                        "description": "Number of results per page (max 100)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="bb_delete_file",
            description="Delete a file from a Bitbucket repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Repository workspace (defaults to kallows)",
                        "default": "kallows"
                    },
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository slug/name"
                    },
                    "path": {
                        "type": "string",
                        "description": "Path to the file to delete"
                    },
                    "message": {
                        "type": "string",
                        "description": "Commit message for the deletion",
                        "default": "Delete file via MCP"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name (defaults to main/master)",
                        "default": "main"
                    }
                },
                "required": ["repo_slug", "path"]
            }
        ),
        types.Tool(
            name="bb_create_pull_request",
            description="Create a new pull request in a Bitbucket repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Repository workspace (defaults to kallows)",
                        "default": "kallows"
                    },
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository slug/name"
                    },
                    "title": {
                        "type": "string",
                        "description": "Pull request title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Pull request description"
                    },
                    "source_branch": {
                        "type": "string",
                        "description": "Branch containing your changes"
                    },
                    "destination_branch": {
                        "type": "string",
                        "description": "Branch you want to merge into",
                        "default": "main"
                    },
                    "close_source_branch": {
                        "type": "boolean",
                        "description": "Close source branch after merge",
                        "default": True
                    }
                },
                "required": ["repo_slug", "title", "source_branch"]
            }
        ),
        types.Tool(
            name="bb_read_pull_request", 
            description="Read/get details of a pull request from a Bitbucket repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Repository workspace (defaults to kallows)",
                        "default": "kallows"
                    },
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository slug/name"
                    },
                    "pull_request_id": {
                        "type": "string",
                        "description": "ID of the pull request to read"
                    }
                },
                "required": ["repo_slug", "pull_request_id"]
            }
        ),
        types.Tool(
            name="bb_list_pull_requests",
            description="List pull requests in a Bitbucket repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Repository workspace (defaults to kallows)",
                        "default": "kallows"
                    },
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository slug/name"
                    },
                    "state": {
                        "type": "string",
                        "description": "Pull request state (OPEN, MERGED, DECLINED, SUPERSEDED)",
                        "default": "OPEN"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 1
                    },
                    "pagelen": {
                        "type": "integer",
                        "description": "Number of results per page (max 50)",
                        "default": 10
                    }
                },
                "required": ["repo_slug"]
            }
        ),
        types.Tool(
            name="bb_get_pull_request_diff",
            description="Get the full diff (line-by-line changes) for a pull request",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Repository workspace (defaults to kallows)",
                        "default": "kallows"
                    },
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository slug/name"
                    },
                    "pull_request_id": {
                        "type": "string",
                        "description": "ID of the pull request to get diff for"
                    }
                },
                "required": ["repo_slug", "pull_request_id"]
            }
        ),
        types.Tool(
            name="bb_get_pull_request_diffstat",
            description="Get diff statistics (files changed, lines added/removed) for a pull request",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Repository workspace (defaults to kallows)",
                        "default": "kallows"
                    },
                    "repo_slug": {
                        "type": "string",
                        "description": "Repository slug/name"
                    },
                    "pull_request_id": {
                        "type": "string",
                        "description": "ID of the pull request to get diffstat for"
                    }
                },
                "required": ["repo_slug", "pull_request_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool execution requests for Bitbucket operations."""
    try:
        auth = HTTPBasicAuth(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # if name == "bb_create_repository":
        #     workspace = arguments.get("workspace", "kallows")
        #     if workspace == "~":  # Personal workspace
        #         # First get the user's workspace
        #         user_url = "https://api.bitbucket.org/2.0/user"
        #         user_response = requests.get(user_url, auth=auth, headers=headers)
        #         if user_response.status_code != 200:
        #             return [types.TextContent(
        #                 type="text",
        #                 text=f"Failed to get user info: {user_response.status_code} - {format_permission_error(user_response.text)}",
        #                 isError=True
        #             )]
        #         workspace = user_response.json().get('username')
        #     repo_name = arguments.get("name")
        #     description = arguments.get("description", "")
        #     is_private = arguments.get("is_private", True)
        #     project_key = arguments.get("project_key")
        #     # Create repository payload
        #     payload = {
        #         "scm": "git",
        #         "name": repo_name,
        #         "is_private": is_private,
        #         "description": description
        #     }
        #     # Only add project if specified (required for workspace repos, not for personal)
        #     if project_key:
        #         payload["project"] = {"key": project_key}
        #     url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_name.lower()}"
        #     response = requests.post(url, json=payload, auth=auth, headers=headers)
        #     if response.status_code in (200, 201):
        #         repo_url = response.json().get('links', {}).get('html', {}).get('href', '')
        #         return [types.TextContent(
        #             type="text",
        #             text=f"Repository created successfully in workspace '{workspace}'\nURL: {repo_url}"
        #         )]
        #     else:
        #         error_msg = format_permission_error(response.text)
        #         if workspace == "kallows" and "permission" in error_msg.lower():
        #             error_msg += "\n\nTip: You can try creating the repository in your personal workspace by setting workspace='~'"
        #         return [types.TextContent(
        #             type="text",
        #             text=f"Failed to create repository: {response.status_code}\n{error_msg}",
        #             isError=True
        #         )]


        if name == "bb_create_repository":
            workspace = arguments.get("workspace", "kallows")
            if workspace == "~":  # Personal workspace
                # First get the user's workspace
                user_url = "https://api.bitbucket.org/2.0/user"
                user_response = requests.get(user_url, auth=auth, headers=headers)
                if user_response.status_code != 200:
                    return [types.TextContent(
                        type="text",
                        text=f"Failed to get user info: {user_response.status_code} - {format_permission_error(user_response.text)}",
                        isError=True
                    )]
                workspace = user_response.json().get('username')

            repo_name = arguments.get("name")
            description = arguments.get("description", "")
            is_private = arguments.get("is_private", True)
            project_key = arguments.get("project_key")

            # Create repository payload
            payload = {
                "scm": "git",
                "name": repo_name,
                "is_private": is_private,
                "description": description,
                "has_issues": arguments.get("has_issues", True)  # Added this line
            }

            # Only add project if specified (required for workspace repos, not for personal)
            if project_key:
                payload["project"] = {"key": project_key}

            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_name.lower()}"
            response = requests.post(url, json=payload, auth=auth, headers=headers)

            if response.status_code in (200, 201):
                repo_url = response.json().get('links', {}).get('html', {}).get('href', '')
                return [types.TextContent(
                    type="text",
                    text=f"Repository created successfully in workspace '{workspace}'\nURL: {repo_url}"
                )]
            else:
                error_msg = format_permission_error(response.text)
                if workspace == "kallows" and "permission" in error_msg.lower():
                    error_msg += "\n\nTip: You can try creating the repository in your personal workspace by setting workspace='~'"
                
                return [types.TextContent(
                    type="text",
                    text=f"Failed to create repository: {response.status_code}\n{error_msg}",
                    isError=True
                )]

        elif name == "bb_search_repositories":
            workspace = arguments.get("workspace", "kallows")
            query = arguments.get("query")
            page = arguments.get("page", 1)
            pagelen = min(arguments.get("pagelen", 10), 100)  # Cap at 100

            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}"
            
            params = {
                'q': query,
                'page': page,
                'pagelen': pagelen
            }
            
            response = requests.get(url, params=params, auth=auth, headers=headers)

            if response.status_code == 200:
                repos = response.json()
                
                # Format the results nicely
                results = []
                for repo in repos.get('values', []):
                    repo_info = {
                        'name': repo.get('name'),
                        'full_name': repo.get('full_name'),
                        'description': repo.get('description', 'No description'),
                        'created_on': repo.get('created_on'),
                        'updated_on': repo.get('updated_on'),
                        'size': repo.get('size', 0),
                        'language': repo.get('language', 'Unknown'),
                        'has_wiki': repo.get('has_wiki', False),
                        'is_private': repo.get('is_private', True),
                        'url': repo.get('links', {}).get('html', {}).get('href', '')
                    }
                    results.append(repo_info)
                
                # Add pagination info
                pagination = {
                    'page': page,
                    'pagelen': pagelen,
                    'size': repos.get('size', 0),
                    'next': 'next' in repos.get('links', {}),
                    'previous': 'previous' in repos.get('links', {})
                }
                
                return [types.TextContent(
                    type="text",
                    text=f"Found {len(results)} repositories:\n\n" + 
                         '\n\n'.join([
                             f"• {r['name']}\n"
                             f"  Description: {r['description']}\n"
                             f"  Language: {r['language']}\n"
                             f"  URL: {r['url']}"
                             for r in results
                         ]) +
                         f"\n\nPage {pagination['page']} | "
                         f"Total results: {pagination['size']} | "
                         f"{'More results available' if pagination['next'] else 'End of results'}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to search repositories: {response.status_code}\n{format_permission_error(response.text)}",
                    isError=True
                )]

        elif name == "bb_create_branch":
            workspace = arguments.get("workspace", "kallows")
            repo_slug = arguments.get("repo_slug")
            branch_name = arguments.get("branch")
            start_point = arguments.get("start_point", "main")

            # First get the hash of the start point
            ref_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/refs/branches/{start_point}"
            ref_response = requests.get(ref_url, auth=auth, headers=headers)
            
            if ref_response.status_code != 200:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to get start point reference: {ref_response.status_code}\n{format_permission_error(ref_response.text)}",
                    isError=True
                )]
            
            start_hash = ref_response.json()['target']['hash']
            
            # Create the new branch
            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/refs/branches"
            payload = {
                "name": branch_name,
                "target": {
                    "hash": start_hash
                }
            }
            
            response = requests.post(url, json=payload, auth=auth, headers=headers)

            if response.status_code in (200, 201):
                branch_url = response.json().get('links', {}).get('html', {}).get('href', '')
                return [types.TextContent(
                    type="text",
                    text=f"Branch '{branch_name}' created successfully\nURL: {branch_url}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to create branch: {response.status_code}\n{format_permission_error(response.text)}",
                    isError=True
                )]

        elif name == "bb_delete_repository":
            workspace = arguments.get("workspace", "kallows")
            if workspace == "~":
                user_url = "https://api.bitbucket.org/2.0/user"
                user_response = requests.get(user_url, auth=auth, headers=headers)
                if user_response.status_code != 200:
                    return [types.TextContent(
                        type="text",
                        text=f"Failed to get user info: {user_response.status_code} - {format_permission_error(user_response.text)}",
                        isError=True
                    )]
                workspace = user_response.json().get('username')

            repo_slug = arguments.get("repo_slug")
            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}"
            response = requests.delete(url, auth=auth, headers=headers)

            if response.status_code == 204:
                return [types.TextContent(
                    type="text",
                    text=f"Repository {repo_slug} deleted successfully from workspace '{workspace}'"
                )]
            else:
                error_msg = format_permission_error(response.text)
                if workspace == "kallows" and "permission" in error_msg.lower():
                    error_msg += "\n\nTip: You can try deleting the repository from your personal workspace by setting workspace='~'"
                
                return [types.TextContent(
                    type="text",
                    text=f"Failed to delete repository: {response.status_code}\n{error_msg}",
                    isError=True
                )]

        elif name == "bb_read_file":
            workspace = arguments.get("workspace", "kallows")
            repo_slug = arguments.get("repo_slug")
            file_path = arguments.get("path")
            branch = arguments.get("branch", "main")

            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/src/{branch}/{file_path}"
            response = requests.get(url, auth=auth)

            if response.status_code == 200:
                return [types.TextContent(
                    type="text",
                    text=response.text
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to read file: {response.status_code}\n{format_permission_error(response.text)}",
                    isError=True
                )]

        elif name == "bb_write_file":
            workspace = arguments.get("workspace", "kallows")
            repo_slug = arguments.get("repo_slug")
            file_path = arguments.get("path")
            content = arguments.get("content")
            message = arguments.get("message", "Update file via MCP")
            branch = arguments.get("branch", "main")

            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/src"
            
            # Prepare form data for file upload
            files = {
                file_path: (None, content)
            }
            data = {
                'message': message,
                'branch': branch
            }

            response = requests.post(url, auth=auth, files=files, data=data)

            if response.status_code in (200, 201):
                return [types.TextContent(
                    type="text",
                    text=f"File {file_path} updated successfully"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to write file: {response.status_code}\n{format_permission_error(response.text)}",
                    isError=True
                )]

        elif name == "bb_create_issue":
            workspace = arguments.get("workspace", "kallows")
            repo_slug = arguments.get("repo_slug")
            title = arguments.get("title")
            content = arguments.get("content")
            kind = arguments.get("kind", "task")
            priority = arguments.get("priority", "minor")

            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/issues"
            
            payload = {
                "title": title,
                "content": {"raw": content},
                "kind": kind,
                "priority": priority
            }

            response = requests.post(url, json=payload, auth=auth, headers=headers)

            if response.status_code in (200, 201):
                issue_id = response.json().get('id')
                issue_url = response.json().get('links', {}).get('html', {}).get('href', '')
                return [types.TextContent(
                    type="text",
                    text=f"Issue created successfully\nID: {issue_id}\nURL: {issue_url}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to create issue: {response.status_code}\n{format_permission_error(response.text)}",
                    isError=True
                )]

        elif name == "bb_delete_issue":
            workspace = arguments.get("workspace", "kallows")
            repo_slug = arguments.get("repo_slug")
            issue_id = arguments.get("issue_id")

            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/issues/{issue_id}"
            response = requests.delete(url, auth=auth, headers=headers)

            if response.status_code == 204:
                return [types.TextContent(
                    type="text",
                    text=f"Issue {issue_id} deleted successfully"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to delete issue: {response.status_code}\n{format_permission_error(response.text)}",
                    isError=True
                )]

        elif name == "bb_delete_file":
            workspace = arguments.get("workspace", "kallows")
            repo_slug = arguments.get("repo_slug")
            file_path = arguments.get("path")
            message = arguments.get("message", "Delete file via MCP")
            branch = arguments.get("branch", "main")

            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/src"
            
            # In Bitbucket, file deletion is done by posting an empty file
            files = {
                file_path: (None, "")
            }
            data = {
                'message': message,
                'branch': branch
            }

            response = requests.post(url, auth=auth, files=files, data=data)

            if response.status_code in (200, 201):
                return [types.TextContent(
                    type="text",
                    text=f"File {file_path} deleted successfully"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to delete file: {response.status_code}\n{format_permission_error(response.text)}",
                    isError=True
                )]

        elif name == "bb_create_pull_request":
            workspace = arguments.get("workspace", "kallows")
            repo_slug = arguments.get("repo_slug")
            title = arguments.get("title")
            description = arguments.get("description", "")
            source_branch = arguments.get("source_branch")
            destination_branch = arguments.get("destination_branch", "main")
            close_source_branch = arguments.get("close_source_branch", True)

            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests"
            
            payload = {
                "title": title,
                "description": description,
                "source": {
                    "branch": {
                        "name": source_branch
                    }
                },
                "destination": {
                    "branch": {
                        "name": destination_branch
                    }
                },
                "close_source_branch": close_source_branch
            }

            response = requests.post(url, json=payload, auth=auth, headers=headers)

            if response.status_code in (200, 201):
                pr_id = response.json().get('id')
                pr_url = response.json().get('links', {}).get('html', {}).get('href', '')
                return [types.TextContent(
                    type="text",
                    text=f"Pull request created successfully\nID: {pr_id}\nURL: {pr_url}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to create pull request: {response.status_code}\n{format_permission_error(response.text)}",
                    isError=True
                )]

        elif name == "bb_read_pull_request":
            workspace = arguments.get("workspace", "kallows")
            repo_slug = arguments.get("repo_slug")
            pull_request_id = arguments.get("pull_request_id")

            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}"
            response = requests.get(url, auth=auth, headers=headers)

            if response.status_code == 200:
                pr_data = response.json()
                
                # Format the pull request information nicely
                pr_info = {
                    'id': pr_data.get('id'),
                    'title': pr_data.get('title'),
                    'description': pr_data.get('description', 'No description'),
                    'state': pr_data.get('state'),
                    'created_on': pr_data.get('created_on'),
                    'updated_on': pr_data.get('updated_on'),
                    'author': pr_data.get('author', {}).get('display_name', 'Unknown'),
                    'source_branch': pr_data.get('source', {}).get('branch', {}).get('name', 'Unknown'),
                    'destination_branch': pr_data.get('destination', {}).get('branch', {}).get('name', 'Unknown'),
                    'merge_commit': pr_data.get('merge_commit', {}).get('hash', 'N/A') if pr_data.get('merge_commit') else 'N/A',
                    'comment_count': pr_data.get('comment_count', 0),
                    'task_count': pr_data.get('task_count', 0),
                    'close_source_branch': pr_data.get('close_source_branch', False),
                    'url': pr_data.get('links', {}).get('html', {}).get('href', '')
                }
                
                formatted_output = f"""Pull Request #{pr_info['id']}: {pr_info['title']}

Description: {pr_info['description']}
State: {pr_info['state']}
Author: {pr_info['author']}
Created: {pr_info['created_on']}
Updated: {pr_info['updated_on']}

Branches:
  Source: {pr_info['source_branch']}
  Destination: {pr_info['destination_branch']}
  Close source after merge: {pr_info['close_source_branch']}

Statistics:
  Comments: {pr_info['comment_count']}
  Tasks: {pr_info['task_count']}
  Merge commit: {pr_info['merge_commit']}

URL: {pr_info['url']}"""

                return [types.TextContent(
                    type="text",
                    text=formatted_output
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to read pull request: {response.status_code}\n{format_permission_error(response.text)}",
                    isError=True
                )]

        elif name == "bb_list_pull_requests":
            workspace = arguments.get("workspace", "kallows")
            repo_slug = arguments.get("repo_slug")
            state = arguments.get("state", "OPEN")
            page = arguments.get("page", 1)
            pagelen = min(arguments.get("pagelen", 10), 50)  # Cap at 50

            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests"
            
            params = {
                'state': state,
                'page': page,
                'pagelen': pagelen
            }
            
            response = requests.get(url, params=params, auth=auth, headers=headers)

            if response.status_code == 200:
                pr_list = response.json()
                
                # Format the results nicely
                results = []
                for pr in pr_list.get('values', []):
                    pr_info = {
                        'id': pr.get('id'),
                        'title': pr.get('title'),
                        'state': pr.get('state'),
                        'author': pr.get('author', {}).get('display_name', 'Unknown'),
                        'created_on': pr.get('created_on'),
                        'source_branch': pr.get('source', {}).get('branch', {}).get('name', 'Unknown'),
                        'destination_branch': pr.get('destination', {}).get('branch', {}).get('name', 'Unknown'),
                        'comment_count': pr.get('comment_count', 0),
                        'url': pr.get('links', {}).get('html', {}).get('href', '')
                    }
                    results.append(pr_info)
                
                # Add pagination info
                pagination = {
                    'page': page,
                    'pagelen': pagelen,
                    'size': pr_list.get('size', 0),
                    'next': 'next' in pr_list.get('links', {}),
                    'previous': 'previous' in pr_list.get('links', {})
                }
                
                formatted_output = f"Pull Requests ({state}) - Page {pagination['page']}\n"
                formatted_output += f"Total results: {pagination['size']}\n\n"
                
                if results:
                    for pr in results:
                        formatted_output += f"#{pr['id']}: {pr['title']}\n"
                        formatted_output += f"  State: {pr['state']}\n"
                        formatted_output += f"  Author: {pr['author']}\n"
                        formatted_output += f"  Branches: {pr['source_branch']} → {pr['destination_branch']}\n"
                        formatted_output += f"  Comments: {pr['comment_count']}\n"
                        formatted_output += f"  URL: {pr['url']}\n\n"
                else:
                    formatted_output += "No pull requests found.\n"
                
                if pagination['next']:
                    formatted_output += f"More results available on page {pagination['page'] + 1}"
                elif pagination['page'] > 1:
                    formatted_output += "End of results"
                
                return [types.TextContent(
                    type="text",
                    text=formatted_output
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to list pull requests: {response.status_code}\n{format_permission_error(response.text)}",
                    isError=True
                )]

        elif name == "bb_get_pull_request_diff":
            workspace = arguments.get("workspace", "kallows")
            repo_slug = arguments.get("repo_slug")
            pull_request_id = arguments.get("pull_request_id")

            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/diff"
            
            # For diff, we need to handle plain text response, not JSON
            response = requests.get(url, auth=auth)

            if response.status_code == 200:
                diff_content = response.text
                
                # Add a header with some context
                header = f"Diff for Pull Request #{pull_request_id}\n"
                header += f"Repository: {workspace}/{repo_slug}\n"
                header += "=" * 60 + "\n\n"
                
                return [types.TextContent(
                    type="text",
                    text=header + diff_content
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to get pull request diff: {response.status_code}\n{format_permission_error(response.text)}",
                    isError=True
                )]

        elif name == "bb_get_pull_request_diffstat":
            workspace = arguments.get("workspace", "kallows")
            repo_slug = arguments.get("repo_slug")
            pull_request_id = arguments.get("pull_request_id")

            url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pull_request_id}/diffstat"
            response = requests.get(url, auth=auth, headers=headers)

            if response.status_code == 200:
                diffstat_data = response.json()
                
                # Format the diffstat information nicely
                header = f"Diff Statistics for Pull Request #{pull_request_id}\n"
                header += f"Repository: {workspace}/{repo_slug}\n"
                header += "=" * 60 + "\n\n"
                
                total_additions = 0
                total_deletions = 0
                files_changed = 0
                
                file_stats = []
                
                for item in diffstat_data.get('values', []):
                    lines_added = item.get('lines_added', 0)
                    lines_removed = item.get('lines_removed', 0)
                    status = item.get('status', 'unknown')
                    
                    # Get file paths
                    old_path = item.get('old', {}).get('path') if item.get('old') else None
                    new_path = item.get('new', {}).get('path') if item.get('new') else None
                    
                    # Determine the file path to display
                    if status == 'added':
                        file_path = new_path or 'unknown'
                        file_display = f"{file_path} (added)"
                    elif status == 'removed':
                        file_path = old_path or 'unknown'
                        file_display = f"{file_path} (deleted)"
                    elif old_path != new_path and old_path and new_path:
                        file_display = f"{old_path} → {new_path} (renamed)"
                    else:
                        file_path = new_path or old_path or 'unknown'
                        file_display = file_path
                    
                    total_additions += lines_added
                    total_deletions += lines_removed
                    files_changed += 1
                    
                    # Create visual representation of changes
                    if lines_added > 0 or lines_removed > 0:
                        change_indicator = ""
                        if lines_added > 0:
                            change_indicator += "+" * min(lines_added, 20)
                        if lines_removed > 0:
                            change_indicator += "-" * min(lines_removed, 20)
                        
                        file_stats.append(f"{file_display}")
                        file_stats.append(f"  +{lines_added} -{lines_removed} {change_indicator}")
                    else:
                        file_stats.append(f"{file_display} (no line changes)")
                
                # Summary
                summary = f"Files changed: {files_changed}\n"
                summary += f"Insertions: +{total_additions}\n"
                summary += f"Deletions: -{total_deletions}\n"
                summary += f"Net change: {total_additions - total_deletions:+d}\n\n"
                
                # File details
                files_section = "Files:\n" + "\n".join(file_stats) if file_stats else "No files changed"
                
                formatted_output = header + summary + files_section
                
                return [types.TextContent(
                    type="text",
                    text=formatted_output
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to get pull request diffstat: {response.status_code}\n{format_permission_error(response.text)}",
                    isError=True
                )]

        raise ValueError(f"Unknown tool: {name}")
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Operation failed: {str(e)}",
            isError=True
        )]

async def main():
    """Run the Bitbucket MCP server using stdin/stdout streams."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="bitbucket-api",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())