import unittest
import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

class BitbucketAPITest(unittest.TestCase):
    """Test class for Bitbucket API operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.server_script = os.getenv("MCP_SERVER_SCRIPT", "../src/mcp_bitbucket/server.py")
        self.workspace = "kallows"
        self.repos_to_cleanup = []
        self.test_repo = None
        
        # Verify required env vars
        self.bitbucket_username = os.getenv("BITBUCKET_USERNAME")
        self.bitbucket_app_password = os.getenv("BITBUCKET_APP_PASSWORD")
        
        if not all([self.bitbucket_username, self.bitbucket_app_password]):
            raise ValueError("BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD must be set")

        # Update setup_client to ensure env vars are passed
        self.env = {
            **dict(os.environ),
            "BITBUCKET_USERNAME": self.bitbucket_username,
            "BITBUCKET_APP_PASSWORD": self.bitbucket_app_password
        }

    def tearDown(self):
        """Clean up test repositories"""
        if self.repos_to_cleanup:
            for repo in self.repos_to_cleanup:
                self.run_async(self.delete_repository(repo))

    def run_async(self, coroutine):
        """Helper to run async code in tests"""
        return asyncio.get_event_loop().run_until_complete(coroutine)

    async def setup_client(self):
        """Initialize MCP client session"""
        try:
            self.exit_stack = AsyncExitStack()
            server_params = StdioServerParameters(
                command="python",
                args=[self.server_script],
                env=self.env
            )
            
            stdio, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
            session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
            await session.initialize()
            
            if not session:
                raise Exception("Failed to create session")
                
            return session
            
        except Exception as e:
            await self.cleanup_client()
            raise Exception(f"Failed to setup client: {str(e)}")

    async def cleanup_client(self):
        """Clean up MCP client session"""
        if hasattr(self, 'exit_stack'):
            await self.exit_stack.aclose()

    async def create_repository(self, name, description="Test repository", has_issues=True):
        """Create a Bitbucket repository"""
        try:
            session = await self.setup_client()
            response = await session.call_tool("bb_create_repository", {
                "workspace": self.workspace,
                "name": name,
                "description": description,
                "is_private": True,
                "has_issues": has_issues
            })
            
            content = response.content[0]
            if content.isError:
                raise Exception(f"Failed to create repository: {content.text}")
            
            # Store current test repository name
            self.test_repo = name
            # Add to cleanup list
            self.repos_to_cleanup.append(name)
                
            return content.text
            
        finally:
            await self.cleanup_client()

    async def delete_repository(self, name):
        """Delete a Bitbucket repository"""
        try:
            session = await self.setup_client()
            await session.call_tool("bb_delete_repository", {
                "workspace": self.workspace,
                "repo_slug": name
            })
        finally:
            await self.cleanup_client()

    async def write_file(self, repo_name, path, content, message="Add file via test"):
        """Write a file to the repository"""
        try:
            session = await self.setup_client()
            response = await session.call_tool("bb_write_file", {
                "workspace": self.workspace,
                "repo_slug": repo_name,
                "path": path,
                "content": content,
                "message": message,
                "branch": "main"
            })
            
            content = response.content[0]
            if content.isError:
                raise Exception(f"Failed to write file: {content.text}")
            return content.text
        finally:
            await self.cleanup_client()

    async def create_issue(self, repo_name, title, content, kind="task", priority="minor"):
        """Create an issue in the repository"""
        try:
            session = await self.setup_client()
            response = await session.call_tool("bb_create_issue", {
                "workspace": self.workspace,
                "repo_slug": repo_name,
                "title": title,
                "content": content,
                "kind": kind,
                "priority": priority
            })
            
            content = response.content[0]
            if content.isError:
                raise Exception(f"Failed to create issue: {content.text}")
            return content.text
        finally:
            await self.cleanup_client()

    def test_create_repository(self):
        """Test basic repository creation"""
        repo_name = "test-repo-basic"
        result = self.run_async(self.create_repository(repo_name))
        self.assertIn("Repository created successfully", result)
        self.assertIn(repo_name, result)

    def test_create_files(self):
        """Test creating multiple files in different directories"""
        # Create test repository if not exists
        if not self.test_repo:
            self.test_create_repository()
        
        # Define test files
        test_files = [
            {
                "path": "docs/readme.md",
                "content": """# Test Repository Documentation
This repository is used for testing Bitbucket API functionality.
## Features Tested
- Issue tracking
- File operations
- Repository management"""
            },
            {
                "path": "src/main.py",
                "content": """def main():
    print("Hello from Bitbucket API test!")
    
if __name__ == "__main__":
    main()"""
            },
            {
                "path": "config/settings.json",
                "content": """{
    "environment": "testing",
    "debug": true,
    "api_version": "1.0.0"
}"""
            },
            {
                "path": "test.txt",
                "content": "Simple test file content for verification."
            }
        ]
        
        # Create each file
        for file_info in test_files:
            result = self.run_async(self.write_file(
                self.test_repo,
                file_info["path"],
                file_info["content"]
            ))
            self.assertIn("updated successfully", result)

    def test_create_issues(self):
        """Test creating multiple issues"""
        # Create test repository if not exists
        if not self.test_repo:
            self.test_create_repository()
        
        # Define test issues
        test_issues = [
            {
                "title": "Implement User Authentication",
                "content": """We need to implement basic user authentication with the following features:
- Login/Logout functionality
- Password reset
- Email verification
- Session management""",
                "kind": "enhancement",
                "priority": "major"
            },
            {
                "title": "Fix Config Loading Bug",
                "content": """The configuration file is not being loaded correctly in production environment.
Steps to reproduce:
1. Deploy to production
2. Check config values
3. Notice environment is still set to 'testing'

Priority is high as this affects production.""",
                "kind": "bug",
                "priority": "critical"
            },
            {
                "title": "Documentation Update Needed",
                "content": """The current documentation needs to be updated with:
- API usage examples
- Configuration options
- Deployment guide
- Troubleshooting section""",
                "kind": "task",
                "priority": "minor"
            }
        ]
        
        # Create each issue
        for issue_info in test_issues:
            result = self.run_async(self.create_issue(
                self.test_repo,
                issue_info["title"],
                issue_info["content"],
                issue_info["kind"],
                issue_info["priority"]
            ))
            self.assertIn("Issue created successfully", result)


if __name__ == '__main__':
    # Set up asyncio loop for test execution
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Create test suite with our test cases in specific order
        suite = unittest.TestSuite()
        test_case = BitbucketAPITest()
        
        # Add tests in desired order
        suite.addTest(BitbucketAPITest('test_create_repository'))
        suite.addTest(BitbucketAPITest('test_create_files'))
        suite.addTest(BitbucketAPITest('test_create_issues'))
        
        # Run the suite
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Exit with appropriate code
        exit_code = 0 if result.wasSuccessful() else 1
        exit(exit_code)
        
    finally:
        loop.close()
        asyncio.set_event_loop(None)
