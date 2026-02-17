#!/usr/bin/env python3
# pylint: disable=too-many-lines
"""
GitHub Repository Scanner - AI Code Detection for Entire Repositories

This module provides comprehensive AI code detection across entire GitHub repositories.
It clones repositories, analyzes all code files, and generates detailed reports.
"""

import os
import re
import sys
import json
import shutil
import argparse
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

# Import the existing detector
from ai_code_detector import AICodeDetector, DetectionResult


# pylint: disable=too-many-instance-attributes
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

    def _validate_branch_name(self, branch: str) -> bool:
        """Validate that the branch name is safe"""
        if not branch:
            return True

        # Branch names cannot start with - to prevent argument injection
        if branch.startswith('-'):
            return False

        # Allow only alphanumeric characters, forward slashes, hyphens, underscores, and dots
        # This is restrictive but safe for most use cases
        if not re.match(r'^[a-zA-Z0-9/_.-]+$', branch):
            return False

        # Git branch names cannot contain '..'
        if '..' in branch:
            return False

        return True

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
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                if 'not found' in error_msg.lower():
                    raise ValueError(f"Repository not found: {url}")
                elif 'could not find remote branch' in error_msg.lower():
                    raise ValueError(f"Branch not found: {branch}")
                else:
                    raise RuntimeError(f"Git clone failed: {error_msg}")

            self._log(f"Repository cloned successfully")
            return self.temp_dir

        except subprocess.TimeoutExpired:
            self._cleanup()
            raise RuntimeError("Clone operation timed out (>5 minutes)")

    def _get_default_branch(self, repo_path: str) -> str:
        """Get the default branch name from the cloned repository"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=repo_path
            )
            return result.stdout.strip() if result.returncode == 0 else 'main'
        except:
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
        repo = Path(repo_path)

        for file_path in repo.rglob('*'):
            # Skip directories in SKIP_DIRECTORIES
            if any(skip_dir in file_path.parts for skip_dir in self.SKIP_DIRECTORIES):
                continue

            # Only include files with matching extensions
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                # Skip very large files (> 1MB)
                if file_path.stat().st_size <= 1024 * 1024:
                    code_files.append(file_path)

        return code_files

    # pylint: disable=too-many-locals
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
            except Exception as e:
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
            except Exception as e:
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

        # Validate branch name
        if branch and not self._validate_branch_name(branch):
            raise ValueError(f"Invalid branch name: {branch}")

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
            avg_probability = sum(r.ai_probability for r in valid_results) / len(valid_results) if valid_results else 0

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
        avg_probability = sum(r.ai_probability for r in valid_results) / len(valid_results) if valid_results else 0

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


class ReportGenerator:
    """Generate reports from repository analysis results"""

    @staticmethod
    def generate_json_report(analysis: RepositoryAnalysis, output_path: str):
        """Generate a JSON report"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(analysis), f, indent=2)
        print(f"JSON report saved to: {output_path}")

    @staticmethod
    # pylint: disable=duplicate-code, too-many-locals, too-many-statements
    def generate_html_report(analysis: RepositoryAnalysis, output_path: str):
        """Generate a professional HTML report with visualizations"""

        # Calculate percentages for distribution chart
        total = analysis.files_analyzed if analysis.files_analyzed > 0 else 1
        dist_percentages = {k: (v / total) * 100 for k, v in analysis.distribution.items()}

        # Color coding for verdict
        def get_verdict_color(verdict):
            if 'LIKELY AI' in verdict:
                return '#dc3545'  # Red
            if 'POSSIBLY AI' in verdict:
                return '#fd7e14'  # Orange
            if 'MIXED' in verdict:
                return '#ffc107'  # Yellow
            if 'HUMAN' in verdict:
                return '#28a745'  # Green
            return '#6c757d'  # Gray

        def get_probability_color(prob):
            if prob >= 75:
                return '#dc3545'  # Red
            if prob >= 55:
                return '#fd7e14'  # Orange
            if prob >= 35:
                return '#ffc107'  # Yellow
            return '#28a745'  # Green

        # Generate top files HTML
        top_files_html = ""
        for i, file in enumerate(analysis.top_ai_files, 1):
            color = get_probability_color(file['ai_probability'])
            top_files_html += f"""
            <tr>
                <td>{i}</td>
                <td class="file-path">{file['file']}</td>
                <td style="color: {color}; font-weight: bold;">{file['ai_probability']}%</td>
                <td>{file['confidence']}</td>
                <td style="color: {color};">{file['verdict']}</td>
            </tr>"""

        # Generate high risk files HTML
        high_risk_html = ""
        if analysis.high_risk_files:
            for file in analysis.high_risk_files[:20]:  # Limit to 20
                high_risk_html += f"""
                <tr class="high-risk">
                    <td class="file-path">{file['file']}</td>
                    <td style="color: #dc3545; font-weight: bold;">{file['ai_probability']}%</td>
                    <td>{file['confidence']}</td>
                    <td style="color: #dc3545;">{file['verdict']}</td>
                </tr>"""
        else:
            high_risk_html = '<tr><td colspan="4" style="text-align: center; color: #28a745;">No high-risk files detected!</td></tr>'

        # Generate language breakdown HTML
        lang_html = ""
        max_files = max(analysis.language_breakdown.values()) if analysis.language_breakdown else 1
        for lang, count in analysis.language_breakdown.items():
            width = (count / max_files) * 100
            lang_html += f"""
            <div class="lang-bar">
                <span class="lang-name">{lang}</span>
                <div class="bar-container">
                    <div class="bar" style="width: {width}%"></div>
                </div>
                <span class="lang-count">{count} files</span>
            </div>"""

        # Generate all files table
        all_files_html = ""
        sorted_results = sorted(analysis.file_results, key=lambda x: x['ai_probability'], reverse=True)
        for result in sorted_results:
            color = get_probability_color(result['ai_probability'])
            all_files_html += f"""
            <tr>
                <td class="file-path">{result['file_path']}</td>
                <td style="color: {color}; font-weight: bold;">{result['ai_probability']}%</td>
                <td>{result['human_probability']}%</td>
                <td>{result['confidence']}</td>
                <td style="color: {color};">{result['verdict']}</td>
            </tr>"""

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Code Detection Report - {analysis.repository_url.split('/')[-1].replace('.git', '')}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            background: linear-gradient(135deg, #0f3460 0%, #533483 100%);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}

        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            color: #fff;
        }}

        .meta {{
            color: #a0a0a0;
            font-size: 0.95em;
        }}

        .meta span {{
            margin-right: 20px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}

        .stat-card h3 {{
            color: #a0a0a0;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}

        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #fff;
        }}

        .stat-value.green {{ color: #28a745; }}
        .stat-value.yellow {{ color: #ffc107; }}
        .stat-value.orange {{ color: #fd7e14; }}
        .stat-value.red {{ color: #dc3545; }}

        section {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.1);
        }}

        section h2 {{
            color: #fff;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.1);
        }}

        .distribution-chart {{
            display: flex;
            height: 40px;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 15px;
        }}

        .dist-segment {{
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.85em;
            color: #fff;
            transition: flex 0.3s;
        }}

        .dist-segment.green {{ background: #28a745; }}
        .dist-segment.yellow {{ background: #ffc107; color: #333; }}
        .dist-segment.orange {{ background: #fd7e14; }}
        .dist-segment.red {{ background: #dc3545; }}

        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 15px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
        }}

        .lang-bar {{
            display: flex;
            align-items: center;
            margin-bottom: 12px;
        }}

        .lang-name {{
            width: 120px;
            font-weight: 500;
        }}

        .bar-container {{
            flex: 1;
            height: 24px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin: 0 15px;
        }}

        .bar {{
            height: 100%;
            background: linear-gradient(90deg, #533483, #0f3460);
            border-radius: 4px;
            transition: width 0.5s;
        }}

        .lang-count {{
            width: 80px;
            text-align: right;
            color: #a0a0a0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}

        th {{
            background: rgba(0,0,0,0.2);
            color: #fff;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
        }}

        tr:hover {{
            background: rgba(255,255,255,0.05);
        }}

        tr.high-risk {{
            background: rgba(220, 53, 69, 0.1);
        }}

        .file-path {{
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.9em;
            word-break: break-all;
        }}

        .verdict-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}

        .verdict-item {{
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            background: rgba(0,0,0,0.2);
        }}

        .verdict-count {{
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .verdict-label {{
            font-size: 0.85em;
            color: #a0a0a0;
        }}

        .table-container {{
            max-height: 500px;
            overflow-y: auto;
            border-radius: 8px;
        }}

        .table-container::-webkit-scrollbar {{
            width: 8px;
        }}

        .table-container::-webkit-scrollbar-track {{
            background: rgba(255,255,255,0.1);
        }}

        .table-container::-webkit-scrollbar-thumb {{
            background: rgba(255,255,255,0.3);
            border-radius: 4px;
        }}

        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            margin-top: 30px;
        }}

        @media (max-width: 768px) {{
            h1 {{ font-size: 1.8em; }}
            .stats-grid {{ grid-template-columns: 1fr 1fr; }}
            .stat-value {{ font-size: 2em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 AI Code Detection Report</h1>
            <div class="meta">
                <span>📁 Repository: <strong>{analysis.repository_url}</strong></span>
                <span>🌿 Branch: <strong>{analysis.branch}</strong></span>
                <span>📅 Analyzed: <strong>{analysis.analysis_timestamp[:19].replace('T', ' ')}</strong></span>
            </div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Files Analyzed</h3>
                <div class="stat-value">{analysis.files_analyzed}</div>
            </div>
            <div class="stat-card">
                <h3>Average AI Probability</h3>
                <div class="stat-value {'red' if analysis.average_ai_probability >= 60 else 'orange' if analysis.average_ai_probability >= 40 else 'green'}">{analysis.average_ai_probability}%</div>
            </div>
            <div class="stat-card">
                <h3>High Risk Files</h3>
                <div class="stat-value {'red' if len(analysis.high_risk_files) > 5 else 'orange' if len(analysis.high_risk_files) > 0 else 'green'}">{len(analysis.high_risk_files)}</div>
            </div>
            <div class="stat-card">
                <h3>Languages Detected</h3>
                <div class="stat-value">{len(analysis.language_breakdown)}</div>
            </div>
        </div>

        <section>
            <h2>📊 AI Probability Distribution</h2>
            <div class="distribution-chart">
                <div class="dist-segment green" style="flex: {dist_percentages.get('likely_human (0-35%)', 0)}">{analysis.distribution.get('likely_human (0-35%)', 0)}</div>
                <div class="dist-segment yellow" style="flex: {dist_percentages.get('mixed (35-55%)', 0)}">{analysis.distribution.get('mixed (35-55%)', 0)}</div>
                <div class="dist-segment orange" style="flex: {dist_percentages.get('possibly_ai (55-75%)', 0)}">{analysis.distribution.get('possibly_ai (55-75%)', 0)}</div>
                <div class="dist-segment red" style="flex: {dist_percentages.get('likely_ai (75-100%)', 0)}">{analysis.distribution.get('likely_ai (75-100%)', 0)}</div>
            </div>
            <div class="legend">
                <div class="legend-item"><div class="legend-color" style="background:#28a745"></div> Likely Human (0-35%): {analysis.distribution.get('likely_human (0-35%)', 0)} files</div>
                <div class="legend-item"><div class="legend-color" style="background:#ffc107"></div> Mixed (35-55%): {analysis.distribution.get('mixed (35-55%)', 0)} files</div>
                <div class="legend-item"><div class="legend-color" style="background:#fd7e14"></div> Possibly AI (55-75%): {analysis.distribution.get('possibly_ai (55-75%)', 0)} files</div>
                <div class="legend-item"><div class="legend-color" style="background:#dc3545"></div> Likely AI (75-100%): {analysis.distribution.get('likely_ai (75-100%)', 0)} files</div>
            </div>
        </section>

        <section>
            <h2>📈 Verdict Summary</h2>
            <div class="verdict-summary">
                <div class="verdict-item">
                    <div class="verdict-count" style="color:#dc3545">{analysis.summary.get('verdict_summary', {}).get('likely_ai', 0)}</div>
                    <div class="verdict-label">Likely AI-Generated</div>
                </div>
                <div class="verdict-item">
                    <div class="verdict-count" style="color:#fd7e14">{analysis.summary.get('verdict_summary', {}).get('possibly_ai', 0)}</div>
                    <div class="verdict-label">Possibly AI-Assisted</div>
                </div>
                <div class="verdict-item">
                    <div class="verdict-count" style="color:#ffc107">{analysis.summary.get('verdict_summary', {}).get('mixed', 0)}</div>
                    <div class="verdict-label">Mixed Indicators</div>
                </div>
                <div class="verdict-item">
                    <div class="verdict-count" style="color:#28a745">{analysis.summary.get('verdict_summary', {}).get('likely_human', 0)}</div>
                    <div class="verdict-label">Likely Human-Written</div>
                </div>
                <div class="verdict-item">
                    <div class="verdict-count" style="color:#6c757d">{analysis.summary.get('verdict_summary', {}).get('inconclusive', 0)}</div>
                    <div class="verdict-label">Inconclusive</div>
                </div>
            </div>
        </section>

        <section>
            <h2>💻 Language Breakdown</h2>
            {lang_html if lang_html else '<p>No files detected</p>'}
        </section>

        <section>
            <h2>🔝 Top 10 Most Likely AI-Generated Files</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>File Path</th>
                            <th>AI Probability</th>
                            <th>Confidence</th>
                            <th>Verdict</th>
                        </tr>
                    </thead>
                    <tbody>
                        {top_files_html if top_files_html else '<tr><td colspan="5" style="text-align:center">No files analyzed</td></tr>'}
                    </tbody>
                </table>
            </div>
        </section>

        <section>
            <h2>⚠️ High Risk Files (>70% AI probability, HIGH confidence)</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>File Path</th>
                            <th>AI Probability</th>
                            <th>Confidence</th>
                            <th>Verdict</th>
                        </tr>
                    </thead>
                    <tbody>
                        {high_risk_html}
                    </tbody>
                </table>
            </div>
        </section>

        <section>
            <h2>📋 All Files Analysis</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>File Path</th>
                            <th>AI Probability</th>
                            <th>Human Probability</th>
                            <th>Confidence</th>
                            <th>Verdict</th>
                        </tr>
                    </thead>
                    <tbody>
                        {all_files_html if all_files_html else '<tr><td colspan="5" style="text-align:center">No files analyzed</td></tr>'}
                    </tbody>
                </table>
            </div>
        </section>

        <footer>
            <p>Generated by AI Code Detector | Repository Scanner v1.0</p>
            <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML report saved to: {output_path}")

    @staticmethod
    def print_summary(analysis: RepositoryAnalysis):
        """Print a summary of the analysis to console"""
        print("\n" + "=" * 80)
        print("🔍 AI CODE DETECTION - REPOSITORY ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"\n📁 Repository: {analysis.repository_url}")
        print(f"🌿 Branch: {analysis.branch}")
        print(f"📅 Analyzed: {analysis.analysis_timestamp[:19].replace('T', ' ')}")

        print(f"\n{'─' * 40}")
        print("📊 STATISTICS")
        print(f"{'─' * 40}")
        print(f"  Total Files Analyzed: {analysis.files_analyzed}")
        print(f"  Average AI Probability: {analysis.average_ai_probability}%")
        print(f"  High Risk Files: {len(analysis.high_risk_files)}")

        print(f"\n{'─' * 40}")
        print("📈 DISTRIBUTION")
        print(f"{'─' * 40}")
        for category, count in analysis.distribution.items():
            print(f"  {category}: {count} files")

        print(f"\n{'─' * 40}")
        print("💻 LANGUAGE BREAKDOWN")
        print(f"{'─' * 40}")
        for lang, count in list(analysis.language_breakdown.items())[:10]:
            print(f"  {lang}: {count} files")

        if analysis.high_risk_files:
            print(f"\n{'─' * 40}")
            print("⚠️  HIGH RISK FILES")
            print(f"{'─' * 40}")
            for file in analysis.high_risk_files[:10]:
                print(f"  • {file['file']} ({file['ai_probability']}%)")

        print(f"\n{'─' * 40}")
        print("🔝 TOP 5 AI-LIKELY FILES")
        print(f"{'─' * 40}")
        for i, file in enumerate(analysis.top_ai_files[:5], 1):
            print(f"  {i}. {file['file']} - {file['ai_probability']}% AI")

        print("\n" + "=" * 80 + "\n")


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
            ReportGenerator.generate_html_report(analysis, str(html_path))

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
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
