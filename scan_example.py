#!/usr/bin/env python3
"""
Sample Usage Script - GitHub Repository Scanner

This script demonstrates how to use the GitHub Repository Scanner
programmatically to analyze repositories for AI-generated code.
"""

from pathlib import Path

# Import the scanner
<<<<<<< HEAD
from github_repo_scanner import GitHubRepoScanner
from report_generator import ReportGenerator
=======
from github_repo_scanner import GitHubRepoScanner, ReportGenerator
>>>>>>> remotes/origin/sentinel-fix-git-branch-injection-14962938762884618886


def example_scan_public_repository():
    """
    Example 1: Scan a public GitHub repository

    This demonstrates scanning a well-known public repository.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Scanning a Public GitHub Repository")
    print("=" * 60 + "\n")

    # Initialize the scanner
    scanner = GitHubRepoScanner(verbose=True)

    # Scan a public repository (httpie - a popular HTTP client)
    # Using a smaller repo for faster demonstration
    repo_url = "https://github.com/httpie/cli"

    print(f"Target: {repo_url}")
    print("-" * 60)

    try:
        # Perform the scan - analyzing only Python files for speed
        analysis = scanner.scan_repository(
            url=repo_url,
            branch=None,  # Use default branch
            extensions=['.py']  # Only Python files for this demo
        )

        # Print summary to console
        ReportGenerator.print_summary(analysis)

        # Generate reports
        output_dir = Path("./example_reports")
        output_dir.mkdir(exist_ok=True)

        # JSON report
        json_path = output_dir / "httpie_analysis.json"
        ReportGenerator.generate_json_report(analysis, str(json_path))

        # HTML report
        html_path = output_dir / "httpie_analysis.html"
<<<<<<< HEAD
        ReportGenerator.generate_repo_html_report(analysis, str(html_path))

        return analysis

    except Exception as e: # pylint: disable=broad-exception-caught
=======
        ReportGenerator.generate_html_report(analysis, str(html_path))

        return analysis

    except Exception as e:
>>>>>>> remotes/origin/sentinel-fix-git-branch-injection-14962938762884618886
        print(f"Error scanning repository: {e}")
        return None


def example_scan_local_directory():
    """
    Example 2: Scan a local directory

    This demonstrates scanning the current project directory.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Scanning Local Directory")
    print("=" * 60 + "\n")

    # Initialize the scanner
    scanner = GitHubRepoScanner(verbose=True)

    # Scan the current directory (this project)
    local_path = str(Path(__file__).parent)

    print(f"Target: {local_path}")
    print("-" * 60)

    try:
        # Perform the scan
        analysis = scanner.scan_local_directory(
            path=local_path,
            extensions=['.py']  # Only Python files
        )

        # Print summary
        ReportGenerator.print_summary(analysis)

        # Generate reports
        output_dir = Path("./example_reports")
        output_dir.mkdir(exist_ok=True)

        # JSON report
        json_path = output_dir / "local_analysis.json"
        ReportGenerator.generate_json_report(analysis, str(json_path))

        # HTML report
        html_path = output_dir / "local_analysis.html"
<<<<<<< HEAD
        ReportGenerator.generate_repo_html_report(analysis, str(html_path))

        return analysis

    except Exception as e: # pylint: disable=broad-exception-caught
=======
        ReportGenerator.generate_html_report(analysis, str(html_path))

        return analysis

    except Exception as e:
>>>>>>> remotes/origin/sentinel-fix-git-branch-injection-14962938762884618886
        print(f"Error scanning directory: {e}")
        return None


def example_custom_analysis():
    """
    Example 3: Custom analysis with specific options

    This demonstrates how to perform targeted analysis.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Custom Analysis Options")
    print("=" * 60 + "\n")

    # Initialize scanner in quiet mode
    scanner = GitHubRepoScanner(verbose=False)

    # Scan with custom extensions
    local_path = str(Path(__file__).parent)

<<<<<<< HEAD
    print("Scanning Python files only, quiet mode...")
=======
    print(f"Scanning Python files only, quiet mode...")
>>>>>>> remotes/origin/sentinel-fix-git-branch-injection-14962938762884618886
    print("-" * 60)

    try:
        analysis = scanner.scan_local_directory(
            path=local_path,
            extensions=['.py']
        )

        # Access analysis data programmatically
<<<<<<< HEAD
        print("\n📊 Analysis Results:")
=======
        print(f"\n📊 Analysis Results:")
>>>>>>> remotes/origin/sentinel-fix-git-branch-injection-14962938762884618886
        print(f"   Total files: {analysis.files_analyzed}")
        print(f"   Average AI probability: {analysis.average_ai_probability}%")
        print(f"   High-risk files: {len(analysis.high_risk_files)}")

<<<<<<< HEAD
        print("\n📈 Distribution:")
        for category, count in analysis.distribution.items():
            print(f"   {category}: {count} files")

        print("\n💻 Languages found:")
=======
        print(f"\n📈 Distribution:")
        for category, count in analysis.distribution.items():
            print(f"   {category}: {count} files")

        print(f"\n💻 Languages found:")
>>>>>>> remotes/origin/sentinel-fix-git-branch-injection-14962938762884618886
        for lang, count in analysis.language_breakdown.items():
            print(f"   {lang}: {count} files")

        if analysis.high_risk_files:
<<<<<<< HEAD
            print("\n⚠️  High-risk files requiring review:")
=======
            print(f"\n⚠️  High-risk files requiring review:")
>>>>>>> remotes/origin/sentinel-fix-git-branch-injection-14962938762884618886
            for f in analysis.high_risk_files[:5]:
                print(f"   • {f['file']} ({f['ai_probability']}%)")

        return analysis

<<<<<<< HEAD
    except Exception as e: # pylint: disable=broad-exception-caught
=======
    except Exception as e:
>>>>>>> remotes/origin/sentinel-fix-git-branch-injection-14962938762884618886
        print(f"Error: {e}")
        return None


def main():
    """
    Main function demonstrating various scanner capabilities
    """
    print("\n" + "=" * 70)
    print("   AI CODE DETECTOR - GitHub Repository Scanner Examples")
    print("=" * 70)

    # Run examples
    examples = [
        ("Local Directory Scan", example_scan_local_directory),
        ("Custom Analysis", example_custom_analysis),
    ]

    results = {}
    for name, func in examples:
        try:
            result = func()
            results[name] = "Success" if result else "Failed"
<<<<<<< HEAD
        except Exception as e: # pylint: disable=broad-exception-caught
=======
        except Exception as e:
>>>>>>> remotes/origin/sentinel-fix-git-branch-injection-14962938762884618886
            results[name] = f"Error: {e}"

    # Summary
    print("\n" + "=" * 70)
    print("   EXAMPLES SUMMARY")
    print("=" * 70)
    for name, status in results.items():
        icon = "✅" if status == "Success" else "❌"
        print(f"   {icon} {name}: {status}")

    print("\n📁 Reports generated in: ./example_reports/")
    print("\n" + "=" * 70)
    print("   For GitHub repository scanning, run:")
    print("   python github_repo_scanner.py https://github.com/user/repo")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
