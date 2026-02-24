import unittest
import tempfile
import shutil
import os
from unittest.mock import MagicMock, patch
from pathlib import Path
from github_repo_scanner import GitHubRepoScanner

class TestScannerE2E(unittest.TestCase):
    def setUp(self):
        self.scanner = GitHubRepoScanner(verbose=False)
        self.test_dir = tempfile.mkdtemp()
        self.repo_dir = Path(self.test_dir) / "test_repo"
        self.repo_dir.mkdir()

        # Create a sample Python file (simple/human-like)
        self.human_file = self.repo_dir / "human.py"
        with open(self.human_file, "w") as f:
            f.write("def add(a, b):\n    return a + b\n")

        # Create a sample AI-like file (verbose/complex)
        self.ai_file = self.repo_dir / "ai.py"
        with open(self.ai_file, "w") as f:
            f.write('"""\nThis module performs addition operations.\nIt ensures that the inputs are valid numbers.\n"""\n')
            f.write('from typing import Union\n\n')
            f.write('def perform_addition_operation(first_number: Union[int, float], second_number: Union[int, float]) -> Union[int, float]:\n')
            f.write('    """\n    Adds two numbers together and returns the result.\n    """\n')
            f.write('    if not isinstance(first_number, (int, float)):\n        raise ValueError("First number must be numeric")\n')
            f.write('    if not isinstance(second_number, (int, float)):\n        raise ValueError("Second number must be numeric")\n')
            f.write('    return first_number + second_number\n')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('github_repo_scanner.GitHubRepoScanner._clone_repository')
    @patch('github_repo_scanner.GitHubRepoScanner._get_default_branch')
    def test_scan_repository_e2e(self, mock_get_branch, mock_clone):
        # Setup mocks
        mock_clone.return_value = str(self.repo_dir)
        mock_get_branch.return_value = "main"

        # Run scan
        analysis = self.scanner.scan_repository("https://github.com/example/test_repo")

        # Verify results
        self.assertEqual(analysis.total_files, 2)
        self.assertEqual(analysis.files_analyzed, 2)

        # Verify file results
        file_results = {r['file_path']: r for r in analysis.file_results}
        self.assertIn("human.py", file_results)
        self.assertIn("ai.py", file_results)

        # Check that AI file has higher probability than human file
        # Note: These values depend on the detector's heuristics,
        # but the relative order should be consistent.
        ai_prob = file_results["ai.py"]["ai_probability"]
        human_prob = file_results["human.py"]["ai_probability"]

        self.assertGreater(ai_prob, human_prob,
                          f"AI file ({ai_prob}%) should have higher probability than human file ({human_prob}%)")

        # Verify language breakdown
        self.assertEqual(analysis.language_breakdown.get("Python"), 2)

if __name__ == '__main__':
    unittest.main()
