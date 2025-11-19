#!/usr/bin/env python3
"""
run_many_all.py
Run the many.py solver on all graph instances in the data/ directory.
Updates the M column in results.txt with the results.
"""
import subprocess
import pathlib
import sys
import re

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"
SOLVER = ROOT / "solvers" / "many.py"
RESULTS_FILE = ROOT / "results.txt"
TIMEOUT = 120  # seconds per instance (longer for NP-hard problem)

def run_many(instance_path):
    """Run many.py on a single instance and return (success, result, error_msg)."""
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
        
        # Parse output: first line is the number (max red vertices) or -1
        # Second line (if present) is the path (we ignore it for results.txt)
        lines = output.splitlines()
        answer = lines[0].strip()
        
        # Validate it's a number or -1
        try:
            int(answer)
        except ValueError:
            return False, None, f"Unexpected output: {answer}"
        
        return True, answer, None
        
    except subprocess.TimeoutExpired:
        return False, None, f"Timeout after {TIMEOUT} seconds"
    except Exception as e:
        return False, None, f"Exception: {str(e)}"

def read_results_file():
    """Read results.txt and return lines as list of lists."""
    if not RESULTS_FILE.exists():
        return None
    
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Parse lines - format is space-separated with fixed-width columns
    parsed = []
    for line in lines:
        line = line.rstrip("\n")
        if not line.strip() or line.strip().startswith("-"):
            # Skip separator lines but keep them for writing
            parsed.append([line])
            continue
        
        # Split on whitespace, but preserve structure
        # Format: instance (24 chars), n (8), A (8), F (8), M (8), N (8), S (8)
        # Use regex to split on 2+ spaces (column separators)
        parts = re.split(r'\s{2,}', line)
        # Strip each part but keep all parts to preserve column structure
        parts = [p.strip() for p in parts]
        if len(parts) >= 7:
            parsed.append(parts)
        elif len(parts) > 0:
            # Header line or malformed - keep as is
            parsed.append(parts)
    
    return parsed

def write_results_file(lines):
    """Write results back to results.txt with proper formatting."""
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        for parts in lines:
            if len(parts) == 1:
                # Separator line or single-element line - write as-is
                f.write(parts[0] + "\n")
            elif len(parts) < 7:
                # Header or malformed line - write as-is
                if parts[0] == "instance":
                    f.write("instance                  n       A       F       M       N       S\n")
                    f.write("-------------------------------------------------------------------\n")
                else:
                    # Try to reconstruct the line
                    f.write(" ".join(parts) + "\n")
            else:
                # Format: instance, n, A, F, M, N, S
                instance = parts[0]
                n = parts[1]
                A = parts[2]
                F = parts[3]
                M = parts[4]
                N = parts[5]
                S = parts[6]
                
                # Format with proper spacing (matching original format)
                f.write(f"{instance:<24}{n:>8}{A:>8}{F:>8}{M:>8}{N:>8}{S:>8}\n")

def main():
    # Read existing results
    lines = read_results_file()
    if lines is None:
        print(f"Error: {RESULTS_FILE} not found")
        return
    
    # Get header and data lines (skip separator line)
    header = None
    data_lines = []
    for line in lines:
        if len(line) > 0 and line[0] == "instance":
            header = line
        elif len(line) > 0 and not line[0].startswith("-"):
            data_lines.append(line)
    
    if not header:
        print(f"Error: Invalid results.txt format - header not found")
        return
    
    # Get all .txt files in data directory
    instances = sorted([p for p in DATA.iterdir() if p.is_file() and p.suffix == ".txt"])
    
    if not instances:
        print(f"No .txt files found in {DATA}")
        return
    
    print(f"Found {len(instances)} graph instances in {DATA}")
    print(f"Running many.py solver on all instances and updating results.txt...\n")
    print("=" * 80)
    
    # Create a mapping from instance name to line index
    instance_to_line = {}
    for i, line in enumerate(data_lines):
        if len(line) > 0:
            instance_to_line[line[0]] = i
    
    success_count = 0
    failure_count = 0
    updated_count = 0
    failures = []  # Track failures for summary
    
    for i, instance_path in enumerate(instances, 1):
        instance_name = instance_path.name
        print(f"[{i}/{len(instances)}] Processing {instance_name}...", end=" ", flush=True)
        
        success, result, error = run_many(instance_path)
        
        if success:
            print(f"[OK] SUCCESS (result: {result})")
            success_count += 1
            
            # Update the corresponding line in results
            if instance_name in instance_to_line:
                line_idx = instance_to_line[instance_name]
                if len(data_lines[line_idx]) >= 7:
                    data_lines[line_idx][4] = result  # Update M column (index 4)
                    updated_count += 1
                else:
                    print(f"  Warning: Line for {instance_name} has wrong format")
            else:
                print(f"  Warning: {instance_name} not found in results.txt")
        else:
            print(f"[FAIL] FAILED: {error}")
            failure_count += 1
            failures.append((instance_name, error))
    
    print("=" * 80)
    print("\nSUMMARY:")
    print(f"  Total instances: {len(instances)}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {failure_count}")
    print(f"  Updated in results.txt: {updated_count}")
    
    # Write updated results back to file
    if updated_count > 0:
        all_lines = [header, ["-------------------------------------------------------------------"]] + data_lines
        write_results_file(all_lines)
        print(f"\nUpdated {RESULTS_FILE} with {updated_count} results")
    
    if failure_count > 0:
        print("\nFAILED INSTANCES:")
        for instance_name, error in failures:
            print(f"  - {instance_name}: {error}")
    
    # Exit with error code if any failures
    sys.exit(1 if failure_count > 0 else 0)

if __name__ == "__main__":
    main()

