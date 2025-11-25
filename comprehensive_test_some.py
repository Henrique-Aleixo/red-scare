#!/usr/bin/env python3
"""
Comprehensive testing for SOME problem Ford-Fulkerson solver.
Tests various edge cases and verifies correctness.
"""
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SOLVER_FF = ROOT / "solvers" / "some_ff.py"
DATA = ROOT / "data"

def create_test(name, content):
    """Create a test file."""
    test_file = DATA / f"test_{name}.txt"
    with open(test_file, 'w') as f:
        f.write(content)
    return test_file

def run_test(instance_path, expected, description):
    """Run a test and return (passed, result, path)."""
    try:
        result = subprocess.run(
            [sys.executable, str(SOLVER_FF), str(instance_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return False, f"ERROR: {result.stderr}", None
        
        lines = result.stdout.strip().split('\n')
        answer = lines[0].strip().lower() if lines else "ERROR"
        path = lines[1].strip().split() if len(lines) > 1 else None
        
        passed = (answer == expected.lower())
        return passed, answer, path
        
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT", None
    except Exception as e:
        return False, f"EXCEPTION: {e}", None

def verify_path_has_red(instance_path, path):
    """Verify that path includes at least one red vertex."""
    if not path:
        return True, "No path to verify"
    
    # Read instance to get red vertices
    with open(instance_path, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    header = lines[0].split()
    n = int(header[0])
    red_vertices = set()
    for i in range(2, 2+n):
        if i < len(lines) and lines[i].endswith('*'):
            red_vertices.add(lines[i].rstrip('*').strip())
    
    path_has_red = any(v in red_vertices for v in path)
    return path_has_red, red_vertices

def main():
    print("Comprehensive Testing for SOME Problem (Ford-Fulkerson)")
    print("=" * 80)
    
    tests = []
    
    # Test 1: Edge case from professor's feedback - multiple reds sharing common vertex
    tests.append((
        "edge_case_professor",
        """7 7 2
0 6
0
1
2 *
3
4 *
5
6
0 -- 1
1 -- 2
0 -- 3
3 -- 4
2 -- 5
4 -- 5
5 -- 6""",
        "true",
        "Edge case: Multiple red vertices sharing common vertex to t"
    ))
    
    # Test 2: Simple direct path with red
    tests.append((
        "simple_direct",
        """4 3 1
0 3
0
1 *
2
3
0 -- 1
1 -- 2
2 -- 3""",
        "true",
        "Simple: Direct path with red vertex"
    ))
    
    # Test 3: Path must go s->r->t
    tests.append((
        "s_to_r_to_t",
        """5 4 1
0 4
0
1
2 *
3
4
0 -- 1
1 -- 2
2 -- 3
3 -- 4""",
        "true",
        "Path must go s->r->t"
    ))
    
    # Test 4: No path with red exists
    tests.append((
        "no_path_red",
        """5 3 1
0 4
0
1
2 *
3
4
0 -- 1
1 -- 3
3 -- 4""",
        "!?",
        "No path with red exists (red vertex isolated from s-t path) - can't verify false"
    ))
    
    # Test 5: Source is red
    tests.append((
        "s_is_red",
        """4 3 1
0 3
0 *
1
2
3
0 -- 1
1 -- 2
2 -- 3""",
        "true",
        "Source vertex is red"
    ))
    
    # Test 6: Target is red
    tests.append((
        "t_is_red",
        """4 3 1
0 3
0
1
2
3 *
0 -- 1
1 -- 2
2 -- 3""",
        "true",
        "Target vertex is red"
    ))
    
    # Test 7: Multiple reds, only one path works
    tests.append((
        "multiple_reds_one_works",
        """7 6 2
0 6
0
1
2 *
3
4 *
5
6
0 -- 1
1 -- 2
2 -- 3
3 -- 4
4 -- 5
5 -- 6
0 -- 3""",
        "true",
        "Multiple reds, path through r1 works"
    ))
    
    # Test 8: Complex case - red in middle, multiple paths
    tests.append((
        "complex_middle_red",
        """6 7 1
0 5
0
1
2 *
3
4
5
0 -- 1
1 -- 2
2 -- 3
3 -- 4
4 -- 5
0 -- 3
1 -- 4""",
        "true",
        "Complex: Red in middle, multiple paths exist"
    ))
    
    # Test 9: No path exists at all
    tests.append((
        "no_path",
        """4 2 1
0 3
0
1
2 *
3
0 -- 1
2 -- 3""",
        "false",
        "No path from s to t exists"
    ))
    
    # Test 10: Path exists but no red on any path
    tests.append((
        "path_no_red",
        """5 3 1
0 4
0
1
2 *
3
4
0 -- 1
1 -- 3
3 -- 4""",
        "!?",
        "Path exists but red vertex not on any s-t path - can't verify false"
    ))
    
    passed = 0
    failed = 0
    issues = []
    
    for name, content, expected, desc in tests:
        test_file = create_test(name, content)
        print(f"\n[{passed + failed + 1}/{len(tests)}] {desc}")
        
        result_passed, result, path = run_test(test_file, expected, desc)
        
        if result_passed:
            if result == "true" and path:
                # Verify path includes red
                has_red, reds = verify_path_has_red(test_file, path)
                if has_red:
                    print(f"  [OK] Result: {result}, Path: {' -> '.join(path)}")
                    passed += 1
                else:
                    print(f"  [BUG] Path does not include red! Path: {path}, Reds: {reds}")
                    failed += 1
                    issues.append(f"{name}: Path {path} does not include red vertex")
            elif result == "!?":
                # !? is acceptable when we can't verify
                print(f"  [OK] Result: {result} (cannot verify)")
                passed += 1
            else:
                print(f"  [OK] Result: {result}")
                passed += 1
        else:
            print(f"  [FAIL] Expected {expected}, got {result}")
            failed += 1
            issues.append(f"{name}: Expected {expected}, got {result}")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    
    if issues:
        print("\nISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nAll tests passed!")

if __name__ == "__main__":
    main()

