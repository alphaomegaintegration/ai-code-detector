"""
Report Generator for AI Code Detection
"""
# pylint: disable=line-too-long, too-many-lines
import json
import html
from datetime import datetime
from dataclasses import asdict
from typing import List, Any, Dict # pylint: disable=unused-import

class ReportGenerator:
    """Generate reports for AI code detection analysis."""

    CSS = """
        :root {
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --bg-card: rgba(255,255,255,0.05);
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0a0;
            --accent-purple: #533483;
            --accent-blue: #0f3460;
            --color-green: #28a745;
            --color-yellow: #ffc107;
            --color-orange: #fd7e14;
            --color-red: #dc3545;
            --color-gray: #6c757d;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }

        h1 {
            font-size: 2.2em;
            margin-bottom: 10px;
            color: #fff;
        }

        .meta {
            color: var(--text-secondary);
            font-size: 0.9em;
        }

        .meta span {
            margin-right: 20px;
        }

        /* Summary Section */
        .summary-section {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.1);
        }

        .summary-section h2 {
            color: #fff;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.1);
        }

        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }

        /* Override for repo scanner style cards */
        .stats-grid .stat-card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
            text-align: left;
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .stats-grid .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        .stats-grid .stat-card h3 {
            color: #a0a0a0;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #fff;
        }

        .stat-value.green { color: var(--color-green); }
        .stat-value.yellow { color: var(--color-yellow); }
        .stat-value.orange { color: var(--color-orange); }
        .stat-value.red { color: var(--color-red); }

        .stat-label {
            color: var(--text-secondary);
            font-size: 0.9em;
            margin-top: 5px;
        }

        section {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.1);
        }

        section h2 {
            color: #fff;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.1);
        }

        .distribution-section h3 {
            margin-bottom: 15px;
            color: #fff;
        }

        .distribution-bar {
            display: flex;
            height: 35px;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 15px;
        }

        .distribution-chart {
            display: flex;
            height: 40px;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 15px;
        }

        .dist-segment {
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.85em;
            color: #fff;
            min-width: 2px;
            transition: flex 0.3s;
        }

        .dist-segment.green { background: var(--color-green); }
        .dist-segment.yellow { background: var(--color-yellow); color: #333; }
        .dist-segment.orange { background: var(--color-orange); }
        .dist-segment.red { background: var(--color-red); }

        .distribution-legend, .legend {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }

        .legend {
            gap: 20px;
            margin-top: 15px;
        }

        .distribution-legend span, .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.9em;
        }

        .legend-item {
            gap: 8px;
        }

        .legend-dot, .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 3px;
        }

        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 4px;
        }

        .legend-dot.green, .legend-color[style*="28a745"] { background: var(--color-green) !important; }
        .legend-dot.yellow, .legend-color[style*="ffc107"] { background: var(--color-yellow) !important; }
        .legend-dot.orange, .legend-color[style*="fd7e14"] { background: var(--color-orange) !important; }
        .legend-dot.red, .legend-color[style*="dc3545"] { background: var(--color-red) !important; }

        /* File Cards */
        .file-card {
            background: var(--bg-card);
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .file-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }

        .file-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 20px;
            background: rgba(0,0,0,0.2);
            flex-wrap: wrap;
            gap: 15px;
        }

        .file-info {
            flex: 1;
            min-width: 250px;
        }

        .file-path {
            font-size: 1.1em;
            color: #fff;
            margin-bottom: 10px;
            word-break: break-all;
            font-family: 'Monaco', 'Consolas', monospace;
        }

        .verdict-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }

        .verdict-badge.green { background: rgba(40, 167, 69, 0.2); color: var(--color-green); border: 1px solid var(--color-green); }
        .verdict-badge.yellow { background: rgba(255, 193, 7, 0.2); color: var(--color-yellow); border: 1px solid var(--color-yellow); }
        .verdict-badge.orange { background: rgba(253, 126, 20, 0.2); color: var(--color-orange); border: 1px solid var(--color-orange); }
        .verdict-badge.red { background: rgba(220, 53, 69, 0.2); color: var(--color-red); border: 1px solid var(--color-red); }

        .file-summary {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .probability-circle {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border: 3px solid;
        }

        .probability-circle.green { border-color: var(--color-green); background: rgba(40, 167, 69, 0.1); }
        .probability-circle.yellow { border-color: var(--color-yellow); background: rgba(255, 193, 7, 0.1); }
        .probability-circle.orange { border-color: var(--color-orange); background: rgba(253, 126, 20, 0.1); }
        .probability-circle.red { border-color: var(--color-red); background: rgba(220, 53, 69, 0.1); }

        .prob-value {
            font-size: 1.3em;
            font-weight: bold;
        }

        .probability-circle.green .prob-value { color: var(--color-green); }
        .probability-circle.yellow .prob-value { color: var(--color-yellow); }
        .probability-circle.orange .prob-value { color: var(--color-orange); }
        .probability-circle.red .prob-value { color: var(--color-red); }

        .prob-label {
            font-size: 0.75em;
            color: var(--text-secondary);
        }

        .confidence-badge {
            background: rgba(255,255,255,0.1);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85em;
        }

        .file-details {
            padding: 20px;
            display: none;
        }

        .file-details.visible {
            display: block;
        }

        .details-section {
            margin-bottom: 25px;
        }

        .details-section h4 {
            color: #fff;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .dimensions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 10px;
        }

        .dimension-item {
            display: flex;
            align-items: center;
            padding: 10px;
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
        }

        .dim-icon {
            font-size: 1.1em;
            margin-right: 10px;
            width: 24px;
            text-align: center;
        }

        .dim-name {
            flex: 1;
            font-size: 0.9em;
            min-width: 100px;
        }

        .dim-bar-container {
            width: 80px;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin: 0 10px;
        }

        .dim-bar {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
        }

        .dim-score {
            font-weight: bold;
            font-size: 0.9em;
            width: 45px;
            text-align: right;
        }

        .pattern-category {
            margin-bottom: 15px;
        }

        .pattern-category h5 {
            color: var(--text-secondary);
            margin-bottom: 8px;
            font-size: 0.95em;
        }

        .pattern-list {
            list-style: none;
            padding-left: 10px;
        }

        .pattern-list li {
            padding: 6px 10px;
            background: rgba(0,0,0,0.15);
            border-radius: 4px;
            margin-bottom: 5px;
            font-size: 0.85em;
            font-family: 'Monaco', 'Consolas', monospace;
            word-break: break-all;
            border-left: 3px solid var(--accent-purple);
        }

        .indicators-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .indicator-badge {
            background: rgba(83, 52, 131, 0.3);
            border: 1px solid var(--accent-purple);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
        }

        .toggle-details {
            width: 100%;
            padding: 12px;
            background: rgba(255,255,255,0.05);
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 0.9em;
            transition: background 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .toggle-details:hover {
            background: rgba(255,255,255,0.1);
        }

        .expand-icon {
            transition: transform 0.2s;
        }

        .toggle-details.expanded .expand-icon {
            transform: rotate(180deg);
        }

        .lang-bar {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
        }

        .lang-name {
            width: 120px;
            font-weight: 500;
        }

        .bar-container {
            flex: 1;
            height: 24px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin: 0 15px;
        }

        .bar {
            height: 100%;
            background: linear-gradient(90deg, #533483, #0f3460);
            border-radius: 4px;
            transition: width 0.5s;
        }

        .lang-count {
            width: 80px;
            text-align: right;
            color: #a0a0a0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        th {
            background: rgba(0,0,0,0.2);
            color: #fff;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
        }

        tr:hover {
            background: rgba(255,255,255,0.05);
        }

        tr.high-risk {
            background: rgba(220, 53, 69, 0.1);
        }

        .verdict-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .verdict-item {
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            background: rgba(0,0,0,0.2);
        }

        .verdict-count {
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .verdict-label {
            font-size: 0.85em;
            color: #a0a0a0;
        }

        .table-container {
            max-height: 500px;
            overflow-y: auto;
            border-radius: 8px;
        }

        .table-container::-webkit-scrollbar {
            width: 8px;
        }

        .table-container::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.1);
        }

        .table-container::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.3);
            border-radius: 4px;
        }

        footer {
            text-align: center;
            padding: 20px;
            color: #666;
            margin-top: 30px;
        }

        @media (max-width: 768px) {
            h1 { font-size: 1.8em; }
            .stats-grid { grid-template-columns: 1fr 1fr; }
            .stat-value { font-size: 2em; }
            .file-header { flex-direction: column; }
            .file-summary { width: 100%; justify-content: flex-start; }
            .dimensions-grid { grid-template-columns: 1fr; }
            .summary-stats { grid-template-columns: 1fr 1fr; }
        }
    """

    @staticmethod
    def get_probability_color(prob): # pylint: disable=missing-function-docstring
        if prob >= 75:
            return '#dc3545'  # Red
        if prob >= 55:
            return '#fd7e14'  # Orange
        if prob >= 35:
            return '#ffc107'  # Yellow
        return '#28a745'  # Green

    @staticmethod
    def get_probability_class(prob): # pylint: disable=missing-function-docstring
        if prob >= 75:
            return 'red'
        if prob >= 55:
            return 'orange'
        if prob >= 35:
            return 'yellow'
        return 'green'

    @staticmethod
    def get_probability_label(prob): # pylint: disable=missing-function-docstring
        if prob >= 75:
            return 'Likely AI-Generated'
        if prob >= 55:
            return 'Possibly AI-Assisted'
        if prob >= 35:
            return 'Mixed Indicators'
        return 'Likely Human'

    @staticmethod
    def generate_json_report(data: Any, output_path: str):
        """Generate a JSON report"""
        with open(output_path, 'w', encoding='utf-8') as f:
            if hasattr(data, '__dict__'):
                json.dump(asdict(data), f, indent=2)
            else:
                json.dump(data, f, indent=2)
        print(f"JSON report saved to: {output_path}")

    @staticmethod
    def generate_repo_html_report(analysis: Any, output_path: str): # pylint: disable=too-many-locals
        """Generate a professional HTML report for repository analysis"""
        # Calculate percentages for distribution chart
        total = analysis.files_analyzed if analysis.files_analyzed > 0 else 1
        dist_percentages = {k: (v / total) * 100 for k, v in analysis.distribution.items()}

        # Generate top files HTML
        top_files_html = ""
        for i, file in enumerate(analysis.top_ai_files, 1):
            color = ReportGenerator.get_probability_color(file['ai_probability'])
            top_files_html += f"""
            <tr>
                <td>{i}</td>
                <td class="file-path">{html.escape(str(file['file']))}</td>
                <td style="color: {color}; font-weight: bold;">{file['ai_probability']}%</td>
                <td>{file['confidence']}</td>
                <td style="color: {color};">{html.escape(str(file['verdict']))}</td>
            </tr>"""

        # Generate high risk files HTML
        high_risk_html = ""
        if analysis.high_risk_files:
            for file in analysis.high_risk_files[:20]:  # Limit to 20
                high_risk_html += f"""
                <tr class="high-risk">
                    <td class="file-path">{html.escape(str(file['file']))}</td>
                    <td style="color: #dc3545; font-weight: bold;">{file['ai_probability']}%</td>
                    <td>{file['confidence']}</td>
                    <td style="color: #dc3545;">{html.escape(str(file['verdict']))}</td>
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
                <span class="lang-name">{html.escape(str(lang))}</span>
                <div class="bar-container">
                    <div class="bar" style="width: {width}%"></div>
                </div>
                <span class="lang-count">{count} files</span>
            </div>"""

        # Generate all files table
        all_files_html = ""
        sorted_results = sorted(analysis.file_results, key=lambda x: x['ai_probability'], reverse=True)
        for result in sorted_results:
            color = ReportGenerator.get_probability_color(result['ai_probability'])
            all_files_html += f"""
            <tr>
                <td class="file-path">{html.escape(str(result['file_path']))}</td>
                <td style="color: {color}; font-weight: bold;">{result['ai_probability']}%</td>
                <td>{result['human_probability']}%</td>
                <td>{result['confidence']}</td>
                <td style="color: {color};">{html.escape(str(result['verdict']))}</td>
            </tr>"""

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Code Detection Report - {html.escape(analysis.repository_url.split('/')[-1].replace('.git', ''))}</title>
    <style>{ReportGenerator.CSS}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 AI Code Detection Report</h1>
            <div class="meta">
                <span>📁 Repository: <strong>{html.escape(str(analysis.repository_url))}</strong></span>
                <span>🌿 Branch: <strong>{html.escape(str(analysis.branch))}</strong></span>
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
    def generate_files_report(results: List[Any], output_path: str, title: str): # pylint: disable=too-many-locals
        """Generate a professional HTML report for a list of files"""
        # Calculate summary statistics
        valid_results = [r for r in results if r.confidence != "ERROR"]
        total_files = len(valid_results)
        avg_ai_prob = sum(r.ai_probability for r in valid_results) / max(total_files, 1)

        # Distribution
        distribution = {
            'likely_human': sum(1 for r in valid_results if r.ai_probability < 35),
            'mixed': sum(1 for r in valid_results if 35 <= r.ai_probability < 55),
            'possibly_ai': sum(1 for r in valid_results if 55 <= r.ai_probability < 75),
            'likely_ai': sum(1 for r in valid_results if r.ai_probability >= 75),
        }

        # Generate file cards HTML
        file_cards_html = ""
        sorted_results = sorted(valid_results, key=lambda x: x.ai_probability, reverse=True)

        for idx, result in enumerate(sorted_results):
            color_class = ReportGenerator.get_probability_class(result.ai_probability)

            # Generate dimension scores HTML
            dimension_html = ""
            dimension_names = {
                'naming_analysis': ('Naming Patterns', '📝'),
                'comment_analysis': ('Comment Style', '💬'),
                'structure_analysis': ('Code Structure', '🏗️'),
                'complexity_analysis': ('Complexity', '🧩'),
                'error_handling': ('Error Handling', '🛡️'),
                'documentation': ('Documentation', '📖'),
                'formatting_consistency': ('Formatting', '✨'),
                'modern_syntax': ('Modern Syntax', '🚀'),
                'enhanced_comment_analysis': ('Enhanced Comments', '🔍'),
                'defensive_coding': ('Defensive Coding', '🔒'),
                'textbook_algorithms': ('Textbook Patterns', '📚'),
                'over_modularization': ('Over-Modularization', '📦'),
                'perfect_consistency': ('Perfect Consistency', '🎯'),
                'contextual_quirks': ('Contextual Quirks', '👤'),
                'formatting_perfection': ('Formatting Perfection', '💎'),
                'obvious_comments': ('Obvious Comments', '🔔'),
            }

            for dim_key, (dim_name, dim_icon) in dimension_names.items():
                if dim_key in result.detailed_scores:
                    score_data = result.detailed_scores[dim_key]
                    ai_indicator = score_data.get('ai_indicators', 0)
                    score_pct = ai_indicator * 100
                    score_color = ReportGenerator.get_probability_color(score_pct)
                    dimension_html += f'''
                    <div class="dimension-item">
                        <span class="dim-icon">{dim_icon}</span>
                        <span class="dim-name">{dim_name}</span>
                        <div class="dim-bar-container">
                            <div class="dim-bar" style="width: {score_pct}%; background: {score_color};"></div>
                        </div>
                        <span class="dim-score" style="color: {score_color};">{score_pct:.0f}%</span>
                    </div>'''

            # Generate detected patterns HTML
            patterns_html = ""
            pattern_categories = [
                ('obvious_comment_examples', 'Obvious Comments', '💬'),
                ('ai_phrases', 'AI-Typical Phrases', '🤖'),
                ('textbook_patterns', 'Textbook Patterns', '📚'),
                ('defensive_patterns', 'Defensive Coding', '🛡️'),
                ('small_functions', 'Small Functions', '📦'),
                ('missing_quirks', 'Missing Human Quirks', '👤'),
            ]

            for pattern_key, pattern_name, pattern_icon in pattern_categories:
                if pattern_key in result.detected_patterns and result.detected_patterns[pattern_key]:
                    patterns = result.detected_patterns[pattern_key][:5]
                    patterns_html += f'''
                    <div class="pattern-category">
                        <h5>{pattern_icon} {html.escape(str(pattern_name))}</h5>
                        <ul class="pattern-list">'''
                    for p in patterns:
                        escaped_p = html.escape(str(p))
                        patterns_html += f'<li>{escaped_p}</li>'
                    patterns_html += '</ul></div>'

            # Generate indicators HTML
            indicators_html = ""
            boolean_indicators = {k: v for k, v in result.indicators.items() if isinstance(v, bool) and v}
            if boolean_indicators:
                indicators_html = '<div class="indicators-list">'
                for key in boolean_indicators:
                    indicator_name = html.escape(key.replace('_', ' ').title())
                    indicators_html += f'<span class="indicator-badge">{indicator_name}</span>'
                indicators_html += '</div>'

            file_cards_html += f'''
            <div class="file-card" id="file-{idx}">
                <div class="file-header">
                    <div class="file-info">
                        <h3 class="file-path">📄 {html.escape(str(result.file_path))}</h3>
                        <span class="verdict-badge {color_class}">{html.escape(str(result.verdict))}</span>
                    </div>
                    <div class="file-summary">
                        <div class="probability-circle {color_class}">
                            <span class="prob-value">{result.ai_probability:.1f}%</span>
                            <span class="prob-label">AI</span>
                        </div>
                        <div class="confidence-badge">Confidence: {result.confidence}</div>
                    </div>
                </div>

                <div class="file-details">
                    <div class="details-section">
                        <h4>📊 Detection Dimensions (16 Total)</h4>
                        <div class="dimensions-grid">
                            {dimension_html}
                        </div>
                    </div>

                    {'<div class="details-section"><h4>🔍 Detected Patterns</h4>' + patterns_html + '</div>' if patterns_html else ''}

                    {'<div class="details-section"><h4>🎯 Key Indicators</h4>' + indicators_html + '</div>' if indicators_html else ''}
                </div>

                <button class="toggle-details" onclick="toggleDetails({idx})">
                    <span class="expand-icon">▼</span> Show Details
                </button>
            </div>'''

        # Summary row for multiple files
        summary_section = ""
        if total_files > 1:
            dist_total = max(sum(distribution.values()), 1)
            summary_section = f'''
            <section class="summary-section">
                <h2>📊 Analysis Summary</h2>
                <div class="summary-stats">
                    <div class="stat-card">
                        <div class="stat-value">{total_files}</div>
                        <div class="stat-label">Files Analyzed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value {ReportGenerator.get_probability_class(avg_ai_prob)}">{avg_ai_prob:.1f}%</div>
                        <div class="stat-label">Avg AI Probability</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value red">{distribution['likely_ai']}</div>
                        <div class="stat-label">Likely AI (≥75%)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value green">{distribution['likely_human']}</div>
                        <div class="stat-label">Likely Human (&lt;35%)</div>
                    </div>
                </div>

                <div class="distribution-section">
                    <h3>Distribution by AI Probability</h3>
                    <div class="distribution-bar">
                        <div class="dist-segment green" style="width: {distribution['likely_human'] / dist_total * 100}%;"
                             title="Likely Human (0-35%): {distribution['likely_human']} files"></div>
                        <div class="dist-segment yellow" style="width: {distribution['mixed'] / dist_total * 100}%;"
                             title="Mixed (35-55%): {distribution['mixed']} files"></div>
                        <div class="dist-segment orange" style="width: {distribution['possibly_ai'] / dist_total * 100}%;"
                             title="Possibly AI (55-75%): {distribution['possibly_ai']} files"></div>
                        <div class="dist-segment red" style="width: {distribution['likely_ai'] / dist_total * 100}%;"
                             title="Likely AI (75-100%): {distribution['likely_ai']} files"></div>
                    </div>
                    <div class="distribution-legend">
                        <span><span class="legend-dot green"></span> Likely Human (0-35%): {distribution['likely_human']}</span>
                        <span><span class="legend-dot yellow"></span> Mixed (35-55%): {distribution['mixed']}</span>
                        <span><span class="legend-dot orange"></span> Possibly AI (55-75%): {distribution['possibly_ai']}</span>
                        <span><span class="legend-dot red"></span> Likely AI (75-100%): {distribution['likely_ai']}</span>
                    </div>
                </div>
            </section>'''

        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(str(title))}</title>
    <style>{ReportGenerator.CSS}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 {html.escape(str(title))}</h1>
            <div class="meta">
                <span>📅 Generated: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong></span>
                <span>📁 Files: <strong>{total_files}</strong></span>
                <span>📊 Dimensions: <strong>16</strong></span>
            </div>
        </header>

        {summary_section}

        <section class="files-section">
            <h2 style="color: #fff; margin-bottom: 20px;">📄 File Analysis Results</h2>
            {file_cards_html if file_cards_html else '<p style="color: var(--text-secondary);">No files were analyzed.</p>'}
        </section>

        <footer>
            <p>Generated by AI Code Detector v2.0 | 16-Dimension Analysis</p>
            <p>Color coding: <span style="color:var(--color-green)">●</span> Likely Human (0-35%) |
               <span style="color:var(--color-yellow)">●</span> Mixed (35-55%) |
               <span style="color:var(--color-orange)">●</span> Possibly AI (55-75%) |
               <span style="color:var(--color-red)">●</span> Likely AI (75-100%)</p>
        </footer>
    </div>

    <script>
        function toggleDetails(idx) {{
            const card = document.getElementById('file-' + idx);
            const details = card.querySelector('.file-details');
            const btn = card.querySelector('.toggle-details');

            if (details.classList.contains('visible')) {{
                details.classList.remove('visible');
                btn.classList.remove('expanded');
                btn.innerHTML = '<span class="expand-icon">▼</span> Show Details';
            }} else {{
                details.classList.add('visible');
                btn.classList.add('expanded');
                btn.innerHTML = '<span class="expand-icon">▼</span> Hide Details';
            }}
        }}

        // Expand all for printing
        window.onbeforeprint = function() {{
            document.querySelectorAll('.file-details').forEach(el => el.classList.add('visible'));
        }};
    </script>
</body>
</html>'''

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML report saved to: {output_path}")

    @staticmethod
    def print_summary(analysis: Any):
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
