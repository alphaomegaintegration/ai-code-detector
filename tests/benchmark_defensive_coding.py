import time
import re
from ai_code_detector import AICodeDetector

def run_benchmark():
    detector = AICodeDetector()

    code_chunk = """
def process_data(data):
    if data is not None:
        if type_data != null:
            pass
    if isinstance(data, dict):
        pass
    try:
        do_something()
    except Exception as e:
        pass
    assert data > 0
    if condition:
        pass
    if condition:
        pass
    if not valid:
        raise ValueError("Invalid")
"""
    large_code = code_chunk * 5000

    start_time = time.time()

    iterations = 200
    for _ in range(iterations):
        # Force a cache clear to simulate processing many different files/patterns
        re.purge()
        detector._analyze_defensive_coding(large_code)

    end_time = time.time()

    total_time = end_time - start_time
    avg_time = total_time / iterations

    print(f"Total time for {iterations} iterations: {total_time:.4f} seconds")
    print(f"Average time per iteration: {avg_time:.4f} seconds")

if __name__ == "__main__":
    run_benchmark()
