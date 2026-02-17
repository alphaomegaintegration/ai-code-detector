"""
Unit tests for AICodeDetector
"""
import unittest
import os
import tempfile
from ai_code_detector import AICodeDetector

class TestAICodeDetector(unittest.TestCase):
    """Test suite for AICodeDetector class"""

    def setUp(self):
        # Create a temporary directory
        # pylint: disable=consider-using-with
        self.test_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.test_dir.cleanup)

    def create_file(self, filename, content):
        """Helper to create a test file"""
        path = os.path.join(self.test_dir.name, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path

    def test_small_file(self):
        """Test analyzing a file within the size limit"""
        detector = AICodeDetector(max_file_size=1024)  # 1KB limit
        path = self.create_file('small.py', 'print("hello")')
        result = detector.analyze_file(path)
        self.assertNotEqual(result.confidence, "ERROR")

    def test_large_file(self):
        """Test analyzing a file exceeding the size limit"""
        detector = AICodeDetector(max_file_size=10)  # 10 bytes limit
        path = self.create_file('large.py', 'print("hello world")') # > 10 bytes
        result = detector.analyze_file(path)
        self.assertEqual(result.confidence, "ERROR")
        self.assertIn("File size exceeds limit", result.indicators.get('error', ''))

    def test_custom_limit(self):
        """Test configuring the limit"""
        detector = AICodeDetector(max_file_size=50)
        path = self.create_file('medium.py', 'x = ' + 'a'*40) # 44 bytes approx
        result = detector.analyze_file(path)
        self.assertNotEqual(result.confidence, "ERROR")

        detector2 = AICodeDetector(max_file_size=10)
        result2 = detector2.analyze_file(path)
        self.assertEqual(result2.confidence, "ERROR")

    def test_default_limit(self):
        """Test default limit (1MB)"""
        detector = AICodeDetector()
        self.assertEqual(detector.max_file_size, 1024 * 1024)

if __name__ == '__main__':
    unittest.main()
