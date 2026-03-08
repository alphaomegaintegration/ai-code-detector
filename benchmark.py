import timeit

setup_code = """
from github_repo_scanner import GitHubRepoScanner
scanner = GitHubRepoScanner()
files = [] # doesn't matter much for the method itself
"""

test_code = """
scanner._get_extension_to_language()
"""

print("Baseline:", timeit.timeit(stmt=test_code, setup=setup_code, number=100000))
