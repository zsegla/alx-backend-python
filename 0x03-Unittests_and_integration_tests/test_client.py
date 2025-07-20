#!/usr/bin/env python3
"""Unit tests for GithubOrgClient module"""

import unittest
from unittest.mock import patch, PropertyMock
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test case for GithubOrgClient"""

    @patch('client.get_json', return_value={"login": "test-org"})
    def test_org(self, mock_get_json):
        """Test that GithubOrgClient.org returns correct data"""
        client = GithubOrgClient("test-org")
        result = client.org
        self.assertEqual(result, {"login": "test-org"})
        mock_get_json.assert_called_once_with(
            "https://api.github.com/orgs/test-org"
        )


if __name__ == "__main__":
    unittest.main()
