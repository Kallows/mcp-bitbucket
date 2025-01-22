import sys
import unittest
import os
import base64
import json
import datetime
import tracemalloc
import time
import warnings
from io import StringIO
from unittest.mock import Mock, patch
import requests

class _JsonTestResult(unittest.TextTestResult):
    """Custom test result class that captures detailed test information"""
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_results = {}
        self.current_test_start = None

    def startTest(self, test):
        self.current_test_start = time.time()
        super().startTest(test)

    def addSuccess(self, test):
        super().addSuccess(test)
        self._store_result(test, "PASS")
        
    def addError(self, test, err):
        super().addError(test, err)
        self._store_result(test, "ERROR", err)
        
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._store_result(test, "FAIL", err)

    def _store_result(self, test, status, error=None):
        test_name = test._testMethodName
        test_method = getattr(test, test_name)
        duration = time.time() - self.current_test_start
        
        self.test_results[test_name] = {
            'description': test_method.__doc__ or '',
            'status': status,
            'output': getattr(test, 'output', ''),
            'duration': duration,
            'error': self._exc_info_to_string(error, test) if error else None
        }

class JsonTestRunner(unittest.TextTestRunner):
    """Custom test runner that uses JsonTestResult"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _makeResult(self):
        return _JsonTestResult(self.stream, self.descriptions, self.verbosity)

class TestBitbucketApiTools(unittest.TestCase):
    def setUp(self):
        """Set up environment variables and test data for each test"""
        os.environ["BITBUCKET_USERNAME"] = "test_user"
        os.environ["BITBUCKET_APP_PASSWORD"] = "test_password"
        
        # Sample test data
        self.test_workspace = "kallows"
        self.test_repo_slug = "test-repo"
        self.test_branch = "main"
        self.test_file_path = "test/path/file.txt"
        
        # Create patches for each HTTP method
        self.patches = {
            'get': patch('requests.get'),
            'post': patch('requests.post'),
            'delete': patch('requests.delete'),
            'put': patch('requests.put')
        }
        
        # Start all patches and store the mocks
        self.mocks = {method: patcher.start() for method, patcher in self.patches.items()}
        
        # Output capture setup
        self.output = StringIO()
        self._stdout = patch('sys.stdout', new=self.output)
        self._stdout.start()

    def tearDown(self):
        """Clean up all patches after each test"""
        for patcher in self.patches.values():
            patcher.stop()
        self._stdout.stop()
        self.output = self.output.getvalue()

    def _mock_response(self, status_code=200, json_data=None, content=None):
        """Helper to create mock responses"""
        mock_resp = Mock()
        mock_resp.status_code = status_code
        if json_data is not None:
            mock_resp.json.return_value = json_data
        if content is not None:
            mock_resp.text = content
        return mock_resp

    def test_create_repository(self):
        """Test creating a new Bitbucket repository"""
        mock_data = {
            'links': {'html': {'href': 'https://bitbucket.org/kallows/test-repo'}}
        }
        self.mocks['post'].return_value = self._mock_response(201, mock_data)
        
        response = requests.post(
            f"https://api.bitbucket.org/2.0/repositories/{self.test_workspace}/{self.test_repo_slug}",
            auth=('test_user', 'test_password'),
            json={
                'scm': 'git',
                'name': self.test_repo_slug,
                'is_private': True,
                'description': 'Test repository'
            }
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue('links' in response.json())
        self.mocks['post'].assert_called_once()

    def test_delete_repository(self):
        """Test deleting a Bitbucket repository"""
        self.mocks['delete'].return_value = self._mock_response(204)
        
        response = requests.delete(
            f"https://api.bitbucket.org/2.0/repositories/{self.test_workspace}/{self.test_repo_slug}",
            auth=('test_user', 'test_password')
        )        
        self.assertEqual(response.status_code, 204)
        self.mocks['delete'].assert_called_once()

    def test_read_file(self):
        """Test reading a file from a Bitbucket repository"""
        test_content = "Test file content"
        self.mocks['get'].return_value = self._mock_response(200, content=test_content)
        
        response = requests.get(
            f"https://api.bitbucket.org/2.0/repositories/{self.test_workspace}/{self.test_repo_slug}/src/{self.test_branch}/{self.test_file_path}",
            auth=('test_user', 'test_password')
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, test_content)
        self.mocks['get'].assert_called_once()

    def test_write_file(self):
        """Test writing a file to a Bitbucket repository"""
        self.mocks['post'].return_value = self._mock_response(201)
        
        files = {self.test_file_path: (None, "Test content")}
        data = {'message': 'Update file', 'branch': self.test_branch}
        
        response = requests.post(
            f"https://api.bitbucket.org/2.0/repositories/{self.test_workspace}/{self.test_repo_slug}/src",
            auth=('test_user', 'test_password'),
            files=files,
            data=data
        )
        
        self.assertEqual(response.status_code, 201)
        self.mocks['post'].assert_called_once()

    def test_create_issue(self):
        """Test creating an issue in a Bitbucket repository"""
        mock_data = {
            'id': 1,
            'links': {'html': {'href': 'https://bitbucket.org/kallows/test-repo/issues/1'}}
        }
        self.mocks['post'].return_value = self._mock_response(201, mock_data)
        
        response = requests.post(
            f"https://api.bitbucket.org/2.0/repositories/{self.test_workspace}/{self.test_repo_slug}/issues",
            auth=('test_user', 'test_password'),
            json={
                'title': 'Test Issue',
                'content': {'raw': 'Test description'},
                'kind': 'bug',
                'priority': 'major'
            }
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue('id' in response.json())
        self.mocks['post'].assert_called_once()

    def test_delete_issue(self):
        """Test deleting an issue from a Bitbucket repository"""
        self.mocks['delete'].return_value = self._mock_response(204)
        
        response = requests.delete(
            f"https://api.bitbucket.org/2.0/repositories/{self.test_workspace}/{self.test_repo_slug}/issues/1",
            auth=('test_user', 'test_password')
        )
        
        self.assertEqual(response.status_code, 204)
        self.mocks['delete'].assert_called_once()

    def test_delete_file(self):
        """Test deleting a file from a Bitbucket repository"""
        self.mocks['post'].return_value = self._mock_response(201)
        
        files = {self.test_file_path: (None, "")}
        data = {'message': 'Delete file', 'branch': self.test_branch}
        
        response = requests.post(
            f"https://api.bitbucket.org/2.0/repositories/{self.test_workspace}/{self.test_repo_slug}/src",
            auth=('test_user', 'test_password'),
            files=files,
            data=data
        )
        
        self.assertEqual(response.status_code, 201)
        self.mocks['post'].assert_called_once()

    def test_create_pull_request(self):
        """Test creating a pull request in a Bitbucket repository"""
        mock_data = {
            'id': 1,
            'links': {'html': {'href': 'https://bitbucket.org/kallows/test-repo/pull-requests/1'}}
        }
        self.mocks['post'].return_value = self._mock_response(201, mock_data)
        
        response = requests.post(
            f"https://api.bitbucket.org/2.0/repositories/{self.test_workspace}/{self.test_repo_slug}/pullrequests",
            auth=('test_user', 'test_password'),
            json={
                'title': 'Test PR',
                'description': 'Test description',
                'source': {'branch': {'name': 'feature'}},
                'destination': {'branch': {'name': 'main'}},
                'close_source_branch': True
            }
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue('id' in response.json())
        self.mocks['post'].assert_called_once()

    def test_create_branch(self):
        """Test creating a new branch"""
        mock_data = {'name': 'feature-branch'}
        self.mocks['post'].return_value = self._mock_response(201, mock_data)
        
        response = requests.post(
            f"https://api.bitbucket.org/2.0/repositories/{self.test_workspace}/{self.test_repo_slug}/refs/branches",
            auth=('test_user', 'test_password'),
            json={
                'name': 'feature-branch',
                'target': {'hash': 'main'}
            }
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'feature-branch')
        self.mocks['post'].assert_called_once()

    def test_permission_error_handling(self):
        """Test handling of permission errors"""
        error_response = {
            'error': {
                'detail': {
                    'required': ['repository:admin'],
                    'granted': ['repository:read']
                }
            }
        }
        self.mocks['post'].return_value = self._mock_response(403, error_response)
        
        response = requests.post(
            f"https://api.bitbucket.org/2.0/repositories/{self.test_workspace}/{self.test_repo_slug}",
            auth=('test_user', 'test_password'),
            json={'name': self.test_repo_slug}
        )
        
        self.assertEqual(response.status_code, 403)
        error_data = response.json()
        self.assertTrue('error' in error_data)
        self.assertTrue('detail' in error_data['error'])
        self.mocks['post'].assert_called_once()

def main():
    # Enable tracemalloc for memory stats
    tracemalloc.start()

    # Prepare JSON output structure
    test_results = {
        "summary": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "execution_time": 0,
            "overall_status": "",
            "timestamp": datetime.datetime.now().isoformat()
        },
        "tests": [],
        "warnings": [],
        "memory_stats": []
    }

    # Capture warnings
    with warnings.catch_warnings(record=True) as captured_warnings:
        warnings.simplefilter("always")

        # Run the tests
        start_time = time.time()
        test_suite = unittest.TestLoader().loadTestsFromTestCase(TestBitbucketApiTools)
        result_stream = StringIO()
        runner = JsonTestRunner(stream=result_stream, verbosity=2)
        result = runner.run(test_suite)
        execution_time = time.time() - start_time

        # Process warnings
        test_results["warnings"] = [
            {
                "message": str(warning.message),
                "category": warning.category.__name__,
                "filename": warning.filename,
                "lineno": warning.lineno
            }
            for warning in captured_warnings
        ]

    # Get memory statistics
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")
    
    for stat in top_stats[:10]:
        test_results["memory_stats"].append({
            "size": stat.size,
            "count": stat.count,
            "traceback": str(stat.traceback)
        })

    # Update summary
    test_results["summary"].update({
        "total_tests": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "failed": len(result.failures) + len(result.errors),
        "execution_time": round(execution_time, 3),
        "overall_status": "PASS" if result.wasSuccessful() else "FAIL"
    })

    # Process test results
    test_results["tests"] = [
        {
            "name": name,
            "description": str(details['description']),
            "status": str(details['status']),
            "output": details['output'].getvalue() if hasattr(details['output'], 'getvalue') else str(details['output']),
            "duration": round(details['duration'], 3),
            "error": str(details['error']) if details['error'] else None
        }
        for name, details in result.test_results.items()
    ]

    # Output JSON
    print(json.dumps(test_results, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == '__main__':
    main()
