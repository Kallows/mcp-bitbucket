# MCP Bitbucket Tests

This directory contains the test suite for the MCP Bitbucket server. The tests are organized to ensure comprehensive coverage of both the API interface and MCP tool integration.

## Test Files Overview

### test_bb_api.py
Unit tests for the Bitbucket API interface:
- Uses mocks to test API functionality without making actual Bitbucket calls
- Tests individual API functions and their error handling
- Verifies proper parameter validation and transformation
- Ensures correct handling of API responses
- Tests edge cases and error conditions
- Validates authentication handling
- Tests permission error formatting
- Comprehensive pull request functionality testing:
  - Reading PR details with structured data validation
  - Listing PRs with pagination and state filtering
  - Getting complete diffs with proper content parsing
  - Analyzing diff statistics with file status handling

### test_bb_integration.py
Integration tests for all MCP tools provided by the server:
- Tests actual interactions with Bitbucket API
- Verifies each tool's functionality:
  - Repository creation, deletion, and search
  - Branch operations and management
  - File operations (read, write, delete)
  - Issue creation and management
  - Pull request creation and comprehensive analysis workflow
  - Pull request diff retrieval and statistics
- Tests proper environment variable handling
- Verifies correct MCP protocol implementation
- Ensures proper error handling and status codes
- Tests workspace operations (personal vs team)

## Test Organization

### Unit Tests
Focus on isolated functionality:
- API client behavior
- Response parsing
- Error handling
- Parameter validation
- Mock external dependencies

### Integration Tests
Test complete workflows:
- End-to-end tool operations
- Real Bitbucket API interactions
- Cross-tool dependencies
- Authentication flows

## Running the Tests

### All Tests
```bash
python -m unittest discover tests
```

### Specific Test Files
```bash
# API unit tests
python -m unittest tests.test_bb_api

# Integration tests
python -m unittest tests.test_bb_integration

# Verbose output
python -m unittest discover tests -v
```

### Individual Test Methods
```bash
# Test specific functionality
python -m unittest tests.test_bb_api.TestBitbucketApiTools.test_create_repository

# Test new pull request functionality
python -m unittest tests.test_bb_api.TestBitbucketApiTools.test_read_pull_request
python -m unittest tests.test_bb_api.TestBitbucketApiTools.test_list_pull_requests
python -m unittest tests.test_bb_api.TestBitbucketApiTools.test_get_pull_request_diff
python -m unittest tests.test_bb_api.TestBitbucketApiTools.test_get_pull_request_diffstat
```

## Environment Setup

### Required Environment Variables

For integration tests, set up your Bitbucket credentials:

```bash
export BITBUCKET_USERNAME="your-username"
export BITBUCKET_APP_PASSWORD="your-app-password"
```

### Bitbucket App Password Setup

Your app password needs these permissions:
- **Repositories**: Read, Write, Admin (for repository operations)
- **Pull requests**: Read, Write (for PR operations)  
- **Issues**: Read, Write (for issue operations)
- **Account**: Read (for workspace operations)

### Test Data Management

- Integration tests may create temporary repositories/branches
- Tests include cleanup procedures
- Use descriptive names with timestamps to avoid conflicts
- Tests are designed to be idempotent

## Test Coverage Areas

The test suite covers:

### Repository Operations
- Creating repositories with various configurations
- Deleting repositories with permission handling
- Searching repositories with different query patterns
- Workspace-specific operations

### File Management
- Reading files from different branches
- Writing/updating files with commit messages
- Deleting files with proper cleanup
- Handling binary and text files

### Branch Operations
- Creating branches from different starting points
- Working with main/master branch variations
- Branch naming and validation

### Issue Management
- Creating issues with different priorities and types
- Deleting issues with proper permissions
- Issue content formatting

### Pull Requests
- Creating PRs between branches
- Reading individual pull request details
- Listing pull requests with filtering (state, pagination)
- Getting complete line-by-line diffs for PRs
- Analyzing diff statistics and file changes
- Setting up source and destination branches
- PR descriptions and metadata

### Error Handling
- Network connectivity issues
- Authentication failures
- Permission denied scenarios
- Invalid parameters
- Rate limiting responses

## Mock Testing Strategy

Unit tests use comprehensive mocking:

```python
# Example mock setup
@patch('requests.get')
def test_read_file_success(self, mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "file content"
    # Test implementation
```

### Mock Scenarios Tested
- Successful API responses
- Various HTTP error codes (400, 401, 403, 404, 500)
- Network timeouts and connectivity issues
- Malformed JSON responses
- Rate limiting responses

### Pull Request Testing Patterns

The new pull request tests include comprehensive scenarios:

#### test_read_pull_request
- Tests detailed PR information retrieval
- Validates structured response parsing (author, branches, timestamps)
- Verifies proper handling of PR metadata (comments, tasks, state)

#### test_list_pull_requests
- Tests pagination and filtering by state
- Validates multiple PR response handling
- Checks proper list formatting and navigation

#### test_get_pull_request_diff
- Tests complete unified diff retrieval
- Validates diff content parsing and formatting
- Ensures proper handling of file changes and line modifications

#### test_get_pull_request_diffstat
- Tests file change statistics
- Validates handling of different file statuses (added, modified, removed)
- Checks proper calculation of lines added/removed
- Tests edge cases for renamed files and binary changes

## Integration Test Patterns

Integration tests follow consistent patterns:

1. **Setup**: Create test resources if needed
2. **Execute**: Run the tool with test parameters
3. **Verify**: Check expected outcomes
4. **Cleanup**: Remove any created resources

## Debugging Tests

### Verbose Output
```bash
python -m unittest tests.test_bb_integration -v
```

### Debug Specific Test
```bash
python -c "
import unittest
from tests.test_bb_integration import TestBitbucketIntegration
suite = unittest.TestLoader().loadTestsFromName('test_create_repository', TestBitbucketIntegration)
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
"
```

### Environment Debug
Verify your environment setup:
```bash
python -c "
import os
print('Username:', os.getenv('BITBUCKET_USERNAME'))
print('App Password Set:', bool(os.getenv('BITBUCKET_APP_PASSWORD')))
"
```

## Test Best Practices

### When Adding New Tests
1. Create both unit and integration tests for new tools
2. Test both success and failure scenarios
3. Include edge cases and boundary conditions
4. Verify error messages are user-friendly
5. Test with different workspace configurations

### Test Data Guidelines
- Use descriptive, unique names for test resources
- Include timestamps to avoid naming conflicts
- Clean up test data in tearDown methods
- Use realistic but safe test data

### Performance Considerations
- Integration tests make real API calls and may be slower
- Use appropriate timeouts for network operations
- Consider rate limiting in test design
- Separate fast unit tests from slower integration tests

## Continuous Integration

The test suite is designed for CI/CD integration:
- All tests run independently
- No dependencies on external test data
- Configurable via environment variables
- Standard exit codes for success/failure
- Compatible with common CI platforms

## Coverage Reporting

Generate test coverage reports:

```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run -m unittest discover tests

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
```

Target coverage areas:
- All tool implementations
- Error handling paths
- Authentication flows
- Parameter validation