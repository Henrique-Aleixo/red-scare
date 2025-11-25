# Red Scare

A collection of solvers for the Red Scare problem variants on graphs.

## Problem Description

The Red Scare problem involves finding paths in a graph with special constraints related to "red" vertices. This project implements solvers for five problem variants:

- **NONE**: Find the shortest s-t path that internally avoids all red vertices
- **SOME**: Determine if there exists an s-t path that includes at least one red vertex
- **FEW**: Find an s-t path minimizing the number of red vertices
- **MANY**: Maximize the number of red vertices on any simple s-t path (NP-hard)
- **ALTERNATE**: Determine if there exists an s-t path that alternates between red and non-red vertices

## Project Structure

```
red-scare/
├── solvers/          # Problem solvers
│   ├── none.py       # NONE problem solver (BFS-based)
│   ├── some.py       # SOME problem solver (polynomial-time only: trees & DAGs)
│   ├── some_ff.py    # SOME problem solver (Ford-Fulkerson with verification)
│   ├── few.py        # FEW problem solver (Dijkstra with vertex splitting)
│   ├── many.py       # MANY problem solver (NP-hard, polynomial-time only: trees & DAGs)
│   └── alternate.py  # ALTERNATE problem solver (BFS on filtered graph)
├── data/             # Test instances (154 instances)
├── doc/              # Documentation and strategy plans
├── run_none_all.py      # Batch runner for NONE
├── run_some_all.py      # Batch runner for SOME (polynomial-time only)
├── run_some_ff_all.py   # Batch runner for SOME (Ford-Fulkerson)
├── run_few_all.py       # Batch runner for FEW
├── run_many_all.py      # Batch runner for MANY
├── run_alternate_all.py # Batch runner for ALTERNATE
├── compare_some_approaches.py  # Compare polynomial vs Ford-Fulkerson approaches
├── comprehensive_test_some.py  # Comprehensive test suite for SOME
└── results.txt          # Results summary for all instances
```

## Input Format

Each input file follows this format:

```
n m r
s t
<vertices>           # n lines, vertex names. Red vertices end with ' *'
<edges>              # m lines, either "u -- v" (undirected) or "u -> v" (directed)
```

Where:
- `n` = number of vertices
- `m` = number of edges
- `r` = number of red vertices
- `s` = source vertex name
- `t` = target vertex name

See `data/README.md` for detailed format specification.

## Usage

### Running Individual Solvers

```bash
# NONE: shortest path avoiding red vertices
python solvers/none.py data/instance.txt

# SOME: check if path with red vertex exists
# Option 1: Polynomial-time only (trees and DAGs)
python solvers/some.py data/instance.txt

# Option 2: Ford-Fulkerson with verification (recommended)
python solvers/some_ff.py data/instance.txt

# FEW: path minimizing red vertices
python solvers/few.py data/instance.txt

# MANY: path maximizing red vertices
python solvers/many.py data/instance.txt

# ALTERNATE: check if alternating path exists
python solvers/alternate.py data/instance.txt
```

### Running All Instances

```bash
# Run NONE solver on all instances
python run_none_all.py

# Run SOME solver on all instances
# Polynomial-time only (trees and DAGs)
python run_some_all.py

# Ford-Fulkerson with verification
python run_some_ff_all.py

# Run FEW solver on all instances
python run_few_all.py

# Run MANY solver on all instances
python run_many_all.py

# Run ALTERNATE solver on all instances
python run_alternate_all.py
```

## Algorithm Approaches

### NONE Problem
- **Complexity**: O(n + m) - Polynomial
- **Algorithm**: Remove red vertices (except endpoints), then BFS for shortest path
- **Implementation**: BFS from s to t, avoiding red vertices (except s and t are allowed even if red). We mark all internal red vertices as forbidden and run standard BFS to find the shortest path.

### SOME Problem
- **Complexity**: NP-hard (sophisticated hardness argument in literature - see Dinitz & Shimony, arXiv:2302.09614)
- **Problem Statement**: Determine if there exists a simple s-t path that includes at least one red vertex
- **Two Approaches Implemented**:

#### Approach 1: Polynomial-Time Only (`some.py`)
- **Complexity**: O(n + m)
- **Coverage**: 48/154 instances (31.2%)
- **Algorithm**: Only solves trees and DAGs
- **Implementation**: 
  - **Trees**: DFS to find unique s-t path, check if it includes red
  - **DAGs**: Topological sort + dynamic programming to find path with red
  - **Other graphs**: Returns "!?" (unsolved)

#### Approach 2: Ford-Fulkerson with Verification (`some_ff.py`)
- **Complexity**: O(|R| · VE²) - Polynomial-time (where |R| is number of red vertices)
- **Coverage**: 128/154 instances with verified results (83.1%)
  - True (verified): 104 instances (67.5%)
  - False (verified): 24 instances (15.6%)
  - !? (unverified): 26 instances (16.9%)
- **Algorithm**: Ford-Fulkerson (Edmonds-Karp) with vertex splitting
- **Implementation Details**:
  - **Vertex Splitting**: Each vertex v becomes v_in and v_out connected by capacity-1 edge (ensures simple paths)
  - **Approach**: For each red vertex r individually:
    1. Find path s → r (target r_in)
    2. If found, find path r → t (start from r_out, block vertices from s→r)
    3. If both found, return true with combined path
  - **Verification-Based**: Only returns "true"/"false" when verifiable:
    - **"true"**: Path with red found (verifiable - path includes red)
    - **"false"**: No s-t path exists (verifiable - checked with BFS)
    - **"!?"**: Cannot verify (path exists but no red found - can't prove one doesn't exist)
- **Why This Works**: Handles each red vertex individually to avoid blocking issues from handling all reds at once
- **Limitations**: May miss valid solutions when the first path s→r blocks path r→t (e.g., wall problems)

**Literature Reference**: "On Existence of Must-Include Paths and Cycles in Undirected Graphs" by Yefim Dinitz and Solomon Eyal Shimony (arXiv:2302.09614, 2023)

### FEW Problem
- **Complexity**: O((n + m) log n) - Polynomial
- **Algorithm**: Shortest path with vertex costs (red = 1, others = 0)
- **Implementation**: Transform vertex costs into edge weights using vertex splitting. Each vertex v is split into v_in and v_out connected by an edge of weight 1 if v is red, 0 otherwise. Original edges connect v_out to u_in with weight 0. Run Dijkstra's algorithm from s_out to t_out to find the path minimizing the number of red vertices.

### ALTERNATE Problem
- **Complexity**: O(n + m) - Polynomial
- **Algorithm**: Filter edges to keep only alternating edges, then BFS
- **Implementation**: A path is alternating if for each edge, exactly one endpoint is red. The algorithm filters the graph to keep only edges where exactly one endpoint is red (removing edges between two red vertices or two non-red vertices). Then runs BFS from s to t on the filtered graph. If a path exists in the filtered graph, it is by construction an alternating path. Returns "true" with the path if found, "false" otherwise.

### MANY Problem
- **Complexity**: NP-hard (longest path problem with vertex weights)
- **Computational Hardness**: MANY is NP-hard via reduction from **Longest Path**:
  - **Reducing FROM**: Longest Path (known to be NP-hard)
    - Input: Graph G, vertices s, t
    - Question: What is the longest simple path from s to t?
  
  - **Reducing TO**: MANY (what we want to prove is hard)
    - Input: Graph G, vertices s, t, set of red vertices R
    - Question: What is the maximum number of red vertices on any simple s-t path?
  
  - **The Reduction Process**:
    1. Start with a Longest Path instance: graph G, vertices s, t
    2. Transform it into a MANY instance:
       - Use the same graph G and vertices s, t
       - Mark **all vertices as red** (R = V, where V is the set of all vertices)
    3. Solve MANY: find the maximum number of red vertices on any simple s-t path
    4. Extract the answer: since all vertices are red, the answer equals the longest path length
  
  - **Why This Works**:
    - If all vertices are red, maximizing red vertices = maximizing path length (number of vertices visited)
    - Therefore, solving MANY on this transformed instance solves the original Longest Path problem
    - If MANY were solvable in polynomial time, then Longest Path would also be solvable in polynomial time
    - Since Longest Path is NP-hard, MANY must also be NP-hard
  
  - **Conclusion**: This reduction shows that MANY is at least as hard as Longest Path, proving MANY is NP-hard.

- **Algorithm Overview**: Polynomial-time solutions only for well-defined graph classes. For all other instances, outputs "!?" (unsolved).

- **Polynomial-Time Cases**:
  1. **Trees** (O(n))
     - Check: connected graph with m = 2(n-1) edges (undirected) or m = n-1 edges (directed)
     - Handles both undirected trees and directed trees (arborescences)
     - Solve: DFS to find unique s-t path, count red vertices
     - Returns immediately if tree detected
  
  2. **DAGs** (O(n + m))
     - Check: all edges directed and no cycles (iterative DFS cycle detection)
     - Also attempts: if graph has undirected edges, treats them as directed and checks if result is a DAG
     - Solve: topological sort (Kahn's algorithm) + dynamic programming
     - `dp[v] = max reds on path from s to v`
     - Process vertices in topological order, update dp for each edge
     - Returns immediately if DAG detected (either original or force-directed version)
  
  3. **All Other Graphs**
     - Output "!?" (unsolved) - no polynomial-time solution implemented
     - Only use polynomial-time algorithms as required

- **Implementation Details**: 
  - Uses only polynomial-time algorithms (trees: O(n), DAGs: O(n+m))
  - Tree detection: handles both directed and undirected trees
  - DAG detection: tries force-directed conversion for undirected graphs
  - Iterative DFS for cycle detection (avoids recursion depth limits on large graphs)
  - No exact solvers or heuristics - strictly polynomial-time only
  - Respects simple path constraints (no repeated vertices)

## Results

### Overall Performance Summary

The solvers were tested on **154 instances** across 9 problem groups. Results are grouped by problem type:

| Problem Group | Instances | NONE | FEW | MANY | SOME | ALTERNATE |
|---------------|-----------|------|-----|------|------|-----------|
| **common** | 30 | 30/30 | 30/30 | 13/30 | 30/30 | 30/30 |
| **gnm** | 24 | 24/24 | 24/24 | 2/24 | 24/24 | 24/24 |
| **grid** | 12 | 12/12 | 12/12 | 0/12 | 12/12 | 12/12 |
| **increase** | 18 | 18/18 | 18/18 | 18/18 | 18/18 | 18/18 |
| **other** | 4 | 4/4 | 4/4 | 3/4 | 4/4 | 4/4 |
| **rusty** | 17 | 17/17 | 17/17 | 3/17 | 17/17 | 17/17 |
| **ski** | 13 | 13/13 | 13/13 | 13/13 | 13/13 | 13/13 |
| **smallworld** | 12 | 12/12 | 12/12 | 0/12 | 12/12 | 12/12 |
| **wall** | 24 | 24/24 | 24/24 | 0/24 | 0/24 | 24/24 |
| **TOTAL** | **154** | **154/154** | **154/154** | **54/154** | **128/154** | **154/154** |

### Notes on Results

- **NONE**: 100% success rate (154/154 instances)
  - 113 instances (73.4%) found a solution (path length)
  - 41 instances (26.6%) returned `-1` (no valid path exists)
  
- **FEW**: 100% success rate (154/154 instances)
  - 130 instances (84.4%) found a solution (minimum red vertices)
  - 24 instances (15.6%) returned `-1` (no valid path exists)
  
- **SOME**: Two approaches implemented
  - **Polynomial-Time** (`some.py`): 48/154 instances (31.2% success rate)
  - **Ford-Fulkerson with Verification** (`some_ff.py`): 128/154 instances with verified results (83.1%)
    - 104 instances (67.5%) returned `true` (path with red found - verified)
    - 24 instances (15.6%) returned `false` (no s-t path exists - verified)
    - 26 instances (16.9%) returned `!?` (cannot verify - path exists but no red found)
  
- **ALTERNATE**: 100% success rate (154/154 instances)
  - 56 instances (36.4%) returned `true` (alternating path exists)
  - 98 instances (63.6%) returned `false` (no alternating path exists)
  
- **MANY**: 35.1% success rate (54/154 instances)
  - 30 instances (19.5%) found a solution (maximum red vertices) - trees and DAGs only
  - 24 instances (15.6%) returned `-1` (no valid path exists, which is a valid answer)
  - 100 instances (64.9%) marked as `!?` unsolved

**Result Codes:**
- **Numbers**: Optimal or best-found solution (number of red vertices)
- **`-1`**: Valid answer meaning "no valid path exists" (counts as solved)
- **`!?`**: Unable to solve or cannot verify result 
- **`true`/`false`**: Boolean result for SOME and ALTERNATE problems

See `results.txt` for detailed per-instance results.

## Documentation

Detailed documentation for the SOME problem:
- `doc/SOME_Problem_Complete.md` - Complete documentation of SOME problem implementation
- `doc/SOME_Approach_Analysis.md` - Analysis of the Ford-Fulkerson approach
- `doc/SOME_Literature_References.md` - Literature references for NP-hardness
- `doc/Wall_Problem_Analysis.md` - Analysis of why wall problems return "!?"

## Testing

Comprehensive test suite for SOME problem:
```bash
# Run comprehensive tests
python comprehensive_test_some.py

# Compare polynomial vs Ford-Fulkerson approaches
python compare_some_approaches.py
```

## Requirements

- Python 3.6+

No external dependencies required (uses only Python standard library).

