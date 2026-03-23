# AI Code Detector

**A comprehensive, multi-dimensional tool for detecting AI-generated code using pattern recognition, statistical analysis, and heuristic evaluation.**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Overview

AI Code Detector is a sophisticated analysis tool that distinguishes between human-written and AI-generated source code by examining eight independent dimensions:

1. **Naming Pattern Analysis** - Verbose vs. abbreviated identifiers
2. **Comment Style Detection** - Formal documentation vs. informal notes
3. **Code Structure Analysis** - Formatting consistency and organization
4. **Complexity Analysis** - Line length, nesting, and control flow
5. **Error Handling Analysis** - Defensive programming patterns
6. **Documentation Analysis** - Docstring completeness and quality
7. **Formatting Consistency** - Operator spacing and style uniformity
8. **Syntax Modernity** - Modern vs. legacy language features

### Key Features

✅ **Multi-Language Support**: Python, JavaScript, Java, C/C++, PHP, Ruby, Go, TypeScript, and 12+ more  
✅ **GitHub Repository Scanning**: Clone and analyze entire repositories with one command 🆕  
✅ **HTML Reports**: Professional visualizations with charts and color-coded results 🆕  
✅ **High Accuracy**: Research-backed detection methodology  
✅ **Confidence Scoring**: Variance-based confidence calculation  
✅ **Detailed Reports**: Comprehensive analysis with dimension-specific scores  
✅ **Batch Processing**: Analyze entire directories recursively  
✅ **JSON Export**: Machine-readable output for integration  
✅ **Repository Statistics**: Distribution, language breakdown, high-risk files 🆕  
✅ **Zero Dependencies**: Pure Python implementation  

---

## 🚀 Quick Start

### Installation

```bash
# Clone or download the tool
git clone https://github.com/alphaomegaintegration/ai-code-detector/
cd ~/ai_code_detector

# Make executable (optional)
chmod +x ai_code_detector.py
chmod +x github_repo_scanner.py
```

### Basic Usage - Single Files

```bash
# Analyze a single file
python ai_code_detector.py script.py

# Analyze multiple files
python ai_code_detector.py file1.py file2.js file3.java

# Analyze entire directory
python ai_code_detector.py --directory ./src

# Get detailed analysis
python ai_code_detector.py script.py --format detailed

# Export results to JSON
python ai_code_detector.py --directory ./src --output results.json
```

### GitHub Repository Scanning 🆕

```bash
# Scan a public GitHub repository
python github_repo_scanner.py https://github.com/user/repository

# Scan a specific branch
python github_repo_scanner.py https://github.com/user/repo --branch develop

# Generate reports to a specific directory
python github_repo_scanner.py https://github.com/user/repo -o ./reports

# Scan only specific file types
python github_repo_scanner.py https://github.com/user/repo --extensions .py,.js

# Scan a local directory
python github_repo_scanner.py --local ./my-project

# Generate only JSON report
python github_repo_scanner.py https://github.com/user/repo --json-only

# Generate only HTML report
python github_repo_scanner.py https://github.com/user/repo --html-only

# Quiet mode (suppress progress output)
python github_repo_scanner.py https://github.com/user/repo -q
```

---

## 📊 Example Output

### Summary Format

```
======================================================================
File: authentication.py
======================================================================
AI Probability:    78.5%
Human Probability: 21.5%
Confidence:        HIGH
Verdict:           LIKELY AI-GENERATED

Key Indicators:
  • Verbose Naming: True
  • High Documentation: True
  • Perfect Formatting: True
  • Comprehensive Error Handling: True
  • Modern Syntax Heavy: True
```

### Detailed Format

```
======================================================================
DETAILED ANALYSIS: authentication.py
======================================================================
AI Probability:    78.5%
Human Probability: 21.5%
Confidence:        HIGH
Verdict:           LIKELY AI-GENERATED

Detailed Scores:

  Naming Analysis:
    ai_indicators: 0.8
    avg_identifier_length: 14.2
    verbose_count: 45
    abbreviated_count: 3
    descriptive_count: 12

  Comment Analysis:
    ai_indicators: 0.9
    comment_ratio: 0.35
    formal_comments: 8
    informal_comments: 0
    avg_comment_length: 125.4

  [... additional dimensions ...]
```

---

## 🔧 Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `files` | One or more files to analyze | `script.py main.js` |
| `-d, --directory` | Analyze all code files in directory | `--directory ./src` |
| `-o, --output` | Save results to JSON file | `--output results.json` |
| `-f, --format` | Output format: `summary` or `detailed` | `--format detailed` |
| `--extensions` | File extensions to analyze (comma-separated) | `--extensions .py,.js,.java` |

### GitHub Repository Scanner Options 🆕

| Option | Description | Example |
|--------|-------------|---------|
| `url` | GitHub repository URL to scan | `https://github.com/user/repo` |
| `-b, --branch` | Branch to analyze (default: main/master) | `--branch develop` |
| `-o, --output-dir` | Output directory for reports | `-o ./reports` |
| `--local` | Scan a local directory instead | `--local ./my-project` |
| `--extensions` | File extensions to analyze | `--extensions .py,.js` |
| `--json-only` | Generate only JSON report | `--json-only` |
| `--html-only` | Generate only HTML report | `--html-only` |
| `-q, --quiet` | Suppress progress output | `-q` |

---

## 🌐 GitHub Repository Scanning 🆕

### Overview

The GitHub Repository Scanner extends the AI Code Detector to analyze entire repositories, providing comprehensive insights into AI-generated code across your codebase.

### Features

- **Repository Cloning**: Automatically clones public/private repositories
- **Branch Support**: Analyze specific branches
- **Multi-Language Support**: 20+ programming languages
- **Comprehensive Statistics**: Total files, averages, distributions
- **High-Risk Detection**: Identifies files most likely AI-generated
- **HTML Reports**: Professional visualizations with color-coded results
- **JSON Export**: Machine-readable data for further analysis
- **Automatic Cleanup**: Temporary files are removed after analysis

### Repository Analysis Output

```
================================================================================
🔍 AI CODE DETECTION - REPOSITORY ANALYSIS SUMMARY
================================================================================

📁 Repository: https://github.com/example/project
🌿 Branch: main
📅 Analyzed: 2026-02-12 14:30:45

────────────────────────────────────────
📊 STATISTICS
────────────────────────────────────────
  Total Files Analyzed: 156
  Average AI Probability: 42.3%
  High Risk Files: 8

────────────────────────────────────────
📈 DISTRIBUTION
────────────────────────────────────────
  likely_human (0-35%): 78 files
  mixed (35-55%): 42 files
  possibly_ai (55-75%): 28 files
  likely_ai (75-100%): 8 files

────────────────────────────────────────
💻 LANGUAGE BREAKDOWN
────────────────────────────────────────
  Python: 89 files
  JavaScript: 45 files
  TypeScript: 22 files

────────────────────────────────────────
⚠️  HIGH RISK FILES
────────────────────────────────────────
  • src/utils/helpers.py (87.5%)
  • src/api/handlers.py (82.3%)
  • lib/validators.js (78.9%)

────────────────────────────────────────
🔝 TOP 5 AI-LIKELY FILES
────────────────────────────────────────
  1. src/utils/helpers.py - 87.5% AI
  2. src/api/handlers.py - 82.3% AI
  3. lib/validators.js - 78.9% AI
  4. tests/test_auth.py - 76.2% AI
  5. src/models/user.py - 74.1% AI
================================================================================
```

### HTML Report

The scanner generates professional HTML reports with:

- 📊 **Summary Statistics Cards** - Quick overview of key metrics
- 📈 **Distribution Chart** - Visual breakdown of AI probability ranges
- 💻 **Language Breakdown** - Bar chart showing files per language
- 🔝 **Top AI-Likely Files** - Table of highest probability files
- ⚠️ **High Risk Files** - Color-coded list requiring review
- 📋 **Complete File List** - Searchable table with all results

### Supported Languages

| Language | Extensions |
|----------|-----------|
| Python | `.py` |
| JavaScript | `.js`, `.jsx`, `.mjs` |
| TypeScript | `.ts`, `.tsx` |
| Java | `.java` |
| C++ | `.cpp`, `.cxx`, `.cc`, `.hpp`, `.h` |
| C | `.c` |
| C# | `.cs` |
| Go | `.go` |
| Ruby | `.rb` |
| PHP | `.php` |
| Rust | `.rs` |
| Swift | `.swift` |
| Kotlin | `.kt`, `.kts` |
| Scala | `.scala` |
| Shell | `.sh`, `.bash` |
| HTML | `.html`, `.htm` |
| CSS | `.css`, `.scss`, `.sass`, `.less` |
| SQL | `.sql` |
| YAML | `.yml`, `.yaml` |
| Markdown | `.md` |

### Skipped Directories

The scanner automatically skips these directories:
- `node_modules`, `vendor`, `venv`, `.venv`
- `__pycache__`, `.git`, `.svn`, `.hg`
- `dist`, `build`, `target`, `bin`, `obj`
- `.idea`, `.vscode`, `coverage`

---

## 📖 Understanding the Results

### AI Probability Ranges

| Range | Interpretation | Recommended Action |
|-------|----------------|-------------------|
| **0-35%** | Likely Human-Written | Low suspicion, minimal review needed |
| **35-55%** | Mixed Indicators | Moderate suspicion, contextual review |
| **55-75%** | Possibly AI-Assisted | High suspicion, detailed review required |
| **75-100%** | Likely AI-Generated | Very high suspicion, thorough investigation |

### Confidence Levels

- **HIGH**: All dimensions agree, verdict is reliable
- **MEDIUM**: Moderate variation across dimensions, verdict is probable
- **LOW**: High variation, inconclusive, manual review essential

### Key Indicators

The tool highlights specific patterns that strongly suggest AI generation:

- **Verbose Naming**: Identifiers average >10 characters
- **High Documentation**: >70% of functions/classes have docstrings
- **Perfect Formatting**: >90% consistency in spacing and indentation
- **Comprehensive Error Handling**: >8% of lines are error handling
- **Modern Syntax Heavy**: >80% modern language features

---

## 🧪 Testing the Tool

### Test Samples Included

The repository includes two test samples demonstrating the detection capability:

1. **`test_samples/ai_generated_sample.py`**: Simulated AI-generated code with verbose naming, comprehensive documentation, and perfect formatting
2. **`test_samples/human_written_sample.py`**: Simulated human-written code with abbreviated variables, minimal comments, and informal style

### Run Tests

```bash
python ai_code_detector.py test_samples/*.py --format detailed
```

**Expected Results**:
- AI sample: 70-85% AI probability, HIGH confidence
- Human sample: 10-25% AI probability, HIGH confidence

---

## 🔬 Methodology

### Detection Approach

The tool employs a **multi-dimensional scoring system** where each dimension contributes equally to the final AI probability:

```
AI_Probability = (Σ dimension_scores) / 8
```

### Dimension Scoring

Each dimension analyzes specific code characteristics:

1. **Naming Patterns**: Measures identifier verbosity and descriptiveness
2. **Comment Style**: Evaluates documentation formality and density
3. **Code Structure**: Assesses formatting consistency
4. **Complexity**: Analyzes line length and nesting patterns
5. **Error Handling**: Counts defensive programming constructs
6. **Documentation**: Measures docstring coverage and quality
7. **Formatting**: Evaluates operator spacing consistency
8. **Syntax Modernity**: Compares modern vs. legacy feature usage

### Confidence Calculation

Confidence is determined by analyzing **variance** across dimension scores:

- **Low variance** (< 0.05): All dimensions agree → HIGH confidence
- **Medium variance** (0.05-0.15): Moderate agreement → MEDIUM confidence
- **High variance** (≥ 0.15): Dimensions conflict → LOW confidence

For complete methodology details, see **[METHODOLOGY.md](METHODOLOGY.md)**.

---

## 🎓 Use Cases

### Academic Integrity

- **Computer Science Education**: Detect plagiarism in programming assignments
- **Coding Bootcamps**: Verify student work authenticity
- **Online Courses**: Monitor submission integrity

### Professional Development

- **Code Review**: Identify AI-assisted contributions in pull requests
- **Quality Assurance**: Flag code requiring additional human review
- **Intellectual Property**: Verify code authorship for licensing compliance

### Research and Analysis

- **AI Impact Studies**: Measure AI adoption in open-source projects
- **Code Quality Research**: Compare human vs. AI code characteristics
- **Tool Development**: Benchmark AI coding assistant outputs

---

## ⚠️ Limitations

### Known Constraints

1. **Probabilistic, Not Definitive**: Results indicate likelihood, not certainty
2. **False Positives**: Highly disciplined human code may trigger AI indicators
3. **False Negatives**: Heavily modified AI code may evade detection
4. **Minimum Code Length**: Requires ~50+ lines for reliable analysis
5. **Language Variations**: Accuracy varies by programming language

### Evasion Techniques

Sophisticated users may attempt to evade detection through:

- Variable renaming (shortening verbose names)
- Comment removal (stripping documentation)
- Formatting disruption (introducing inconsistencies)
- Logic restructuring (refactoring code organization)

**Note**: Complete evasion is difficult due to the multi-dimensional approach requiring systematic modification across all eight dimensions.

---

## 🤝 Best Practices

### For Educators

1. **Use as Decision Support**: Combine tool results with manual review
2. **Set Clear Policies**: Define acceptable AI usage in your context
3. **Focus on Learning**: Use detection to guide conversations, not punish
4. **Continuous Monitoring**: Track trends over time, not just individual cases

### For Developers

1. **Transparency First**: Disclose AI usage proactively
2. **Human Oversight**: Review and modify AI-generated code
3. **Proper Attribution**: Credit AI tools in commit messages or documentation
4. **Quality Focus**: Use detection to identify code needing extra review

### For Organizations

1. **Establish Guidelines**: Define AI usage policies for your team
2. **Integrate into Workflow**: Add detection to CI/CD pipelines
3. **Track Metrics**: Monitor AI adoption and code quality trends
4. **Support Training**: Help developers use AI tools effectively

---

## 📚 Additional Resources

### Documentation

- **[METHODOLOGY.md](METHODOLOGY.md)**: Complete technical methodology and research foundation
- **Test Samples**: Example AI and human code in `test_samples/`

### Research References

1. Hoq, M., et al. (2024). "Detecting ChatGPT-Generated Code Submissions in a CS1 Course"
2. CodeRabbit (2025). "AI vs Human Code Generation Report"
3. arXiv:2512.00867 (2025). "The AI Attribution Paradox"

### Related Tools

- **GPTZero**: Text and code detection
- **Codequiry**: Neural network-based detection
- **SonarQube**: AI code quality assurance

---

## 🛠️ Technical Details

### Requirements

- **Python**: 3.7 or higher
- **Dependencies**: None (pure Python standard library)
- **Operating System**: Cross-platform (Linux, macOS, Windows)

### Supported Languages

Primary support (highest accuracy):
- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- Java (.java)

Secondary support (good accuracy):
- C/C++ (.c, .cpp, .h, .hpp)
- PHP (.php)
- Ruby (.rb)
- Go (.go)

### Performance

- **Speed**: ~100-500 files per second (depending on file size)
- **Memory**: Minimal (<50MB for typical usage)
- **Scalability**: Can process large codebases (10,000+ files)

---

## 📝 License

This project is released under the **MIT License**.

```
MIT License

Copyright (c) 2026 AI Code Detector

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

This tool is built on research from:

- Academic institutions studying AI code generation
- Open-source communities analyzing AI adoption
- Industry leaders developing AI detection methodologies

Special thanks to the researchers and developers advancing the field of AI code detection.

---

## 📧 Support

For questions, issues, or contributions:

1. Review the [METHODOLOGY.md](METHODOLOGY.md) for technical details
2. Check test samples for usage examples
3. Examine the source code for implementation details

---

## 🔮 Future Enhancements

Potential improvements for future versions:

- [x] GitHub repository scanning ✅ **NEW in v1.1**
- [x] HTML report generation with visualizations ✅ **NEW in v1.1**
- [x] Repository-level statistics ✅ **NEW in v1.1**
- [ ] Machine learning model integration for improved accuracy
- [ ] AST (Abstract Syntax Tree) analysis for deeper structural insights
- [ ] Language-specific detection rules
- [ ] Real-time IDE integration
- [ ] Web-based interface
- [ ] API endpoint for programmatic access
- [ ] Database of known AI code patterns
- [ ] Temporal analysis for commit history

---

**Version**: 1.1  
**Last Updated**: February 2026  
**Status**: Production Ready

---

## 📦 Files Included

| File | Description |
|------|-------------|
| `ai_code_detector.py` | Core detection tool for individual files |
| `github_repo_scanner.py` | Repository scanning with HTML/JSON reports |
| `scan_example.py` | Sample usage script |
| `README.md` | This documentation |
| `METHODOLOGY.md` | Technical methodology details |
| `USAGE_GUIDE.md` | Detailed usage guide |
| `test_samples/` | Example AI and human code samples |

---

*Built with precision. Used with responsibility.*
