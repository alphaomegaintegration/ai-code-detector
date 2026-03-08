import timeit

setup_code = """
from typing import Dict
class GitHubRepoScanner:
    LANGUAGE_EXTENSIONS = {
        'Python': ['.py'],
        'JavaScript': ['.js', '.jsx', '.mjs'],
        'TypeScript': ['.ts', '.tsx'],
        'Java': ['.java'],
        'C++': ['.cpp', '.cxx', '.cc', '.hpp', '.h'],
        'C': ['.c'],
        'C#': ['.cs'],
        'Go': ['.go'],
        'Ruby': ['.rb'],
        'PHP': ['.php'],
        'Rust': ['.rs'],
        'Swift': ['.swift'],
        'Kotlin': ['.kt', '.kts'],
        'Scala': ['.scala'],
        'Shell': ['.sh', '.bash'],
        'HTML': ['.html', '.htm'],
        'CSS': ['.css', '.scss', '.sass', '.less'],
        'SQL': ['.sql'],
        'YAML': ['.yml', '.yaml'],
        'Markdown': ['.md'],
    }

    EXTENSION_TO_LANGUAGE = {
        ext: lang
        for lang, extensions in LANGUAGE_EXTENSIONS.items()
        for ext in extensions
    }

    def _get_extension_to_language(self) -> Dict[str, str]:
        return self.EXTENSION_TO_LANGUAGE

scanner = GitHubRepoScanner()
"""

test_code = """
scanner._get_extension_to_language()
"""

print("Optimized:", timeit.timeit(stmt=test_code, setup=setup_code, number=100000))
