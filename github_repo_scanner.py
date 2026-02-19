#!/usr/bin/env python3
# pylint: disable=line-too-long, too-many-locals, too-many-instance-attributes
"""
GitHub Repository Scanner - AI Code Detection for Entire Repositories

This module provides comprehensive AI code detection across entire GitHub repositories.
It clones repositories, analyzes all code files, and generates detailed reports.
"""

import os
import re
import sys
import shutil
import argparse
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

# Import the existing detector and report generator
from ai_code_detector import AICodeDetector, DetectionResult
from report_generator import ReportGenerator


@dataclass
class RepositoryAnalysis:
    """Comprehensive analysis results for a repository"""
    repository_url: str
    branch: str
    analysis_timestamp: str
    total_files: int
    files_analyzed: int
    average_ai_probability: float
    distribution: Dict[str, int]
    high_risk_files: List[Dict[str, Any]]
    language_breakdown: Dict[str, int]
    top_ai_files: List[Dict[str, Any]]
    file_results: List[Dict[str, Any]]
    summary: Dict[str, Any]


class GitHubRepoScanner:
    """Scanner for analyzing GitHub repositories for AI-generated code"""

    # Supported file extensions by language
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

    # Directories to skip during analysis
    SKIP_DIRECTORIES = {
        'node_modules', 'vendor', 'venv', '.venv', 'env', '.env',
        '__pycache__', '.git', '.svn', '.hg', 'dist', 'build',
        'target', 'bin', 'obj', '.idea', '.vscode', 'coverage',
        '.pytest_cache', '.mypy_cache', 'eggs', '.eggs',
    }

    def __init__(self, verbose: bool = True):
        """Initialize the scanner with the AI code detector"""
        self.detector = AICodeDetector()
        self.verbose = verbose
        self.temp_dir = None

    def _log(self, message: str, prefix: str = "INFO"):
        """Print log messages if verbose mode is enabled"""
        if self.verbose:
            print(f"[{prefix}] {message}")

    def _validate_github_url(self, url: str) -> Tuple[bool, str]:
        """Validate and normalize a GitHub repository URL"""
        # Patterns for valid GitHub URLs
        patterns = [
            r'^https?://github\.com/[\w.-]+/[\w.-]+(?:\.git)?$',
            r'^git@github\.com:[\w.-]+/[\w.-]+(?:\.git)?$',
            r'^gh:[\w.-]+/[\w.-]+$',  # Short form
        ]

        # Normalize the URL
        normalized_url = url.strip().rstrip('/')
        if not normalized_url.endswith('.git') and 'github.com' in normalized_url:
            normalized_url = normalized_url + '.git'

        for pattern in patterns:
            if re.match(pattern, normalized_url.replace('.git', ''), re.IGNORECASE):
                return True, normalized_url

        return False, normalized_url

    def _clone_repository(self, url: str, branch: Optional[str] = None) -> str:
        """Clone a GitHub repository to a temporary directory"""
        self.temp_dir = tempfile.mkdtemp(prefix='ai_scanner_')
        self._log(f"Cloning repository to {self.temp_dir}")

        clone_cmd = ['git', 'clone', '--depth', '1']

        if branch:
            clone_cmd.extend(['--branch', branch])

        clone_cmd.extend([url, self.temp_dir])

        try:
            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                if 'not found' in error_msg.lower():
                    raise ValueError(f"Repository not found: {url}")
                if 'could not find remote branch' in error_msg.lower():
                    raise ValueError(f"Branch not found: {branch}")
                raise RuntimeError(f"Git clone failed: {error_msg}")

            self._log("Repository cloned successfully")
            return self.temp_dir

        except subprocess.TimeoutExpired as exc:
            self._cleanup()
            raise RuntimeError("Clone operation timed out (>5 minutes)") from exc

    def _get_default_branch(self, repo_path: str) -> str:
        """Get the default branch name from the cloned repository"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=repo_path,
                check=False
            )
            return result.stdout.strip() if result.returncode == 0 else 'main'
        except Exception: # pylint: disable=broad-exception-caught
            return 'main'

    def _get_extension_to_language(self) -> Dict[str, str]:
        """Create a mapping from file extension to language"""
        ext_to_lang = {}
        for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
            for ext in extensions:
                ext_to_lang[ext] = lang
        return ext_to_lang

    def _find_code_files(self, repo_path: str, extensions: Optional[List[str]] = None) -> List[Path]:
        """Find all code files in the repository"""
        if extensions is None:
            extensions = []
            for exts in self.LANGUAGE_EXTENSIONS.values():
                extensions.extend(exts)

        code_files = []
        repo = Path(repo_path).resolve()

        for file_path in repo.rglob('*'):
            # Skip directories in SKIP_DIRECTORIES
            if any(skip_dir in file_path.parts for skip_dir in self.SKIP_DIRECTORIES):
                continue

            # Security check: Ensure file resolves to within the repository
            # This prevents symlink traversal attacks
            try:
                # Check if the resolved path is relative to the repo root
                file_path.resolve().relative_to(repo)
            except (ValueError, RuntimeError):
                self._log(f"Skipping file outside repository boundary: {file_path}", "WARN")
                continue

            # Only include files with matching extensions
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                # Skip very large files (> 1MB)
                if file_path.stat().st_size <= 1024 * 1024:
                    code_files.append(file_path)

        return code_files

    def _analyze_files(self, files: List[Path], repo_path: str) -> List[DetectionResult]:
        """Analyze a list of files and return results"""
        results = []
        total = len(files)

        for idx, file_path in enumerate(files, 1):
            # Show progress
            if self.verbose and idx % 10 == 0:
                progress = (idx / total) * 100
                self._log(f"Progress: {idx}/{total} files ({progress:.1f}%)", "PROGRESS")

            try:
                result = self.detector.analyze_file(str(file_path))
                # Convert to relative path for cleaner output
                rel_path = str(file_path.relative_to(repo_path))
                result.file_path = rel_path
                results.append(result)
            except Exception as e: # pylint: disable=broad-exception-caught
                self._log(f"Error analyzing {file_path}: {e}", "ERROR")

        return results

    def _calculate_distribution(self, results: List[DetectionResult]) -> Dict[str, int]:
        """Calculate the distribution of AI probabilities"""
        distribution = {
            'likely_human (0-35%)': 0,
            'mixed (35-55%)': 0,
            'possibly_ai (55-75%)': 0,
            'likely_ai (75-100%)': 0
        }

        for result in results:
            prob = result.ai_probability
            if prob < 35:
                distribution['likely_human (0-35%)'] += 1
            elif prob < 55:
                distribution['mixed (35-55%)'] += 1
            elif prob < 75:
                distribution['possibly_ai (55-75%)'] += 1
            else:
                distribution['likely_ai (75-100%)'] += 1

        return distribution

    def _find_high_risk_files(self, results: List[DetectionResult]) -> List[Dict[str, Any]]:
        """Find files with high AI probability and high confidence"""
        high_risk = []

        for result in results:
            if result.ai_probability > 70 and result.confidence == 'HIGH':
                high_risk.append({
                    'file': result.file_path,
                    'ai_probability': result.ai_probability,
                    'confidence': result.confidence,
                    'verdict': result.verdict
                })

        # Sort by AI probability descending
        high_risk.sort(key=lambda x: x['ai_probability'], reverse=True)
        return high_risk

    def _calculate_language_breakdown(self, files: List[Path]) -> Dict[str, int]:
        """Calculate the number of files per language"""
        ext_to_lang = self._get_extension_to_language()
        breakdown = defaultdict(int)

        for file_path in files:
            ext = file_path.suffix.lower()
            lang = ext_to_lang.get(ext, 'Other')
            breakdown[lang] += 1

        return dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))

    def _get_top_ai_files(self, results: List[DetectionResult], n: int = 10) -> List[Dict[str, Any]]:
        """Get the top N files most likely to be AI-generated"""
        sorted_results = sorted(results, key=lambda x: x.ai_probability, reverse=True)

        top_files = []
        for result in sorted_results[:n]:
            top_files.append({
                'file': result.file_path,
                'ai_probability': result.ai_probability,
                'human_probability': result.human_probability,
                'confidence': result.confidence,
                'verdict': result.verdict
            })

        return top_files

    def _cleanup(self):
        """Clean up temporary directories"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            self._log(f"Cleaning up temporary directory: {self.temp_dir}")
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e: # pylint: disable=broad-exception-caught
                self._log(f"Warning: Could not clean up temp dir: {e}", "WARN")
            finally:
                self.temp_dir = None

    def scan_repository(self, url: str, branch: Optional[str] = None,
                       extensions: Optional[List[str]] = None) -> RepositoryAnalysis:
        """
        Scan a GitHub repository for AI-generated code

        Args:
            url: GitHub repository URL
            branch: Branch to analyze (defaults to main/master)
            extensions: List of file extensions to analyze (defaults to all supported)

        Returns:
            RepositoryAnalysis object with comprehensive results
        """
        self._log(f"Starting scan of repository: {url}")

        # Validate URL
        is_valid, normalized_url = self._validate_github_url(url)
        if not is_valid:
            raise ValueError(f"Invalid GitHub repository URL: {url}")

        try:
            # Clone repository
            repo_path = self._clone_repository(normalized_url, branch)

            # Get actual branch name
            actual_branch = self._get_default_branch(repo_path)
            self._log(f"Analyzing branch: {actual_branch}")

            # Find code files
            self._log("Scanning for code files...")
            code_files = self._find_code_files(repo_path, extensions)
            self._log(f"Found {len(code_files)} code files to analyze")

            if not code_files:
                self._log("No code files found in repository", "WARN")
                return RepositoryAnalysis(
                    repository_url=url,
                    branch=actual_branch,
                    analysis_timestamp=datetime.now().isoformat(),
                    total_files=0,
                    files_analyzed=0,
                    average_ai_probability=0.0,
                    distribution={},
                    high_risk_files=[],
                    language_breakdown={},
                    top_ai_files=[],
                    file_results=[],
                    summary={'message': 'No code files found'}
                )

            # Analyze files
            self._log("Analyzing files for AI patterns...")
            results = self._analyze_files(code_files, repo_path)

            # Calculate statistics
            valid_results = [r for r in results if r.confidence != 'ERROR']
            if valid_results:
                avg_probability = sum(r.ai_probability for r in valid_results) / len(valid_results)
            else:
                avg_probability = 0

            # Calculate distribution
            distribution = self._calculate_distribution(valid_results)

            # Find high-risk files
            high_risk_files = self._find_high_risk_files(valid_results)

            # Language breakdown
            language_breakdown = self._calculate_language_breakdown(code_files)

            # Top AI files
            top_ai_files = self._get_top_ai_files(valid_results, 10)

            # Convert results to dicts
            file_results = [asdict(r) for r in results]

            # Generate summary
            summary = {
                'total_files_in_repo': len(code_files),
                'files_successfully_analyzed': len(valid_results),
                'files_with_errors': len(results) - len(valid_results),
                'average_ai_probability': round(avg_probability, 2),
                'median_ai_probability': round(
                    sorted([r.ai_probability for r in valid_results])[len(valid_results)//2]
                    if valid_results else 0, 2
                ),
                'high_risk_count': len(high_risk_files),
                'verdict_summary': {
                    'likely_ai': sum(1 for r in valid_results if 'LIKELY AI' in r.verdict),
                    'possibly_ai': sum(1 for r in valid_results if 'POSSIBLY AI' in r.verdict),
                    'mixed': sum(1 for r in valid_results if 'MIXED' in r.verdict),
                    'likely_human': sum(1 for r in valid_results if 'HUMAN' in r.verdict),
                    'inconclusive': sum(1 for r in valid_results if 'INCONCLUSIVE' in r.verdict)
                }
            }

            analysis = RepositoryAnalysis(
                repository_url=url,
                branch=actual_branch,
                analysis_timestamp=datetime.now().isoformat(),
                total_files=len(code_files),
                files_analyzed=len(valid_results),
                average_ai_probability=round(avg_probability, 2),
                distribution=distribution,
                high_risk_files=high_risk_files,
                language_breakdown=language_breakdown,
                top_ai_files=top_ai_files,
                file_results=file_results,
                summary=summary
            )

            self._log(f"Analysis complete! Analyzed {len(valid_results)} files")
            return analysis

        finally:
            self._cleanup()

    def scan_local_directory(self, path: str, extensions: Optional[List[str]] = None) -> RepositoryAnalysis:
        """
        Scan a local directory for AI-generated code

        Args:
            path: Path to local directory
            extensions: List of file extensions to analyze (defaults to all supported)

        Returns:
            RepositoryAnalysis object with comprehensive results
        """
        path = Path(path).resolve()

        if not path.exists():
            raise ValueError(f"Directory does not exist: {path}")

        self._log(f"Scanning local directory: {path}")

        # Find code files
        code_files = self._find_code_files(str(path), extensions)
        self._log(f"Found {len(code_files)} code files to analyze")

        if not code_files:
            return RepositoryAnalysis(
                repository_url=str(path),
                branch='local',
                analysis_timestamp=datetime.now().isoformat(),
                total_files=0,
                files_analyzed=0,
                average_ai_probability=0.0,
                distribution={},
                high_risk_files=[],
                language_breakdown={},
                top_ai_files=[],
                file_results=[],
                summary={'message': 'No code files found'}
            )

        # Analyze files
        results = self._analyze_files(code_files, str(path))

        # Calculate statistics (same as scan_repository)
        valid_results = [r for r in results if r.confidence != 'ERROR']
        if valid_results:
            avg_probability = sum(r.ai_probability for r in valid_results) / len(valid_results)
        else:
            avg_probability = 0

        distribution = self._calculate_distribution(valid_results)
        high_risk_files = self._find_high_risk_files(valid_results)
        language_breakdown = self._calculate_language_breakdown(code_files)
        top_ai_files = self._get_top_ai_files(valid_results, 10)
        file_results = [asdict(r) for r in results]

        summary = {
            'total_files_in_repo': len(code_files),
            'files_successfully_analyzed': len(valid_results),
            'files_with_errors': len(results) - len(valid_results),
            'average_ai_probability': round(avg_probability, 2),
            'median_ai_probability': round(
                sorted([r.ai_probability for r in valid_results])[len(valid_results)//2]
                if valid_results else 0, 2
            ),
            'high_risk_count': len(high_risk_files),
            'verdict_summary': {
                'likely_ai': sum(1 for r in valid_results if 'LIKELY AI' in r.verdict),
                'possibly_ai': sum(1 for r in valid_results if 'POSSIBLY AI' in r.verdict),
                'mixed': sum(1 for r in valid_results if 'MIXED' in r.verdict),
                'likely_human': sum(1 for r in valid_results if 'HUMAN' in r.verdict),
                'inconclusive': sum(1 for r in valid_results if 'INCONCLUSIVE' in r.verdict)
            }
        }

        return RepositoryAnalysis(
            repository_url=str(path),
            branch='local',
            analysis_timestamp=datetime.now().isoformat(),
            total_files=len(code_files),
            files_analyzed=len(valid_results),
            average_ai_probability=round(avg_probability, 2),
            distribution=distribution,
            high_risk_files=high_risk_files,
            language_breakdown=language_breakdown,
            top_ai_files=top_ai_files,
            file_results=file_results,
            summary=summary
        )


def main():
    """Main entry point for the GitHub repository scanner"""
    parser = argparse.ArgumentParser(
        description='GitHub Repository Scanner - Detect AI-generated code in repositories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Scan a public GitHub repository:
    python github_repo_scanner.py https://github.com/user/repo

  Scan a specific branch:
    python github_repo_scanner.py https://github.com/user/repo --branch develop

  Generate reports to a specific directory:
    python github_repo_scanner.py https://github.com/user/repo -o ./reports

  Only analyze Python files:
    python github_repo_scanner.py https://github.com/user/repo --extensions .py

  Scan a local directory:
    python github_repo_scanner.py --local ./my-project

  Generate only JSON report:
    python github_repo_scanner.py https://github.com/user/repo --json-only

  Generate only HTML report:
    python github_repo_scanner.py https://github.com/user/repo --html-only
        """
    )

    parser.add_argument('url', nargs='?', help='GitHub repository URL to scan')
    parser.add_argument('-b', '--branch', help='Branch to analyze (default: main/master)')
    parser.add_argument('-o', '--output-dir', default='.',
                       help='Output directory for reports (default: current directory)')
    parser.add_argument('--local', metavar='PATH', help='Scan a local directory instead of GitHub')
    parser.add_argument('--extensions', help='Comma-separated list of file extensions to analyze (e.g., .py,.js)')
    parser.add_argument('--json-only', action='store_true', help='Generate only JSON report')
    parser.add_argument('--html-only', action='store_true', help='Generate only HTML report')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress progress output')

    args = parser.parse_args()

    # Validate arguments
    if not args.url and not args.local:
        parser.error("Please provide either a GitHub URL or use --local for local directory scanning")

    # Parse extensions
    extensions = None
    if args.extensions:
        extensions = [ext.strip() if ext.startswith('.') else f'.{ext.strip()}'
                     for ext in args.extensions.split(',')]

    # Create scanner
    scanner = GitHubRepoScanner(verbose=not args.quiet)

    try:
        # Perform analysis
        if args.local:
            analysis = scanner.scan_local_directory(args.local, extensions)
            base_name = Path(args.local).name
        else:
            analysis = scanner.scan_repository(args.url, args.branch, extensions)
            base_name = args.url.split('/')[-1].replace('.git', '')

        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamp for filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Print summary
        ReportGenerator.print_summary(analysis)

        # Generate reports
        if not args.html_only:
            json_path = output_dir / f"{base_name}_analysis_{timestamp}.json"
            ReportGenerator.generate_json_report(analysis, str(json_path))

        if not args.json_only:
            html_path = output_dir / f"{base_name}_analysis_{timestamp}.html"
            ReportGenerator.generate_repo_html_report(analysis, str(html_path))

        print("\n✅ Analysis complete!")

    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(130)
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
