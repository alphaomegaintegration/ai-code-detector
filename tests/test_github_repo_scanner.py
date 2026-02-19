import unittest
import os
import shutil
import tempfile
from pathlib import Path
from github_repo_scanner import GitHubRepoScanner

class TestGitHubRepoScanner(unittest.TestCase):
    def setUp(self):
        self.repo_dir = Path(tempfile.mkdtemp())
        self.scanner = GitHubRepoScanner(verbose=False)

    def tearDown(self):
        shutil.rmtree(self.repo_dir)

    def test_find_code_files_skips_symlinks_outside_repo(self):
        # Create a secret file outside the repo
        secret_file = Path(tempfile.mkdtemp()) / "secret.txt"
        with open(secret_file, "w") as f:
            f.write("SECRET_DATA")

        try:
            # Create a symlink inside the repo pointing to the secret file
            symlink_path = self.repo_dir / "exploit.py"
            os.symlink(secret_file, symlink_path)

            # Create a legitimate file
            (self.repo_dir / "valid.py").touch()

            # Find files
            code_files = self.scanner._find_code_files(str(self.repo_dir))

            # Convert to filenames
            filenames = [f.name for f in code_files]

            # Assert valid file is found but symlink is skipped
            self.assertIn("valid.py", filenames)
            self.assertNotIn("exploit.py", filenames)

        finally:
            shutil.rmtree(secret_file.parent)

    def test_find_code_files_allows_symlinks_inside_repo(self):
        # Create a real file inside the repo
        real_file = self.repo_dir / "real.py"
        real_file.touch()

        # Create a symlink to it
        link_file = self.repo_dir / "link.py"
        os.symlink(real_file.name, link_file)

        # Find files
        code_files = self.scanner._find_code_files(str(self.repo_dir))
        filenames = [f.name for f in code_files]

        self.assertIn("real.py", filenames)
        self.assertIn("link.py", filenames)

if __name__ == '__main__':
    unittest.main()
