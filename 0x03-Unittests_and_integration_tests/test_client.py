#!/usr/bin/env python3
"""Unit tests for GithubOrgClient"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value"""
        expected_result = {"login": org_name}
        mock_get_json.return_value = expected_result

        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, expected_result)
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")

    def test_public_repos_url(self):
        """Test _public_repos_url returns correct URL from mocked org"""
        with patch.object(
            GithubOrgClient,
            "org",
            new_callable=PropertyMock,
            return_value={"repos_url": "https://api.github.com/orgs/test-org/repos"}
        ) as mock_org:
            client = GithubOrgClient("test-org")
            result = client._public_repos_url

            self.assertEqual(result, "https://api.github.com/orgs/test-org/repos")
            mock_org.assert_called_once()


if __name__ == "__main__":
    unittest.main()
