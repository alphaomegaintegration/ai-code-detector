import unittest
from ai_code_detector import AICodeDetector

class TestDefensiveCoding(unittest.TestCase):
    def setUp(self):
        self.detector = AICodeDetector()

    def test_empty_code(self):
        result = self.detector._analyze_defensive_coding("")
        self.assertEqual(result['scores']['none_checks'], 0)
        self.assertEqual(result['scores']['type_checks'], 0)
        self.assertEqual(result['scores']['ai_indicators'], 0.0)
        self.assertEqual(result['patterns'], [])

    def test_no_defensive_patterns(self):
        code = "print('Hello, World!')\nx = 1 + 2\n"
        result = self.detector._analyze_defensive_coding(code)
        self.assertEqual(result['scores']['none_checks'], 0)
        self.assertEqual(result['scores']['type_checks'], 0)
        self.assertEqual(result['scores']['ai_indicators'], 0.0)

    def test_none_checks(self):
        code = """
if x is not None:
    pass
if y is not None:
    pass
if z != null:
    pass
if a != NULL:
    pass
"""
        result = self.detector._analyze_defensive_coding(code)
        self.assertEqual(result['scores']['none_checks'], 4)
        self.assertTrue(any("None check:" in p for p in result['patterns']))

    def test_excessive_type_checks(self):
        code = """
isinstance(x, int)
isinstance(y, str)
isinstance(z, list)
isinstance(a, dict)
"""
        result = self.detector._analyze_defensive_coding(code)
        self.assertEqual(result['scores']['type_checks'], 4)
        self.assertIn("Excessive type checks: 4 isinstance calls", result['patterns'])

    def test_many_try_blocks(self):
        code = """
try:
    do_something()
except:
    pass
try:
    do_something_else()
except:
    pass
try:
    third_thing()
except:
    pass
try:
    fourth_thing()
except:
    pass
"""
        result = self.detector._analyze_defensive_coding(code)
        self.assertEqual(result['scores']['try_blocks'], 4)
        self.assertIn("Many try blocks: 4", result['patterns'])

    def test_multiple_assertions(self):
        code = """
assert x > 0
assert y is not None
assert len(z) == 10
"""
        result = self.detector._analyze_defensive_coding(code)
        self.assertEqual(result['scores']['assertions'], 3)
        self.assertIn("Multiple assertions: 3", result['patterns'])

    def test_repeated_conditions(self):
        code = """
if x > 0:
    pass
if x > 0:
    pass
"""
        result = self.detector._analyze_defensive_coding(code)
        self.assertEqual(result['scores']['repeated_conditions'], 1)
        self.assertIn("Repeated conditions: 1", result['patterns'])

    def test_ai_score_high_defensive_ratio(self):
        # High ratio should trigger ai_indicators score
        # lines = 10
        # defensive constructs: 4 (none_checks) + 0 + 0 + 0 = 4
        # ratio = 4/10 = 0.4 > 0.15 => ai_score = 0.5
        code = """
if a is not None: pass
if b is not None: pass
if c is not None: pass
if d is not None: pass
# filler
# filler
# filler
# filler
# filler
# filler
"""
        result = self.detector._analyze_defensive_coding(code)
        self.assertGreaterEqual(result['scores']['ai_indicators'], 0.5)

    def test_validation_patterns(self):
        code = """
if not x:
    raise ValueError("Missing x")
if y is None:
    raise TypeError("y is None")
raise RuntimeError("Something went wrong")
"""
        result = self.detector._analyze_defensive_coding(code)
        # validation_patterns = 1 (if not x) + 1 (if y is None) + 3 (raises) = 5
        # We can't directly see validation_patterns in the result,
        # but it affects defensive_ratio and ai_indicators.
        # none_checks = 0 (only 'is not None' and '!= null' are counted in none_checks)
        self.assertEqual(result['scores']['none_checks'], 0)
        # But defensive_ratio should include them
        # lines = 6
        # ratio = (0 + 0 + 0 + 5) / 6 = 0.833
        self.assertGreater(result['scores']['defensive_ratio'], 0.5)

if __name__ == '__main__':
    unittest.main()
