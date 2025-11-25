#!/usr/bin/env python3
"""
Compare the two SOME solver approaches:
1. Polynomial-time only (some.py) - trees and DAGs
2. Ford-Fulkerson (some_ff.py)

Run both on all instances and compare results.
"""
import subprocess
import sys
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"
SOLVER_POLY = ROOT / "solvers" / "some.py"
SOLVER_FF = ROOT / "solvers" / "some_ff.py"

def run_solver(solver_path, instance_path):
    """Run a solver on an instance and return (success, result, path)."""
    try:
        result = subprocess.run(
            [sys.executable, str(solver_path), str(instance_path)],
            capture_output=True,
            text=True,
            timeout=60  # Polynomial algorithm, should complete but allow time for large graphs
        )
        
        if result.returncode != 0:
            return False, None, None, result.stderr
        
        output = result.stdout.strip()
        lines = output.split('\n')
        
        if not lines:
            return False, None, None, "No output"
        
        answer = lines[0].strip().lower()
        path = lines[1].strip() if len(lines) > 1 else None
        
        return True, answer, path, None
        
    except subprocess.TimeoutExpired:
        return False, None, None, "Timeout"
    except Exception as e:
        return False, None, None, str(e)

def main():
    print("Comparing SOME solver approaches...")
    print("=" * 80)
    
    instances = sorted([p for p in DATA.iterdir() if p.is_file() and p.suffix == ".txt"])
    
    if not instances:
        print(f"No .txt files found in {DATA}")
        return
    
    print(f"Found {len(instances)} instances\n")
    
    results = []
    stats = {
        'poly_solved': 0,
        'poly_unsolved': 0,
        'ff_solved': 0,
        'ff_false': 0,
        'ff_unsolved': 0,
        'both_same': 0,
        'different': 0,
        'poly_true_ff_false': 0,
        'poly_false_ff_true': 0,
        'poly_unsolved_ff_solved': 0,
        'poly_unsolved_ff_unsolved': 0,
    }
    
    differences = []
    
    for i, instance_path in enumerate(instances, 1):
        instance_name = instance_path.name
        print(f"[{i}/{len(instances)}] {instance_name}...", end=" ", flush=True)
        
        # Run polynomial-time solver
        poly_success, poly_result, poly_path, poly_error = run_solver(SOLVER_POLY, instance_path)
        if not poly_success:
            print(f"POLY ERROR: {poly_error}")
            continue
        
        # Run Ford-Fulkerson solver
        ff_success, ff_result, ff_path, ff_error = run_solver(SOLVER_FF, instance_path)
        if not ff_success:
            print(f"FF ERROR: {ff_error}")
            continue
        
        # Update statistics
        if poly_result == "true" or poly_result == "false":
            stats['poly_solved'] += 1
        else:
            stats['poly_unsolved'] += 1
        
        if ff_result == "true":
            stats['ff_solved'] += 1
        elif ff_result == "false":
            stats['ff_false'] += 1
        elif ff_result == "!?":
            stats['ff_unsolved'] = stats.get('ff_unsolved', 0) + 1
        
        # Compare results
        if poly_result == ff_result:
            stats['both_same'] += 1
            print(f"Same: {poly_result}")
        else:
            stats['different'] += 1
            differences.append((instance_name, poly_result, ff_result))
            
            if poly_result == "true" and ff_result == "false":
                stats['poly_true_ff_false'] += 1
                print(f"DIFF: poly=true, ff=false")
            elif poly_result == "false" and ff_result == "true":
                stats['poly_false_ff_true'] += 1
                print(f"DIFF: poly=false, ff=true")
            elif poly_result == "!?" and ff_result == "true":
                stats['poly_unsolved_ff_solved'] += 1
                print(f"DIFF: poly=!?, ff=true")
            elif poly_result == "!?" and ff_result == "false":
                stats['poly_unsolved_ff_solved'] += 1
                print(f"DIFF: poly=!?, ff=false")
            elif poly_result == "!?" and ff_result == "!?":
                stats['poly_unsolved_ff_unsolved'] += 1
                print(f"Same: !?")
            else:
                print(f"DIFF: poly={poly_result}, ff={ff_result}")
        
        results.append((instance_name, poly_result, ff_result))
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nPolynomial-Time Solver (some.py):")
    print(f"  Solved (true/false): {stats['poly_solved']}")
    print(f"  Unsolved (!?): {stats['poly_unsolved']}")
    
    print(f"\nFord-Fulkerson Solver (some_ff.py):")
    print(f"  True: {stats['ff_solved']}")
    print(f"  False: {stats['ff_false']}")
    print(f"  Unsolved (!?): {stats.get('ff_unsolved', 0)}")
    print(f"  Total with answer: {stats['ff_solved'] + stats['ff_false']}")
    
    print(f"\nComparison:")
    print(f"  Same result: {stats['both_same']}")
    print(f"  Different: {stats['different']}")
    print(f"  Poly=true, FF=false: {stats['poly_true_ff_false']} (FF missed valid path)")
    print(f"  Poly=false, FF=true: {stats['poly_false_ff_true']} (FF found path poly couldn't)")
    print(f"  Poly=!?, FF solved: {stats['poly_unsolved_ff_solved']} (FF solved unsolved cases)")
    print(f"  Poly=!?, FF=!?: {stats.get('poly_unsolved_ff_unsolved', 0)} (Both unsolved)")
    
    if differences:
        print(f"\nInstances with different results ({len(differences)}):")
        for name, poly_res, ff_res in differences[:20]:  # Show first 20
            print(f"  {name}: poly={poly_res}, ff={ff_res}")
        if len(differences) > 20:
            print(f"  ... and {len(differences) - 20} more")

if __name__ == "__main__":
    main()

