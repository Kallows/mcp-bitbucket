# MCP Bitbucket Tests

This directory contains the test suite for the MCP Bitbucket server. The tests are organized to ensure comprehensive coverage of both the API interface and MCP tool integration.

## Test Files Overview

### test_bb_api.py
- Unit tests for the Bitbucket API interface
- Uses mocks to test API functionality without making actual Bitbucket calls
- Tests individual API functions and their error handling
- Verifies proper parameter validation and transformation
- Ensures correct handling of API responses
- Tests edge cases and error conditions
- Validates authentication handling

### test_bb_integration.py
- Integration tests for all MCP tools provided by the server
- Tests actual interactions with Bitbucket
- Verifies each tool's functionality:
  - Repository creation, deletion, and search
  - Branch operations
  - File operations (read, write, delete)
  - Issue management
  - Pull request creation
- Tests proper environment variable handling
- Verifies correct MCP protocol implementation
- Ensures proper error handling and status codes
- Tests rate limiting and retry logic

## Running the Tests

To run the full test suite:

```bash
python -m unittest discover tests
```

To run a specific test file:

```bash
python -m unittest tests/test_bb_api.py
```

## Environment Setup

The integration tests require Bitbucket credentials. Set these environment variables before running the tests:

```bash
export BITBUCKET_USERNAME="your-username"
export BITBUCKET_APP_PASSWORD="your-app-password"
```

## Test Coverage

TODO: Add coverage reporting and maintain a minimum coverage threshold