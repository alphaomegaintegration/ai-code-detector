#!/usr/bin/env python3
# pylint: disable=too-many-lines
"""
AI Code Detector - Multi-Dimensional Analysis Tool (Enhanced Version)
Detects AI-generated code using pattern recognition, statistical analysis, and heuristics
Now with sophisticated detection for AI-generated code characteristics
"""

import re
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter
from dataclasses import dataclass, asdict, field


@dataclass
class DetectionResult:
    file_path: str
    ai_probability: float
    human_probability: float
    confidence: str
    indicators: Dict[str, Any]
    detailed_scores: Dict[str, Any]
    verdict: str
    detected_patterns: Dict[str, List[str]] = field(default_factory=dict)


# pylint: disable=too-many-instance-attributes
class AICodeDetector:
    def __init__(self):
        self.ai_patterns = {
            'verbose_naming': r'[a-z]+[A-Z][a-z]+[A-Z][a-z]+',
            'descriptive_vars': r'(user_data|response_data|result_data|input_value|output_value)',
            'formal_comments': r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')',
            'type_hints': r':\s*(str|int|float|bool|List|Dict|Tuple|Optional|Union)',
        }

        self.human_patterns = {
            'abbreviated_vars': r'\b(i|j|k|x|y|z|tmp|temp|val|res|arr|obj|fn|cb|idx|cnt|num|str)\b',
            'legacy_syntax': r'(var\s+|function\s*\(|\.prototype\.|document\.write)',
            'informal_comments': r'(#\s*TODO|#\s*FIXME|#\s*HACK|#\s*NOTE|#\s*XXX|//\s*TODO|//\s*FIXME|//\s*HACK|//\s*NOTE|//\s*XXX)',
        }

        # AI-typical comment phrases (over-explanation patterns)
        self.ai_comment_phrases = [
            r'check\s+that',
            r'ensure\s+that',
            r'make\s+sure',
            r'initialize\s+the',
            r'set\s+up\s+the',
            r'clean\s+up\s+the',
            r'verify\s+that',
            r'validate\s+that',
            r'this\s+function\s+(will|does|should)',
            r'this\s+method\s+(will|does|should)',
            r'the\s+following\s+(code|function|method)',
            r'handles?\s+the\s+case',
            r'returns?\s+the\s+result',
            r'loop\s+through\s+(the|all|each)',
            r'iterate\s+over\s+(the|all|each)',
            r'should\s+be\s+initialized',
            r'should\s+have\s+the\s+expected',
            r'should\s+contain',
            r'test\s+that\s+the',
        ]

        # Obvious comment patterns (explaining what code does, not why)
        self.obvious_comment_patterns = [
            (r'#\s*increment\s+\w+', 'Increment variable'),
            (r'#\s*decrement\s+\w+', 'Decrement variable'),
            (r'#\s*initialize\s+(the\s+)?\w+', 'Initialize variable'),
            (r'#\s*set\s+\w+\s+to', 'Set variable to'),
            (r'#\s*return\s+(the\s+)?result', 'Return result'),
            (r'#\s*return\s+(the\s+)?value', 'Return value'),
            (r'#\s*loop\s+through', 'Loop through'),
            (r'#\s*iterate\s+over', 'Iterate over'),
            (r'#\s*check\s+if', 'Check if'),
            (r'#\s*verify\s+that', 'Verify that'),
            (r'#\s*create\s+(a\s+)?new', 'Create new'),
            (r'#\s*add\s+\w+\s+to', 'Add to'),
            (r'#\s*remove\s+\w+\s+from', 'Remove from'),
            (r'#\s*update\s+(the\s+)?\w+', 'Update variable'),
            (r'#\s*get\s+(the\s+)?\w+', 'Get variable'),
            (r'#\s*set\s+(the\s+)?\w+', 'Set variable'),
            (r'#\s*call\s+(the\s+)?\w+', 'Call function'),
            (r'#\s*import\s+\w+', 'Import statement'),
            (r'#\s*define\s+\w+', 'Define variable'),
            (r'#\s*assign\s+\w+', 'Assign variable'),
            (r'//\s*increment\s+\w+', 'Increment variable'),
            (r'//\s*decrement\s+\w+', 'Decrement variable'),
            (r'//\s*initialize\s+\w+', 'Initialize variable'),
            (r'//\s*set\s+\w+\s+to', 'Set variable to'),
            (r'//\s*return\s+(the\s+)?result', 'Return result'),
            (r'//\s*loop\s+through', 'Loop through'),
            (r'//\s*check\s+if', 'Check if'),
        ]

        # Textbook algorithm patterns
        self.textbook_patterns = [
            (r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(\s*\w+\s*\)\s*\)', 'range(len()) instead of enumerate'),
            (r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(\s*\w+\s*\)\s*-\s*1\s*\)', 'Bubble sort pattern'),
            (r'if\s+\w+\s*==\s*True', 'Explicit True comparison'),
            (r'if\s+\w+\s*==\s*False', 'Explicit False comparison'),
            (r'if\s+len\s*\(\s*\w+\s*\)\s*==\s*0', 'len() == 0 instead of not'),
            (r'if\s+len\s*\(\s*\w+\s*\)\s*>\s*0', 'len() > 0 instead of truthiness'),
            (r'(\w+)\s*=\s*\1\s*\+\s*1', 'i = i + 1 instead of i += 1'),
            (r'\[\s*i\s*\]\s*>\s*\[\s*i\s*\+\s*1\s*\]', 'Adjacent element comparison (bubble sort)'),
        ]

    # pylint: disable=too-many-locals
    def analyze_file(self, file_path: str) -> DetectionResult:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
        except Exception as e:
            return DetectionResult(
                file_path=file_path,
                ai_probability=0.0,
                human_probability=0.0,
                confidence="ERROR",
                indicators={"error": str(e)},
                detailed_scores={},
                verdict="Unable to analyze",
                detected_patterns={}
            )

        detected_patterns = {}
        scores = {}

        # Original 8 dimensions
        scores['naming_analysis'] = self._analyze_naming_patterns(code)
        scores['comment_analysis'] = self._analyze_comment_style(code)
        scores['structure_analysis'] = self._analyze_code_structure(code)
        scores['complexity_analysis'] = self._analyze_complexity(code)
        scores['error_handling'] = self._analyze_error_handling(code)
        scores['documentation'] = self._analyze_documentation(code)
        scores['formatting_consistency'] = self._analyze_formatting(code)
        scores['modern_syntax'] = self._analyze_syntax_modernity(code)

        # New enhanced dimensions
        comment_result = self._analyze_enhanced_comments(code)
        scores['enhanced_comment_analysis'] = comment_result['scores']
        detected_patterns['obvious_comments'] = comment_result['obvious_comments']
        detected_patterns['ai_phrases'] = comment_result['ai_phrases']

        defensive_result = self._analyze_defensive_coding(code)
        scores['defensive_coding'] = defensive_result['scores']
        detected_patterns['defensive_patterns'] = defensive_result['patterns']

        textbook_result = self._analyze_textbook_algorithms(code)
        scores['textbook_algorithms'] = textbook_result['scores']
        detected_patterns['textbook_patterns'] = textbook_result['patterns']

        modular_result = self._analyze_over_modularization(code)
        scores['over_modularization'] = modular_result['scores']
        detected_patterns['small_functions'] = modular_result['small_functions']

        consistency_result = self._analyze_enhanced_consistency(code)
        scores['perfect_consistency'] = consistency_result

        quirks_result = self._analyze_contextual_quirks(code)
        scores['contextual_quirks'] = quirks_result['scores']
        detected_patterns['missing_quirks'] = quirks_result['missing']

        formatting_result = self._analyze_formatting_perfection(code)
        scores['formatting_perfection'] = formatting_result

        obvious_result = self._analyze_obvious_comments(code)
        scores['obvious_comments'] = obvious_result['scores']
        detected_patterns['obvious_comment_examples'] = obvious_result['examples']

        # Calculate weighted AI score from all dimensions
        dimension_scores = [
            # Original dimensions (weight: 1.0)
            (scores['naming_analysis']['ai_indicators'], 1.0),
            (scores['comment_analysis']['ai_indicators'], 1.0),
            (scores['structure_analysis']['ai_indicators'], 1.0),
            (scores['complexity_analysis']['ai_indicators'], 1.0),
            (scores['error_handling']['ai_indicators'], 1.0),
            (scores['documentation']['ai_indicators'], 1.0),
            (scores['formatting_consistency']['ai_indicators'], 1.0),
            (scores['modern_syntax']['ai_indicators'], 1.0),
            # New dimensions (weight: 1.2 for higher impact)
            (scores['enhanced_comment_analysis']['ai_indicators'], 1.2),
            (scores['defensive_coding']['ai_indicators'], 1.2),
            (scores['textbook_algorithms']['ai_indicators'], 1.0),
            (scores['over_modularization']['ai_indicators'], 1.0),
            (scores['perfect_consistency']['ai_indicators'], 1.2),
            (scores['contextual_quirks']['ai_indicators'], 1.2),
            (scores['formatting_perfection']['ai_indicators'], 1.2),
            (scores['obvious_comments']['ai_indicators'], 1.3),
        ]

        total_weight = sum(w for _, w in dimension_scores)
        ai_score = sum(s * w for s, w in dimension_scores) / total_weight

        human_score = 1.0 - ai_score
        confidence = self._calculate_confidence(scores)
        verdict = self._determine_verdict(ai_score, confidence, scores)
        indicators = self._extract_key_indicators(scores, detected_patterns)

        return DetectionResult(
            file_path=file_path,
            ai_probability=round(ai_score * 100, 2),
            human_probability=round(human_score * 100, 2),
            confidence=confidence,
            indicators=indicators,
            detailed_scores={k: v for k, v in scores.items()},
            verdict=verdict,
            detected_patterns=detected_patterns
        )

    # pylint: disable=too-many-locals
    def _analyze_naming_patterns(self, code: str) -> Dict[str, Any]:
        lines = [l for l in code.split('\n') if l.strip() and not l.strip().startswith('#')]

        verbose_matches = len(re.findall(self.ai_patterns['verbose_naming'], code))
        descriptive_matches = len(re.findall(self.ai_patterns['descriptive_vars'], code))
        abbreviated_matches = len(re.findall(self.human_patterns['abbreviated_vars'], code))

        identifiers = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)
        avg_identifier_length = sum(len(i) for i in identifiers) / max(len(identifiers), 1)

        ai_score = 0.0
        if avg_identifier_length > 12:
            ai_score += 0.4
        elif avg_identifier_length > 8:
            ai_score += 0.2

        if verbose_matches > len(lines) * 0.3:
            ai_score += 0.3
        if descriptive_matches > 5:
            ai_score += 0.2
        if abbreviated_matches > len(lines) * 0.2:
            ai_score -= 0.3

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'ai_indicators': ai_score,
            'avg_identifier_length': round(avg_identifier_length, 2),
            'verbose_count': verbose_matches,
            'abbreviated_count': abbreviated_matches,
            'descriptive_count': descriptive_matches
        }

    def _analyze_comment_style(self, code: str) -> Dict[str, Any]:
        lines = code.split('\n')
        comment_lines = [l for l in lines if l.strip().startswith('#') or l.strip().startswith('//')]

        formal_comments = len(re.findall(self.ai_patterns['formal_comments'], code))
        informal_comments = len(re.findall(self.human_patterns['informal_comments'], code))

        code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        comment_ratio = len(comment_lines) / max(len(code_lines), 1)

        avg_comment_length = sum(len(c) for c in comment_lines) / max(len(comment_lines), 1) if comment_lines else 0

        ai_score = 0.0
        if comment_ratio > 0.3:
            ai_score += 0.3
        if formal_comments > 2:
            ai_score += 0.3
        if avg_comment_length > 60:
            ai_score += 0.2
        if informal_comments > 3:
            ai_score -= 0.3

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'ai_indicators': ai_score,
            'comment_ratio': round(comment_ratio, 3),
            'formal_comments': formal_comments,
            'informal_comments': informal_comments,
            'avg_comment_length': round(avg_comment_length, 2)
        }

    def _analyze_code_structure(self, code: str) -> Dict[str, Any]:
        lines = [l for l in code.split('\n') if l.strip()]

        indentation_levels = []
        for line in lines:
            if line.strip():
                spaces = len(line) - len(line.lstrip())
                indentation_levels.append(spaces)

        indent_consistency = 0.0
        if indentation_levels:
            indent_counter = Counter([i % 4 for i in indentation_levels if i > 0])
            if indent_counter:
                most_common = indent_counter.most_common(1)[0][1]
                indent_consistency = most_common / len([i for i in indentation_levels if i > 0])

        blank_lines = code.count('\n\n')
        blank_line_ratio = blank_lines / max(len(lines), 1)

        ai_score = 0.0
        if indent_consistency > 0.95:
            ai_score += 0.4
        elif indent_consistency > 0.85:
            ai_score += 0.2

        if 0.05 < blank_line_ratio < 0.15:
            ai_score += 0.2

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'ai_indicators': ai_score,
            'indent_consistency': round(indent_consistency, 3),
            'blank_line_ratio': round(blank_line_ratio, 3)
        }

    def _analyze_complexity(self, code: str) -> Dict[str, Any]:
        lines = [l.strip() for l in code.split('\n') if l.strip()]

        avg_line_length = sum(len(l) for l in lines) / max(len(lines), 1)

        control_structures = len(re.findall(r'\b(if|for|while|switch|case)\b', code))
        nesting_indicators = code.count('    if') + code.count('        if')

        ai_score = 0.0
        if 60 < avg_line_length < 90:
            ai_score += 0.3

        if control_structures > 0:
            nesting_ratio = nesting_indicators / control_structures
            if nesting_ratio < 0.3:
                ai_score += 0.2

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'ai_indicators': ai_score,
            'avg_line_length': round(avg_line_length, 2),
            'control_structures': control_structures,
            'nesting_indicators': nesting_indicators
        }

    def _analyze_error_handling(self, code: str) -> Dict[str, Any]:
        try_blocks = len(re.findall(r'\btry\s*:', code))
        except_blocks = len(re.findall(r'\bexcept\s+', code))
        null_checks = len(re.findall(r'(if\s+\w+\s+is\s+not\s+None|if\s+\w+\s*!=\s*null)', code, re.IGNORECASE))

        lines = [l for l in code.split('\n') if l.strip()]
        error_handling_ratio = (try_blocks + except_blocks + null_checks) / max(len(lines), 1)

        ai_score = 0.0
        if error_handling_ratio > 0.1:
            ai_score += 0.4
        elif error_handling_ratio > 0.05:
            ai_score += 0.2

        if try_blocks > 0 and except_blocks >= try_blocks:
            ai_score += 0.2

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'ai_indicators': ai_score,
            'try_blocks': try_blocks,
            'except_blocks': except_blocks,
            'null_checks': null_checks,
            'error_handling_ratio': round(error_handling_ratio, 3)
        }

    def _analyze_documentation(self, code: str) -> Dict[str, Any]:
        docstrings = re.findall(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', code)

        function_defs = len(re.findall(r'\bdef\s+\w+\s*\(', code))
        class_defs = len(re.findall(r'\bclass\s+\w+', code))

        documented_ratio = len(docstrings) / max(function_defs + class_defs, 1)

        avg_docstring_length = sum(len(d) for d in docstrings) / max(len(docstrings), 1) if docstrings else 0

        ai_score = 0.0
        if documented_ratio > 0.7:
            ai_score += 0.4
        elif documented_ratio > 0.4:
            ai_score += 0.2

        if avg_docstring_length > 100:
            ai_score += 0.3

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'ai_indicators': ai_score,
            'docstring_count': len(docstrings),
            'function_count': function_defs,
            'class_count': class_defs,
            'documented_ratio': round(documented_ratio, 3),
            'avg_docstring_length': round(avg_docstring_length, 2)
        }

    def _analyze_formatting(self, code: str) -> Dict[str, Any]:
        lines = [l for l in code.split('\n') if l.strip()]

        spacing_patterns = []
        for line in lines:
            if '=' in line and 'def' not in line and 'class' not in line:
                spacing_patterns.append('=' in line.replace('==', '').replace('!=', ''))

        operator_spacing = len(re.findall(r'\s[+\-*/=]\s', code))
        total_operators = len(re.findall(r'[+\-*/=]', code))
        spacing_consistency = operator_spacing / max(total_operators, 1)

        ai_score = 0.0
        if spacing_consistency > 0.9:
            ai_score += 0.5
        elif spacing_consistency > 0.7:
            ai_score += 0.3

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'ai_indicators': ai_score,
            'spacing_consistency': round(spacing_consistency, 3)
        }

    def _analyze_syntax_modernity(self, code: str) -> Dict[str, Any]:
        modern_features = 0
        legacy_features = 0

        modern_features += len(re.findall(r':\s*(str|int|float|bool|List|Dict)', code))
        modern_features += len(re.findall(r'\bf-["\']', code))
        modern_features += len(re.findall(r'\bawait\s+', code))
        modern_features += len(re.findall(r'\basync\s+def', code))
        modern_features += len(re.findall(r'\bwith\s+\w+', code))

        legacy_features += len(re.findall(r'\bvar\s+', code))
        legacy_features += len(re.findall(r'\.prototype\.', code))
        legacy_features += len(re.findall(r'%\s*[sd]', code))

        total_features = modern_features + legacy_features
        modern_ratio = modern_features / max(total_features, 1) if total_features > 0 else 0.5

        ai_score = modern_ratio

        return {
            'ai_indicators': ai_score,
            'modern_features': modern_features,
            'legacy_features': legacy_features,
            'modern_ratio': round(modern_ratio, 3)
        }

    # ==================== NEW ENHANCED DIMENSIONS ====================

    def _analyze_enhanced_comments(self, code: str) -> Dict[str, Any]:
        """Enhanced comment analysis for AI-typical patterns."""
        lines = code.split('\n')
        comment_lines = [l.strip() for l in lines if l.strip().startswith('#') or l.strip().startswith('//')]

        ai_phrases_found = []
        obvious_comments_found = []

        # Check for AI-typical phrases
        for comment in comment_lines:
            comment_lower = comment.lower()
            for phrase in self.ai_comment_phrases:
                if re.search(phrase, comment_lower):
                    ai_phrases_found.append(comment[:80])
                    break

        # Check for obvious comments
        for comment in comment_lines:
            for pattern, description in self.obvious_comment_patterns:
                if re.search(pattern, comment, re.IGNORECASE):
                    obvious_comments_found.append(f"{description}: {comment[:60]}")
                    break

        total_comments = len(comment_lines)
        ai_phrase_ratio = len(ai_phrases_found) / max(total_comments, 1)
        obvious_ratio = len(obvious_comments_found) / max(total_comments, 1)

        ai_score = 0.0
        if ai_phrase_ratio > 0.3:
            ai_score += 0.4
        elif ai_phrase_ratio > 0.15:
            ai_score += 0.2

        if obvious_ratio > 0.2:
            ai_score += 0.4
        elif obvious_ratio > 0.1:
            ai_score += 0.2

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'scores': {
                'ai_indicators': ai_score,
                'ai_phrase_count': len(ai_phrases_found),
                'obvious_comment_count': len(obvious_comments_found),
                'total_comments': total_comments,
                'ai_phrase_ratio': round(ai_phrase_ratio, 3),
                'obvious_ratio': round(obvious_ratio, 3)
            },
            'obvious_comments': obvious_comments_found[:10],
            'ai_phrases': ai_phrases_found[:10]
        }

    # pylint: disable=too-many-locals
    def _analyze_defensive_coding(self, code: str) -> Dict[str, Any]:
        """Detect excessive defensive coding patterns typical of AI."""
        patterns_found = []

        # Excessive null/None checks
        none_checks = re.findall(r'if\s+\w+\s+is\s+not\s+None', code)
        null_checks = re.findall(r'if\s+\w+\s*!=\s*null', code, re.IGNORECASE)
        none_check_count = len(none_checks) + len(null_checks)
        if none_check_count > 0:
            patterns_found.extend([f"None check: {c[:50]}" for c in none_checks[:3]])

        # Redundant type checking
        type_checks = re.findall(r'isinstance\s*\(\s*\w+\s*,\s*\w+\s*\)', code)
        type_check_count = len(type_checks)
        if type_check_count > 3:
            patterns_found.append(f"Excessive type checks: {type_check_count} isinstance calls")

        # Over-use of try-catch
        try_blocks = len(re.findall(r'\btry\s*:', code))
        simple_operations = len(re.findall(r'try\s*:\s*\n\s*\w+\s*=', code))
        if try_blocks > 3:
            patterns_found.append(f"Many try blocks: {try_blocks}")

        # Redundant assertions
        assertions = re.findall(r'assert\s+.+', code)
        assert_count = len(assertions)
        if assert_count > 2:
            patterns_found.append(f"Multiple assertions: {assert_count}")

        # Multiple validation of same condition
        if_conditions = re.findall(r'if\s+(.+?):', code)
        condition_counter = Counter(if_conditions)
        repeated_conditions = sum(1 for c, count in condition_counter.items() if count > 1)
        if repeated_conditions > 0:
            patterns_found.append(f"Repeated conditions: {repeated_conditions}")

        # Input validation patterns
        validation_patterns = len(re.findall(r'if\s+not\s+\w+\s*:', code))
        validation_patterns += len(re.findall(r'if\s+\w+\s+is\s+None\s*:', code))
        validation_patterns += len(re.findall(r'raise\s+(ValueError|TypeError|RuntimeError)', code))

        lines = [l for l in code.split('\n') if l.strip()]
        defensive_ratio = (none_check_count + type_check_count + try_blocks + validation_patterns) / max(len(lines), 1)

        ai_score = 0.0
        if defensive_ratio > 0.15:
            ai_score += 0.5
        elif defensive_ratio > 0.08:
            ai_score += 0.3
        elif defensive_ratio > 0.04:
            ai_score += 0.15

        if repeated_conditions > 2:
            ai_score += 0.2

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'scores': {
                'ai_indicators': ai_score,
                'none_checks': none_check_count,
                'type_checks': type_check_count,
                'try_blocks': try_blocks,
                'assertions': assert_count,
                'repeated_conditions': repeated_conditions,
                'defensive_ratio': round(defensive_ratio, 3)
            },
            'patterns': patterns_found[:10]
        }

    def _analyze_textbook_algorithms(self, code: str) -> Dict[str, Any]:
        """Detect textbook/standard algorithm implementations."""
        patterns_found = []
        textbook_count = 0

        for pattern, description in self.textbook_patterns:
            matches = re.findall(pattern, code)
            if matches:
                textbook_count += len(matches)
                patterns_found.append(description)

        # Verbose solutions detection
        verbose_indicators = 0

        # range(len()) instead of enumerate
        range_len = len(re.findall(r'range\s*\(\s*len\s*\(', code))
        if range_len > 0:
            verbose_indicators += range_len

        # Manual string concatenation instead of join
        string_concat = len(re.findall(r'\w+\s*\+=\s*["\']', code))
        if string_concat > 2:
            verbose_indicators += 1
            patterns_found.append("String concatenation in loop")

        # Manual list building instead of comprehension
        append_in_loop = len(re.findall(r'for\s+.+:\s*\n\s+\w+\.append\(', code, re.MULTILINE))
        if append_in_loop > 2:
            verbose_indicators += append_in_loop
            patterns_found.append(f"Append in loop ({append_in_loop}x) instead of comprehension")

        lines = len([l for l in code.split('\n') if l.strip()])
        textbook_ratio = textbook_count / max(lines, 1)

        ai_score = 0.0
        if textbook_count > 3:
            ai_score += 0.4
        elif textbook_count > 1:
            ai_score += 0.2

        if verbose_indicators > 2:
            ai_score += 0.3
        elif verbose_indicators > 0:
            ai_score += 0.1

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'scores': {
                'ai_indicators': ai_score,
                'textbook_pattern_count': textbook_count,
                'verbose_indicators': verbose_indicators,
                'textbook_ratio': round(textbook_ratio, 4)
            },
            'patterns': list(set(patterns_found))[:10]
        }

    # pylint: disable=too-many-locals
    def _analyze_over_modularization(self, code: str) -> Dict[str, Any]:
        """Detect over-modularization patterns typical of AI."""
        # Find all function definitions (handles multi-line and type hints)
        func_pattern = r'def\s+(\w+)\s*\('
        func_matches = list(re.finditer(func_pattern, code))

        small_functions = []
        function_sizes = []

        lines = code.split('\n')
        func_start_lines = []

        # Find line numbers for each function start
        for match in func_matches:
            line_num = code[:match.start()].count('\n')
            func_start_lines.append((match.group(1), line_num))

        for i, (func_name, start_line) in enumerate(func_start_lines):
            # Find end of function (next function or end of code)
            if i + 1 < len(func_start_lines):
                end_line = func_start_lines[i + 1][1]
            else:
                end_line = len(lines)

            func_body_lines = lines[start_line:end_line]
            # Count non-empty, non-comment lines (excluding the def line itself)
            func_lines = [l for l in func_body_lines[1:] if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('"""') and not l.strip().startswith("'''")]
            func_size = len(func_lines)
            function_sizes.append(func_size)

            if func_size < 5:
                small_functions.append(f"{func_name} ({func_size} lines)")

        total_functions = len(func_matches)
        small_func_count = len(small_functions)
        small_func_ratio = small_func_count / max(total_functions, 1)

        # Check for helper function naming patterns
        helper_patterns = ['_helper', '_util', '_process', '_handle', '_validate', '_check', '_get', '_set', '_create']
        helper_count = sum(1 for m in func_matches if any(p in m.group(1).lower() for p in helper_patterns))
        helper_ratio = helper_count / max(total_functions, 1)

        # Check for similar function patterns (repetitive structure)
        # func_signatures = [m.group(0) for m in func_matches]

        ai_score = 0.0
        if small_func_ratio > 0.5 and total_functions > 3:
            ai_score += 0.4
        elif small_func_ratio > 0.3 and total_functions > 2:
            ai_score += 0.2

        if helper_ratio > 0.4:
            ai_score += 0.3
        elif helper_ratio > 0.2:
            ai_score += 0.15

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'scores': {
                'ai_indicators': ai_score,
                'total_functions': total_functions,
                'small_function_count': small_func_count,
                'small_function_ratio': round(small_func_ratio, 3),
                'helper_function_count': helper_count,
                'helper_ratio': round(helper_ratio, 3),
                'avg_function_size': round(sum(function_sizes) / max(len(function_sizes), 1), 1)
            },
            'small_functions': small_functions[:10]
        }

    # pylint: disable=too-many-locals
    def _analyze_enhanced_consistency(self, code: str) -> Dict[str, Any]:
        """Detect perfect consistency that's unnatural for humans."""
        lines = [l for l in code.split('\n') if l.strip()]

        # Check naming consistency
        snake_case = len(re.findall(r'\b[a-z]+_[a-z]+\b', code))
        camel_case = len(re.findall(r'\b[a-z]+[A-Z][a-z]+\b', code))
        total_naming = snake_case + camel_case
        if total_naming > 5:
            naming_consistency = max(snake_case, camel_case) / max(total_naming, 1)
        else:
            naming_consistency = 0.5

        # Check spacing around operators
        spaced_ops = len(re.findall(r'\s[=+\-*/]\s', code))
        unspaced_ops = len(re.findall(r'[a-zA-Z0-9][=+\-*/][a-zA-Z0-9]', code))
        total_ops = spaced_ops + unspaced_ops
        if total_ops > 3:
            spacing_consistency = spaced_ops / max(total_ops, 1)
        else:
            spacing_consistency = 0.5

        # Check comment style consistency
        hash_comments = len(re.findall(r'^\s*#', code, re.MULTILINE))
        slash_comments = len(re.findall(r'^\s*//', code, re.MULTILINE))
        total_comments = hash_comments + slash_comments
        if total_comments > 2:
            comment_style_consistency = max(hash_comments, slash_comments) / max(total_comments, 1)
        else:
            comment_style_consistency = 0.5

        # Check indentation consistency (4 spaces vs tabs vs 2 spaces)
        indent_4 = len(re.findall(r'^\s{4}[^\s]', code, re.MULTILINE))
        indent_2 = len(re.findall(r'^\s{2}[^\s]', code, re.MULTILINE))
        indent_tab = len(re.findall(r'^\t[^\t]', code, re.MULTILINE))
        total_indent = indent_4 + indent_2 + indent_tab
        if total_indent > 3:
            indent_consistency = max(indent_4, indent_2, indent_tab) / max(total_indent, 1)
        else:
            indent_consistency = 0.5

        # Perfect consistency is suspicious
        perfect_count = sum([
            1 if naming_consistency > 0.95 and total_naming > 10 else 0,
            1 if spacing_consistency > 0.98 and total_ops > 10 else 0,
            1 if comment_style_consistency > 0.98 and total_comments > 5 else 0,
            1 if indent_consistency > 0.98 and total_indent > 10 else 0
        ])

        ai_score = 0.0
        if perfect_count >= 3:
            ai_score += 0.6
        elif perfect_count >= 2:
            ai_score += 0.4
        elif perfect_count >= 1:
            ai_score += 0.2

        # Also add partial score for high consistency
        avg_consistency = (naming_consistency + spacing_consistency +
                           comment_style_consistency + indent_consistency) / 4
        if avg_consistency > 0.9:
            ai_score += 0.2

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'ai_indicators': ai_score,
            'naming_consistency': round(naming_consistency, 3),
            'spacing_consistency': round(spacing_consistency, 3),
            'comment_style_consistency': round(comment_style_consistency, 3),
            'indent_consistency': round(indent_consistency, 3),
            'perfect_consistency_count': perfect_count
        }

    def _analyze_contextual_quirks(self, code: str) -> Dict[str, Any]:
        """Detect absence of human contextual quirks."""
        missing_quirks = []

        # Check for absence of TODO, FIXME, HACK, NOTE, XXX
        has_todo = bool(re.search(r'(#|//)\s*(TODO|FIXME|HACK|NOTE|XXX)', code, re.IGNORECASE))
        if not has_todo:
            missing_quirks.append("No TODO/FIXME/HACK/NOTE/XXX comments")

        # Check for absence of temp variable names
        has_temp_vars = bool(re.search(r'\b(tmp|temp|foo|bar|baz|xxx|yyy|zzz)\b', code))
        if not has_temp_vars:
            missing_quirks.append("No temporary variable names (tmp, temp, foo, bar)")

        # Check for absence of debugging artifacts
        has_debug = bool(re.search(r'(console\.log|print\s*\(|debugger|System\.out\.print)', code))
        if not has_debug:
            missing_quirks.append("No debugging statements (print, console.log)")

        # Check for absence of commented-out code
        commented_code = re.findall(r'#\s*(if|for|while|def|class|return|import)\s', code)
        commented_code += re.findall(r'//\s*(if|for|while|function|class|return|import)\s', code)
        if not commented_code:
            missing_quirks.append("No commented-out code")

        # Check for absence of magic numbers with comments
        magic_with_comment = re.findall(r'\d+\s*#', code)
        if not magic_with_comment:
            missing_quirks.append("No magic numbers with inline comments")

        # Check for presence of abbreviations
        has_abbrevs = bool(re.search(r'\b(cfg|ctx|env|msg|req|res|db|api|btn|img|err|fmt)\b', code))
        if not has_abbrevs:
            missing_quirks.append("No common abbreviations (cfg, ctx, env, msg, etc.)")

        lines = len([l for l in code.split('\n') if l.strip()])
        quirk_checks = 6
        missing_count = len(missing_quirks)

        # More missing quirks = more likely AI
        ai_score = 0.0
        if lines > 30:  # Only penalize for substantial code
            missing_ratio = missing_count / quirk_checks
            if missing_ratio > 0.8:
                ai_score += 0.5
            elif missing_ratio > 0.6:
                ai_score += 0.3
            elif missing_ratio > 0.4:
                ai_score += 0.15

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'scores': {
                'ai_indicators': ai_score,
                'missing_quirk_count': missing_count,
                'total_quirk_checks': quirk_checks,
                'has_todo_fixme': has_todo,
                'has_temp_vars': has_temp_vars,
                'has_debug_statements': has_debug,
                'has_commented_code': bool(commented_code)
            },
            'missing': missing_quirks
        }

    # pylint: disable=too-many-locals
    def _analyze_formatting_perfection(self, code: str) -> Dict[str, Any]:
        """Detect perfect formatting that's unnatural for humans."""
        lines = code.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]

        # Check indentation perfection (all 4-space aligned)
        indented_lines = [l for l in non_empty_lines if len(l) - len(l.lstrip()) > 0]
        perfect_indent = sum(1 for l in indented_lines if (len(l) - len(l.lstrip())) % 4 == 0)
        indent_perfection = perfect_indent / max(len(indented_lines), 1)

        # Check line length consistency
        line_lengths = [len(l.rstrip()) for l in non_empty_lines]
        if line_lengths:
            avg_length = sum(line_lengths) / len(line_lengths)
            length_variance = sum((l - avg_length) ** 2 for l in line_lengths) / len(line_lengths)
            length_std = length_variance ** 0.5
            # Low std dev indicates very consistent line lengths
            length_consistency = 1.0 if length_std < 15 else (1.0 - min(length_std / 50, 1.0))
        else:
            length_consistency = 0.5

        # Check for 100% consistent trailing whitespace (none)
        trailing_space = sum(1 for l in lines if l.rstrip() != l and l.strip())
        no_trailing_space = trailing_space == 0

        # Check blank line patterns (consistent separation)
        blank_lines = [i for i, l in enumerate(lines) if not l.strip()]
        if len(blank_lines) > 2:
            blank_gaps = [blank_lines[i+1] - blank_lines[i] for i in range(len(blank_lines)-1)]
            if blank_gaps:
                gap_mean = sum(blank_gaps) / len(blank_gaps)
                gap_variance = sum((g - gap_mean)**2 for g in blank_gaps) / len(blank_gaps)
            else:
                gap_variance = 0

            blank_line_regularity = 1.0 if gap_variance < 5 else (1.0 - min(gap_variance / 20, 1.0))
        else:
            blank_line_regularity = 0.5

        perfection_count = sum([
            1 if indent_perfection > 0.98 else 0,
            1 if length_consistency > 0.85 else 0,
            1 if no_trailing_space else 0,
            1 if blank_line_regularity > 0.8 else 0
        ])

        ai_score = 0.0
        if perfection_count >= 4:
            ai_score += 0.6
        elif perfection_count >= 3:
            ai_score += 0.4
        elif perfection_count >= 2:
            ai_score += 0.2

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'ai_indicators': ai_score,
            'indent_perfection': round(indent_perfection, 3),
            'line_length_consistency': round(length_consistency, 3),
            'no_trailing_whitespace': no_trailing_space,
            'blank_line_regularity': round(blank_line_regularity, 3),
            'perfection_count': perfection_count
        }

    def _analyze_obvious_comments(self, code: str) -> Dict[str, Any]:
        """Specifically detect obvious/redundant comments."""
        lines = code.split('\n')
        obvious_examples = []
        obvious_count = 0
        total_comments = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                total_comments += 1
                comment_text = stripped.lstrip('#').lstrip('/').strip().lower()

                # Check for obvious patterns
                obvious_patterns = [
                    (r'^increment', 'Increment statement'),
                    (r'^decrement', 'Decrement statement'),
                    (r'^initialize', 'Initialize statement'),
                    (r'^set\s+\w+\s+to', 'Set variable'),
                    (r'^return\s+(the\s+)?result', 'Return statement'),
                    (r'^return\s+(the\s+)?value', 'Return statement'),
                    (r'^loop\s+through', 'Loop statement'),
                    (r'^iterate\s+over', 'Loop statement'),
                    (r'^check\s+if', 'Condition check'),
                    (r'^verify\s+that', 'Verification'),
                    (r'^create\s+(a\s+)?new', 'Object creation'),
                    (r'^add\s+.+\s+to', 'Add operation'),
                    (r'^remove\s+.+\s+from', 'Remove operation'),
                    (r'^update\s+(the\s+)?', 'Update operation'),
                    (r'^get\s+(the\s+)?', 'Get operation'),
                    (r'^call\s+(the\s+)?', 'Function call'),
                    (r'^import\s+', 'Import statement'),
                    (r'^define\s+', 'Definition'),
                    (r'^assign\s+', 'Assignment'),
                    (r'^the\s+\w+\s+should', 'Test assertion comment'),
                    (r'^test\s+that', 'Test description'),
                    (r'^this\s+test', 'Test description'),
                    (r'^ensure\s+that', 'Validation comment'),
                    (r'^make\s+sure', 'Validation comment'),
                    (r'^should\s+be\s+', 'Expectation comment'),
                    (r'^should\s+have\s+', 'Expectation comment'),
                    (r'^should\s+contain', 'Expectation comment'),
                ]

                for pattern, description in obvious_patterns:
                    if re.search(pattern, comment_text):
                        obvious_count += 1
                        obvious_examples.append(f"[Line {i+1}] {description}: {stripped[:70]}")
                        break

        obvious_ratio = obvious_count / max(total_comments, 1)

        ai_score = 0.0
        if obvious_ratio > 0.4:
            ai_score += 0.6
        elif obvious_ratio > 0.25:
            ai_score += 0.4
        elif obvious_ratio > 0.15:
            ai_score += 0.2
        elif obvious_ratio > 0.08:
            ai_score += 0.1

        ai_score = max(0.0, min(1.0, ai_score))

        return {
            'scores': {
                'ai_indicators': ai_score,
                'obvious_comment_count': obvious_count,
                'total_comments': total_comments,
                'obvious_ratio': round(obvious_ratio, 3)
            },
            'examples': obvious_examples[:15]
        }

    def _calculate_confidence(self, scores: Dict[str, Dict]) -> str:
        score_values = []
        for s in scores.values():
            if isinstance(s, dict) and 'ai_indicators' in s:
                score_values.append(s['ai_indicators'])

        if not score_values:
            return "LOW"

        mean_score = sum(score_values) / len(score_values)
        variance = sum((x - mean_score)**2 for x in score_values) / len(score_values)

        # Count how many dimensions agree
        high_ai = sum(1 for s in score_values if s > 0.5)
        low_ai = sum(1 for s in score_values if s < 0.3)
        agreement = max(high_ai, low_ai) / len(score_values)

        if variance < 0.04 and agreement > 0.6:
            return "HIGH"
        elif variance < 0.08 and agreement > 0.5:
            return "MEDIUM-HIGH"
        elif variance < 0.15:
            return "MEDIUM"
        else:
            return "LOW"

    # pylint: disable=too-many-branches
    def _determine_verdict(self, ai_score: float, confidence: str, scores: Dict[str, Dict]) -> str:
        # Count strong AI indicators
        strong_ai_indicators = 0
        if scores.get('obvious_comments', {}).get('ai_indicators', 0) > 0.4:
            strong_ai_indicators += 1
        if scores.get('enhanced_comment_analysis', {}).get('ai_indicators', 0) > 0.4:
            strong_ai_indicators += 1
        if scores.get('perfect_consistency', {}).get('ai_indicators', 0) > 0.4:
            strong_ai_indicators += 1
        if scores.get('contextual_quirks', {}).get('ai_indicators', 0) > 0.4:
            strong_ai_indicators += 1
        if scores.get('formatting_perfection', {}).get('ai_indicators', 0) > 0.4:
            strong_ai_indicators += 1
        if scores.get('defensive_coding', {}).get('ai_indicators', 0) > 0.4:
            strong_ai_indicators += 1

        if confidence == "LOW":
            return "INCONCLUSIVE - Manual review recommended"

        # Enhanced verdict logic
        if ai_score > 0.70 or (ai_score > 0.55 and strong_ai_indicators >= 4):
            return "HIGHLY LIKELY AI-GENERATED"
        elif ai_score > 0.55 or (ai_score > 0.45 and strong_ai_indicators >= 3):
            return "LIKELY AI-GENERATED"
        elif ai_score > 0.45 or (ai_score > 0.35 and strong_ai_indicators >= 2):
            return "POSSIBLY AI-ASSISTED"
        elif ai_score > 0.30:
            return "MIXED INDICATORS"
        else:
            return "LIKELY HUMAN-WRITTEN"

    # pylint: disable=too-many-locals, too-many-branches
    def _extract_key_indicators(self, scores: Dict[str, Dict], detected_patterns: Dict[str, List]) -> Dict[str, Any]:
        indicators = {}

        # Original indicators
        if scores['naming_analysis'].get('avg_identifier_length', 0) > 10:
            indicators['verbose_naming'] = True

        if scores['comment_analysis'].get('comment_ratio', 0) > 0.25:
            indicators['high_documentation'] = True

        if scores['structure_analysis'].get('indent_consistency', 0) > 0.9:
            indicators['perfect_formatting'] = True

        if scores['error_handling'].get('error_handling_ratio', 0) > 0.08:
            indicators['comprehensive_error_handling'] = True

        if scores['modern_syntax'].get('modern_ratio', 0) > 0.8:
            indicators['modern_syntax_heavy'] = True

        # New indicators
        enhanced_comments = scores.get('enhanced_comment_analysis', {})
        if enhanced_comments.get('ai_phrase_ratio', 0) > 0.2:
            indicators['ai_typical_comment_phrases'] = True

        if enhanced_comments.get('obvious_ratio', 0) > 0.15:
            indicators['obvious_comments_detected'] = True

        defensive = scores.get('defensive_coding', {})
        if defensive.get('defensive_ratio', 0) > 0.1:
            indicators['excessive_defensive_coding'] = True

        textbook = scores.get('textbook_algorithms', {})
        if textbook.get('textbook_pattern_count', 0) > 2:
            indicators['textbook_implementations'] = True

        modular = scores.get('over_modularization', {})
        if modular.get('small_function_ratio', 0) > 0.4:
            indicators['over_modularized'] = True

        consistency = scores.get('perfect_consistency', {})
        if consistency.get('perfect_consistency_count', 0) >= 2:
            indicators['unnaturally_perfect_consistency'] = True

        quirks = scores.get('contextual_quirks', {})
        if quirks.get('missing_quirk_count', 0) >= 4:
            indicators['lacks_human_quirks'] = True

        formatting = scores.get('formatting_perfection', {})
        if formatting.get('perfection_count', 0) >= 3:
            indicators['flawless_formatting'] = True

        obvious = scores.get('obvious_comments', {})
        if obvious.get('obvious_ratio', 0) > 0.2:
            indicators['explains_obvious_code'] = True

        # Add examples of detected patterns
        if detected_patterns.get('obvious_comment_examples'):
            indicators['obvious_comment_examples'] = detected_patterns['obvious_comment_examples'][:5]

        if detected_patterns.get('ai_phrases'):
            indicators['ai_phrase_examples'] = detected_patterns['ai_phrases'][:5]

        if detected_patterns.get('textbook_patterns'):
            indicators['textbook_pattern_examples'] = detected_patterns['textbook_patterns'][:5]

        if detected_patterns.get('defensive_patterns'):
            indicators['defensive_pattern_examples'] = detected_patterns['defensive_patterns'][:5]

        if detected_patterns.get('small_functions'):
            indicators['small_function_examples'] = detected_patterns['small_functions'][:5]

        if detected_patterns.get('missing_quirks'):
            indicators['missing_human_quirks'] = detected_patterns['missing_quirks']

        return indicators


# pylint: disable=duplicate-code, too-many-locals, too-many-branches, too-many-statements
def generate_html_report(results: List[DetectionResult], output_path: str, title: str = "AI Code Detection Report"):
    """
    Generate a professional HTML report with all analysis results.

    Args:
        results: List of DetectionResult objects
        output_path: Path to save the HTML report
        title: Title for the report
    """
    from datetime import datetime

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

    def get_probability_color(prob):
        if prob >= 75:
            return '#dc3545'  # Red
        elif prob >= 55:
            return '#fd7e14'  # Orange
        elif prob >= 35:
            return '#ffc107'  # Yellow
        else:
            return '#28a745'  # Green

    def get_probability_class(prob):
        if prob >= 75:
            return 'red'
        elif prob >= 55:
            return 'orange'
        elif prob >= 35:
            return 'yellow'
        else:
            return 'green'

    def get_probability_label(prob):
        if prob >= 75:
            return 'Likely AI-Generated'
        elif prob >= 55:
            return 'Possibly AI-Assisted'
        elif prob >= 35:
            return 'Mixed Indicators'
        else:
            return 'Likely Human'

    # Generate file cards HTML
    file_cards_html = ""
    sorted_results = sorted(valid_results, key=lambda x: x.ai_probability, reverse=True)

    for idx, result in enumerate(sorted_results):
        color = get_probability_color(result.ai_probability)
        color_class = get_probability_class(result.ai_probability)
        prob_label = get_probability_label(result.ai_probability)

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
                score_color = get_probability_color(score_pct)
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
                    <h5>{pattern_icon} {pattern_name}</h5>
                    <ul class="pattern-list">'''
                for p in patterns:
                    escaped_p = str(p).replace('<', '&lt;').replace('>', '&gt;')
                    patterns_html += f'<li>{escaped_p}</li>'
                patterns_html += '</ul></div>'

        # Generate indicators HTML
        indicators_html = ""
        boolean_indicators = {k: v for k, v in result.indicators.items() if isinstance(v, bool) and v}
        if boolean_indicators:
            indicators_html = '<div class="indicators-list">'
            for key in boolean_indicators:
                indicator_name = key.replace('_', ' ').title()
                indicators_html += f'<span class="indicator-badge">{indicator_name}</span>'
            indicators_html += '</div>'

        file_cards_html += f'''
        <div class="file-card" id="file-{idx}">
            <div class="file-header">
                <div class="file-info">
                    <h3 class="file-path">📄 {result.file_path}</h3>
                    <span class="verdict-badge {color_class}">{result.verdict}</span>
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
                    <div class="stat-value {get_probability_class(avg_ai_prob)}">{avg_ai_prob:.1f}%</div>
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
    <title>{title}</title>
    <style>
        :root {{
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
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}

        h1 {{
            font-size: 2.2em;
            margin-bottom: 10px;
            color: #fff;
        }}

        .meta {{
            color: var(--text-secondary);
            font-size: 0.9em;
        }}

        .meta span {{
            margin-right: 20px;
        }}

        /* Summary Section */
        .summary-section {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .summary-section h2 {{
            color: #fff;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.1);
        }}

        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}

        .stat-card {{
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}

        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #fff;
        }}

        .stat-value.green {{ color: var(--color-green); }}
        .stat-value.yellow {{ color: var(--color-yellow); }}
        .stat-value.orange {{ color: var(--color-orange); }}
        .stat-value.red {{ color: var(--color-red); }}

        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .distribution-section h3 {{
            margin-bottom: 15px;
            color: #fff;
        }}

        .distribution-bar {{
            display: flex;
            height: 35px;
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
            min-width: 2px;
        }}

        .dist-segment.green {{ background: var(--color-green); }}
        .dist-segment.yellow {{ background: var(--color-yellow); color: #333; }}
        .dist-segment.orange {{ background: var(--color-orange); }}
        .dist-segment.red {{ background: var(--color-red); }}

        .distribution-legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }}

        .distribution-legend span {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.9em;
        }}

        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 3px;
        }}

        .legend-dot.green {{ background: var(--color-green); }}
        .legend-dot.yellow {{ background: var(--color-yellow); }}
        .legend-dot.orange {{ background: var(--color-orange); }}
        .legend-dot.red {{ background: var(--color-red); }}

        /* File Cards */
        .file-card {{
            background: var(--bg-card);
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .file-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }}

        .file-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 20px;
            background: rgba(0,0,0,0.2);
            flex-wrap: wrap;
            gap: 15px;
        }}

        .file-info {{
            flex: 1;
            min-width: 250px;
        }}

        .file-path {{
            font-size: 1.1em;
            color: #fff;
            margin-bottom: 10px;
            word-break: break-all;
            font-family: 'Monaco', 'Consolas', monospace;
        }}

        .verdict-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}

        .verdict-badge.green {{ background: rgba(40, 167, 69, 0.2); color: var(--color-green); border: 1px solid var(--color-green); }}
        .verdict-badge.yellow {{ background: rgba(255, 193, 7, 0.2); color: var(--color-yellow); border: 1px solid var(--color-yellow); }}
        .verdict-badge.orange {{ background: rgba(253, 126, 20, 0.2); color: var(--color-orange); border: 1px solid var(--color-orange); }}
        .verdict-badge.red {{ background: rgba(220, 53, 69, 0.2); color: var(--color-red); border: 1px solid var(--color-red); }}

        .file-summary {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .probability-circle {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border: 3px solid;
        }}

        .probability-circle.green {{ border-color: var(--color-green); background: rgba(40, 167, 69, 0.1); }}
        .probability-circle.yellow {{ border-color: var(--color-yellow); background: rgba(255, 193, 7, 0.1); }}
        .probability-circle.orange {{ border-color: var(--color-orange); background: rgba(253, 126, 20, 0.1); }}
        .probability-circle.red {{ border-color: var(--color-red); background: rgba(220, 53, 69, 0.1); }}

        .prob-value {{
            font-size: 1.3em;
            font-weight: bold;
        }}

        .probability-circle.green .prob-value {{ color: var(--color-green); }}
        .probability-circle.yellow .prob-value {{ color: var(--color-yellow); }}
        .probability-circle.orange .prob-value {{ color: var(--color-orange); }}
        .probability-circle.red .prob-value {{ color: var(--color-red); }}

        .prob-label {{
            font-size: 0.75em;
            color: var(--text-secondary);
        }}

        .confidence-badge {{
            background: rgba(255,255,255,0.1);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85em;
        }}

        .file-details {{
            padding: 20px;
            display: none;
        }}

        .file-details.visible {{
            display: block;
        }}

        .details-section {{
            margin-bottom: 25px;
        }}

        .details-section h4 {{
            color: #fff;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}

        .dimensions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 10px;
        }}

        .dimension-item {{
            display: flex;
            align-items: center;
            padding: 10px;
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
        }}

        .dim-icon {{
            font-size: 1.1em;
            margin-right: 10px;
            width: 24px;
            text-align: center;
        }}

        .dim-name {{
            flex: 1;
            font-size: 0.9em;
            min-width: 100px;
        }}

        .dim-bar-container {{
            width: 80px;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin: 0 10px;
        }}

        .dim-bar {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
        }}

        .dim-score {{
            font-weight: bold;
            font-size: 0.9em;
            width: 45px;
            text-align: right;
        }}

        .pattern-category {{
            margin-bottom: 15px;
        }}

        .pattern-category h5 {{
            color: var(--text-secondary);
            margin-bottom: 8px;
            font-size: 0.95em;
        }}

        .pattern-list {{
            list-style: none;
            padding-left: 10px;
        }}

        .pattern-list li {{
            padding: 6px 10px;
            background: rgba(0,0,0,0.15);
            border-radius: 4px;
            margin-bottom: 5px;
            font-size: 0.85em;
            font-family: 'Monaco', 'Consolas', monospace;
            word-break: break-all;
            border-left: 3px solid var(--accent-purple);
        }}

        .indicators-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .indicator-badge {{
            background: rgba(83, 52, 131, 0.3);
            border: 1px solid var(--accent-purple);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
        }}

        .toggle-details {{
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
        }}

        .toggle-details:hover {{
            background: rgba(255,255,255,0.1);
        }}

        .expand-icon {{
            transition: transform 0.2s;
        }}

        .toggle-details.expanded .expand-icon {{
            transform: rotate(180deg);
        }}

        footer {{
            text-align: center;
            padding: 25px;
            color: var(--text-secondary);
            margin-top: 30px;
        }}

        /* Print styles */
        @media print {{
            body {{
                background: #fff;
                color: #333;
                padding: 10px;
            }}

            header {{
                background: #f5f5f5;
                color: #333;
            }}

            h1, h2, h3, h4 {{
                color: #333;
            }}

            .file-card {{
                border: 1px solid #ddd;
                break-inside: avoid;
            }}

            .file-details {{
                display: block !important;
            }}

            .toggle-details {{
                display: none;
            }}
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            h1 {{ font-size: 1.6em; }}

            .file-header {{
                flex-direction: column;
            }}

            .file-summary {{
                width: 100%;
                justify-content: flex-start;
            }}

            .dimensions-grid {{
                grid-template-columns: 1fr;
            }}

            .summary-stats {{
                grid-template-columns: 1fr 1fr;
            }}
        }}

        /* Scrollable sections */
        .scrollable {{
            max-height: 400px;
            overflow-y: auto;
            padding-right: 10px;
        }}

        .scrollable::-webkit-scrollbar {{
            width: 6px;
        }}

        .scrollable::-webkit-scrollbar-track {{
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
        }}

        .scrollable::-webkit-scrollbar-thumb {{
            background: rgba(255,255,255,0.3);
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 {title}</h1>
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


def main():
    parser = argparse.ArgumentParser(
        description='AI Code Detector - Analyze code to detect AI generation patterns (Enhanced Version)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic analysis:
    python ai_code_detector.py script.py
    python ai_code_detector.py --directory ./src

  Output formats:
    python ai_code_detector.py script.py --format detailed
    python ai_code_detector.py script.py --output results.json

  HTML reports:
    python ai_code_detector.py script.py --html
    python ai_code_detector.py script.py --html --html-output report.html
    python ai_code_detector.py --directory ./src --html --html-output analysis.html

  Combined outputs:
    python ai_code_detector.py file1.py file2.py --output results.json --html
        """
    )

    parser.add_argument('files', nargs='*', help='Code files to analyze')
    parser.add_argument('-d', '--directory', help='Analyze all code files in directory')
    parser.add_argument('-o', '--output', help='Output results to JSON file')
    parser.add_argument('-f', '--format', choices=['summary', 'detailed'],
                       default='summary', help='Output format for console (default: summary)')
    parser.add_argument('--extensions', default='.py,.js,.java,.cpp,.c,.php,.rb,.go,.ts',
                       help='File extensions to analyze (comma-separated)')
    parser.add_argument('--html', action='store_true',
                       help='Generate HTML report')
    parser.add_argument('--html-output', metavar='FILE',
                       help='HTML output file path (default: analysis_report.html)')

    args = parser.parse_args()

    detector = AICodeDetector()
    files_to_analyze = []

    if args.directory:
        extensions = tuple(args.extensions.split(','))
        for ext in extensions:
            files_to_analyze.extend(Path(args.directory).rglob(f'*{ext}'))

    if args.files:
        files_to_analyze.extend([Path(f) for f in args.files])

    if not files_to_analyze:
        parser.print_help()
        sys.exit(1)

    results = []
    for file_path in files_to_analyze:
        result = detector.analyze_file(str(file_path))
        results.append(result)

        if args.format == 'summary':
            print(f"\n{'='*80}")
            print(f"File: {result.file_path}")
            print(f"{'='*80}")
            print(f"AI Probability:    {result.ai_probability}%")
            print(f"Human Probability: {result.human_probability}%")
            print(f"Confidence:        {result.confidence}")
            print(f"Verdict:           {result.verdict}")
            if result.indicators:
                print(f"\n📊 Key Indicators:")
                for key, value in result.indicators.items():
                    if isinstance(value, list):
                        print(f"  • {key.replace('_', ' ').title()}:")
                        for item in value[:5]:
                            print(f"      - {item}")
                    elif isinstance(value, bool):
                        if value:
                            print(f"  • {key.replace('_', ' ').title()}")
                    else:
                        print(f"  • {key.replace('_', ' ').title()}: {value}")
        else:
            print(f"\n{'='*80}")
            print(f"DETAILED ANALYSIS: {result.file_path}")
            print(f"{'='*80}")
            print(f"AI Probability:    {result.ai_probability}%")
            print(f"Human Probability: {result.human_probability}%")
            print(f"Confidence:        {result.confidence}")
            print(f"Verdict:           {result.verdict}")
            print(f"\n{'─'*80}")
            print("📈 DIMENSION SCORES:")
            print(f"{'─'*80}")

            # Group scores by category
            original_dims = ['naming_analysis', 'comment_analysis', 'structure_analysis',
                           'complexity_analysis', 'error_handling', 'documentation',
                           'formatting_consistency', 'modern_syntax']
            new_dims = ['enhanced_comment_analysis', 'defensive_coding', 'textbook_algorithms',
                       'over_modularization', 'perfect_consistency', 'contextual_quirks',
                       'formatting_perfection', 'obvious_comments']

            print("\n  📁 ORIGINAL DIMENSIONS:")
            for category in original_dims:
                if category in result.detailed_scores:
                    scores = result.detailed_scores[category]
                    print(f"\n    {category.replace('_', ' ').title()}:")
                    for metric, value in scores.items():
                        print(f"      {metric}: {value}")

            print(f"\n  {'─'*76}")
            print("  🆕 ENHANCED DIMENSIONS:")
            for category in new_dims:
                if category in result.detailed_scores:
                    scores = result.detailed_scores[category]
                    print(f"\n    {category.replace('_', ' ').title()}:")
                    for metric, value in scores.items():
                        if not isinstance(value, (list, dict)):
                            print(f"      {metric}: {value}")

            if result.detected_patterns:
                print(f"\n{'─'*80}")
                print("🔍 DETECTED PATTERNS:")
                print(f"{'─'*80}")
                for pattern_type, patterns in result.detected_patterns.items():
                    if patterns:
                        print(f"\n  {pattern_type.replace('_', ' ').title()}:")
                        for p in patterns[:8]:
                            print(f"    • {p}")

            if result.indicators:
                print(f"\n{'─'*80}")
                print("🎯 KEY INDICATORS:")
                print(f"{'─'*80}")
                for key, value in result.indicators.items():
                    if isinstance(value, list):
                        print(f"\n  {key.replace('_', ' ').title()}:")
                        for item in value[:5]:
                            print(f"    • {item}")
                    elif isinstance(value, bool):
                        if value:
                            print(f"  ✓ {key.replace('_', ' ').title()}")
                    else:
                        print(f"  • {key.replace('_', ' ').title()}: {value}")

    # JSON output
    if args.output:
        output_data = [asdict(r) for r in results]
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\n\nJSON results saved to: {args.output}")

    # HTML report generation
    if args.html or args.html_output:
        html_path = args.html_output if args.html_output else 'analysis_report.html'

        # Generate a title based on input
        if args.directory:
            title = f"AI Code Detection Report - {Path(args.directory).name}"
        elif len(files_to_analyze) == 1:
            title = f"AI Code Detection Report - {files_to_analyze[0].name}"
        else:
            title = "AI Code Detection Report"

        generate_html_report(results, html_path, title)

    print(f"\n{'='*80}")
    print(f"Analysis Complete - {len(results)} file(s) processed")
    print(f"Dimensions analyzed: 16 (8 original + 8 enhanced)")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
