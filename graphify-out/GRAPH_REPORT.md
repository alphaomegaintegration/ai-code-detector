# Graph Report - ai-code-detector  (2026-10-26)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 421 nodes · 607 edges · 28 communities (20 shown, 8 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 38 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `084764f9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- GitHubRepoScanner
- AICodeDetector
- AI Code Detector - Comprehensive Usage Guide
- AI Code Detection Methodology
- AI Code Detection: Complete Solution Delivery
- .scan_repository
- UserAuthenticationManager
- test_ai_code.py
- steps
- ._analyze_defensive_coding
- Best Practices
- Key Indicators Explained
- TestBranchValidation
- ._find_code_files
- AI Code Detector
- 🌐 GitHub Repository Scanning 🆕
- TestScannerE2E
- 🎓 Use Cases
- 📚 Additional Resources
- 📖 Understanding the Results
- 🚀 Quick Start
- 🤝 Best Practices
- 🔬 Methodology
- 🛠️ Technical Details
- 📊 Example Output
- ⚠️ Limitations
- 🧪 Testing the Tool
- sentinel.md

## God Nodes (most connected - your core abstractions)
1. `AICodeDetector` - 36 edges
2. `GitHubRepoScanner` - 33 edges
3. `AI Code Detector` - 19 edges
4. `ReportGenerator` - 15 edges
5. `AI Code Detection: Complete Solution Delivery` - 13 edges
6. `TestDefensiveCoding` - 12 edges
7. `main()` - 11 edges
8. `AI Code Detector - Comprehensive Usage Guide` - 11 edges
9. `AI Code Detection Methodology` - 11 edges
10. `TestAICodeDetector` - 9 edges

## Surprising Connections (you probably didn't know these)
- `TestBranchValidation` --uses--> `GitHubRepoScanner`  [INFERRED]
  tests/test_github_repo_scanner.py → github_repo_scanner.py
- `TestSymlinkTraversal` --uses--> `GitHubRepoScanner`  [INFERRED]
  tests/test_github_repo_scanner.py → github_repo_scanner.py
- `TestScannerE2E` --uses--> `GitHubRepoScanner`  [INFERRED]
  tests/test_scanner_e2e.py → github_repo_scanner.py
- `TestDefensiveCoding` --uses--> `AICodeDetector`  [INFERRED]
  tests/test_defensive_coding.py → ai_code_detector.py
- `TestAICodeDetector` --uses--> `AICodeDetector`  [INFERRED]
  tests/test_ai_code_detector.py → ai_code_detector.py

## Import Cycles
- None detected.

## Communities (28 total, 8 thin omitted)

### Community 0 - "GitHubRepoScanner"
Cohesion: 0.08
Nodes (9): main(), GitHubRepoScanner, main(), RepositoryAnalysis, ReportGenerator, example_custom_analysis(), example_scan_local_directory(), example_scan_public_repository() (+1 more)

### Community 2 - "AI Code Detector - Comprehensive Usage Guide"
Cohesion: 0.06
Nodes (33): Advanced Tips, Advanced Usage, AI Code Detector - Comprehensive Usage Guide, Basic Usage Examples, Batch Processing with Shell Scripts, Conclusion, Continuous Integration (CI/CD), Example 1: Analyze a Single File (+25 more)

### Community 3 - "AI Code Detection Methodology"
Cohesion: 0.06
Nodes (36): 1. Naming Pattern Analysis, 2. Comment Style Detection, 3. Code Structure Analysis, 4. Complexity Analysis, 5. Error Handling Analysis, 6. Documentation Analysis, 7. Formatting Consistency Analysis, 8. Syntax Modernity Analysis (+28 more)

### Community 4 - "AI Code Detection: Complete Solution Delivery"
Cohesion: 0.06
Nodes (33): 1. Academic Integrity, 1. **AI Code Detector Tool** (`ai_code_detector.py`), 2. **Comprehensive Methodology Document** (`METHODOLOGY.md`), 2. Professional Development, 3. Research and Analysis, 3. **User Guide** (`USAGE_GUIDE.md`), 4. **README Documentation** (`README.md`), 5. **Test Samples** (+25 more)

### Community 7 - "test_ai_code.py"
Cohesion: 0.11
Nodes (8): calculate_user_score(), create_user_profile(), _helper_calculate_age(), _helper_format_name(), _helper_validate_email(), process_user_data(), sort_user_list(), validate_user_input()

### Community 8 - "steps"
Cohesion: 0.13
Nodes (14): runs-on, steps, strategy, jobs, build, python-version, name, name (+6 more)

### Community 10 - "Best Practices"
Cohesion: 0.15
Nodes (13): 1. Collect Baseline Data, 1. Establish AI Usage Policy, 1. Set Clear Expectations, 2. Control for Confounding Variables, 2. Integrate into Code Review, 2. Use as a Conversation Starter, 3. Combine with Other Evidence, 3. Monitor Trends, Not Individuals (+5 more)

### Community 11 - "Key Indicators Explained"
Cohesion: 0.15
Nodes (13): Comprehensive Error Handling, HIGH Confidence, High Documentation, Interpreting Results, Key Indicators Explained, LOW Confidence, MEDIUM Confidence, Modern Syntax Heavy (+5 more)

### Community 14 - "AI Code Detector"
Cohesion: 0.20
Nodes (10): 🙏 Acknowledgments, AI Code Detector, 🔧 Command-Line Options, 📦 Files Included, 🔮 Future Enhancements, GitHub Repository Scanner Options 🆕, Key Features, 📝 License (+2 more)

### Community 15 - "🌐 GitHub Repository Scanning 🆕"
Cohesion: 0.29
Nodes (7): Features, 🌐 GitHub Repository Scanning 🆕, HTML Report, Overview, Repository Analysis Output, Skipped Directories, Supported Languages

### Community 17 - "🎓 Use Cases"
Cohesion: 0.50
Nodes (4): Academic Integrity, Professional Development, Research and Analysis, 🎓 Use Cases

### Community 18 - "📚 Additional Resources"
Cohesion: 0.50
Nodes (4): 📚 Additional Resources, Documentation, Related Tools, Research References

### Community 19 - "📖 Understanding the Results"
Cohesion: 0.50
Nodes (4): AI Probability Ranges, Confidence Levels, Key Indicators, 📖 Understanding the Results

### Community 20 - "🚀 Quick Start"
Cohesion: 0.50
Nodes (4): Basic Usage - Single Files, GitHub Repository Scanning 🆕, Installation, 🚀 Quick Start

### Community 21 - "🤝 Best Practices"
Cohesion: 0.50
Nodes (4): 🤝 Best Practices, For Developers, For Educators, For Organizations

### Community 22 - "🔬 Methodology"
Cohesion: 0.50
Nodes (4): Confidence Calculation, Detection Approach, Dimension Scoring, 🔬 Methodology

### Community 23 - "🛠️ Technical Details"
Cohesion: 0.50
Nodes (4): Performance, Requirements, Supported Languages, 🛠️ Technical Details

### Community 24 - "📊 Example Output"
Cohesion: 0.67
Nodes (3): Detailed Format, 📊 Example Output, Summary Format

### Community 25 - "⚠️ Limitations"
Cohesion: 0.67
Nodes (3): Evasion Techniques, Known Constraints, ⚠️ Limitations

### Community 26 - "🧪 Testing the Tool"
Cohesion: 0.67
Nodes (3): Run Tests, Test Samples Included, 🧪 Testing the Tool

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AICodeDetector` connect `AICodeDetector` to `GitHubRepoScanner`, `._analyze_defensive_coding`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `AICodeDetector` (e.g. with `GitHubRepoScanner` and `TestAICodeDetector`) actually correct?**
  _`AICodeDetector` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Should `GitHubRepoScanner` be split into smaller, more focused modules?**
  _Cohesion score 0.07581453634085213 - nodes in this community are weakly interconnected._
- **Why does `GitHubRepoScanner` connect `GitHubRepoScanner` to `AICodeDetector`, `.scan_repository`, `TestBranchValidation`, `._find_code_files`, `TestScannerE2E`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `GitHubRepoScanner` (e.g. with `AICodeDetector` and `DetectionResult`) actually correct?**
  _`GitHubRepoScanner` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `AICodeDetector` be split into smaller, more focused modules?**
  _Cohesion score 0.08502415458937199 - nodes in this community are weakly interconnected._
- **Why does `AI Code Detector - Comprehensive Usage Guide` connect `AI Code Detector - Comprehensive Usage Guide` to `Best Practices`, `Key Indicators Explained`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._