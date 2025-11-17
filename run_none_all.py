#!/usr/bin/env python3
"""
run_none_all.py
Run the none.py solver on all graph instances in the data/ directory.
Reports success/failure for each instance and provides a summary.
"""
import subprocess
import pathlib
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"
SOLVER = ROOT / "solvers" / "none.py"
TIMEOUT = 60  # seconds per instance

def run_none(instance_path):
    """Run none.py on a single instance and return (success, result, error_msg)."""
    if not SOLVER.exists():
        return False, None, f"Solver not found: {SOLVER}"
    
    cmd = [sys.executable, str(SOLVER), str(instance_path)]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() or "Unknown error"
            return False, None, error_msg
        
        output = result.stdout.strip()
        if not output:
            return False, None, "No output from solver"
        
        # Parse output: first line is length (-1 or a number)
        lines = output.splitlines()
        length = lines[0].strip()
        
        return True, length, None
        
    except subprocess.TimeoutExpired:
        return False, None, f"Timeout after {TIMEOUT} seconds"
    except Exception as e:
        return False, None, f"Exception: {str(e)}"

def main():
    # Get all .txt files in data directory
    instances = sorted([p for p in DATA.iterdir() if p.is_file() and p.suffix == ".txt"])
    
    if not instances:
        print(f"No .txt files found in {DATA}")
        return
    
    print(f"Found {len(instances)} graph instances in {DATA}")
    print(f"Running none.py solver on all instances...\n")
    print("=" * 80)
    
    results = []
    success_count = 0
    failure_count = 0
    
    for i, instance in enumerate(instances, 1):
        print(f"[{i}/{len(instances)}] Processing {instance.name}...", end=" ", flush=True)
        
        success, result, error = run_none(instance)
        
        if success:
            print(f"[OK] SUCCESS (result: {result})")
            success_count += 1
            results.append((instance.name, True, result, None))
        else:
            print(f"[FAIL] FAILED: {error}")
            failure_count += 1
            results.append((instance.name, False, None, error))
    
    print("=" * 80)
    print("\nSUMMARY:")
    print(f"  Total instances: {len(instances)}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {failure_count}")
    
    if failure_count > 0:
        print("\nFAILED INSTANCES:")
        for name, success, result, error in results:
            if not success:
                print(f"  - {name}: {error}")
    
    # Exit with error code if any failures
    sys.exit(1 if failure_count > 0 else 0)

if __name__ == "__main__":
    main()

