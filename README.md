# Red Scare

A collection of solvers for the Red Scare problem variants on graphs.

## Problem Description

The Red Scare problem involves finding paths in a graph with special constraints related to "red" vertices. This project implements solvers for four problem variants:

- **NONE**: Find the shortest s-t path that internally avoids all red vertices
- **SOME**: Determine if there exists an s-t path that includes at least one red vertex
- **FEW**: Find an s-t path minimizing the number of red vertices
- **MANY**: Maximize the number of red vertices on any simple s-t path (NP-hard)

## Project Structure

```
red-scare/
├── solvers/          # Problem solvers
│   ├── none.py       # NONE problem solver (BFS-based)
│   ├── some.py       # SOME problem solver (Ford-Fulkerson with vertex splitting)
│   ├── few.py        # FEW problem solver (Dijkstra with vertex splitting)
│   └── many.py       # MANY problem solver (NP-hard, uses heuristics + exact search)
├── data/             # Test instances (154 instances)
├── doc/              # Documentation and strategy plans
│   ├── MANY_Strategy_Plan.md  # Detailed strategy for MANY problem
│   └── Red Scare Notes.txt    # Problem notes and algorithms
├── run_none_all.py   # Batch runner for NONE
├── run_some_all.py   # Batch runner for SOME
├── run_few_all.py    # Batch runner for FEW
├── run_many_all.py   # Batch runner for MANY
└── results.txt       # Results summary for all instances
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
python solvers/some.py data/instance.txt

# FEW: path minimizing red vertices
python solvers/few.py data/instance.txt

# MANY: path maximizing red vertices
python solvers/many.py data/instance.txt
```

### Running All Instances

```bash
# Run NONE solver on all instances
python run_none_all.py

# Run SOME solver on all instances
python run_some_all.py

# Run FEW solver on all instances
python run_few_all.py

# Run MANY solver on all instances (NP-hard, may take longer)
python run_many_all.py
```

## Requirements

- Python 3.6+

No external dependencies required (uses only Python standard library).

## Algorithm Approaches

### NONE Problem
- **Complexity**: O(n + m) - Polynomial
- **Algorithm**: Remove red vertices (except endpoints), then BFS for shortest path
- **Implementation**: BFS from s to t, avoiding red vertices (except s and t are allowed even if red). We mark all internal red vertices as forbidden and run standard BFS to find the shortest path.

### SOME Problem
- **Complexity**: O(n·m) - Polynomial (Edmonds-Karp typically O(VE²) for max flow, but we only need one path so limit to n augmenting paths)
- **Algorithm**: Ford-Fulkerson (Edmonds-Karp) with vertex splitting to find simple paths
- **Implementation**: Uses network flow with vertex splitting to guarantee simple paths (no repeated vertices). Each vertex v is split into v_in and v_out connected by a capacity-1 edge, ensuring each vertex is used at most once. Original edges become u_out → v_in. We find augmenting paths using BFS and check if they include at least one red vertex. If no direct path uses red, we check for paths s→r→t for each red vertex r, ensuring the combined path is simple by blocking vertices used in the first segment. This approach correctly handles the simple path requirement that was problematic in naive BFS implementations.

### FEW Problem
- **Complexity**: O((n + m) log n) - Polynomial
- **Algorithm**: Shortest path with vertex costs (red = 1, others = 0)
- **Implementation**: Transform vertex costs into edge weights using vertex splitting. Each vertex v is split into v_in and v_out connected by an edge of weight 1 if v is red, 0 otherwise. Original edges connect v_out to u_in with weight 0. Run Dijkstra's algorithm from s_out to t_out to find the path minimizing the number of red vertices.

### MANY Problem
- **Complexity**: NP-hard (longest path problem with vertex weights)
- **Algorithm**: Multi-tier strategy combining:
  - Special case detection (DAGs, trees, small instances)
  - Exact branch-and-bound search with pruning
  - Beam search heuristics
  - Adaptive timeouts based on instance size
- **Implementation**: For small instances or trees/DAGs, uses polynomial-time algorithms (DFS for trees, topological sort + DP for DAGs). For general graphs, uses branch-and-bound DFS with pruning based on upper bounds of reachable red vertices. For larger instances, falls back to beam search or greedy heuristics with timeout support.

## Results

### Overall Performance Summary

The solvers were tested on **154 instances** across 9 problem groups. Results are grouped by problem type:

| Problem Group | Instances | NONE | FEW | MANY | SOME |
|---------------|-----------|------|-----|------|------|
| **common** | 30 | 30/30 (100.0%) | 30/30 (100.0%) | 19/30 (63.3%) | 30/30 (100.0%) |
| **gnm** | 24 | 24/24 (100.0%) | 24/24 (100.0%) | 18/24 (75.0%) | 24/24 (100.0%) |
| **grid** | 12 | 12/12 (100.0%) | 12/12 (100.0%) | 9/12 (75.0%) | 12/12 (100.0%) |
| **increase** | 18 | 18/18 (100.0%) | 18/18 (100.0%) | 18/18 (100.0%) | 18/18 (100.0%) |
| **other** | 4 | 4/4 (100.0%) | 4/4 (100.0%) | 3/4 (75.0%) | 4/4 (100.0%) |
| **rusty** | 17 | 17/17 (100.0%) | 17/17 (100.0%) | 6/17 (35.3%) | 17/17 (100.0%) |
| **ski** | 13 | 13/13 (100.0%) | 13/13 (100.0%) | 13/13 (100.0%) | 13/13 (100.0%) |
| **smallworld** | 12 | 12/12 (100.0%) | 12/12 (100.0%) | 10/12 (83.3%) | 12/12 (100.0%) |
| **wall** | 24 | 24/24 (100.0%) | 24/24 (100.0%) | 24/24 (100.0%) | 24/24 (100.0%) |
| **TOTAL** | **154** | **154/154 (100.0%)** | **154/154 (100.0%)** | **120/154 (77.9%)** | **154/154 (100.0%)** |

### Notes on Results

- **NONE**: 100% success rate (154/154 instances)
  - 113 instances (73.4%) found a solution (path length)
  - 41 instances (26.6%) returned `-1` (no valid path exists, which is a valid answer)
  - All instances solved using BFS
  
- **FEW**: 100% success rate (154/154 instances)
  - 130 instances (84.4%) found a solution (minimum red vertices)
  - 24 instances (15.6%) returned `-1` (no valid path exists, which is a valid answer)
  - All instances solved optimally using Dijkstra's algorithm
  
- **SOME**: 100% success rate (154/154 instances)
  - 107 instances (69.5%) returned `true` (path with at least one red vertex exists)
  - 47 instances (30.5%) returned `false` (no such path exists)
  - All instances solved using Ford-Fulkerson (Edmonds-Karp) with vertex splitting
  - This implementation correctly ensures simple paths, fixing a bug in the previous BFS approach
  
- **MANY**: 77.9% success rate (120/154 instances)
  - 94 instances (61.0%) found a solution (maximum red vertices)
  - 26 instances (16.9%) returned `-1` (no valid path exists, which is a valid answer)
  - 34 instances (22.1%) timed out (marked as `!?`, does NOT count as solved)
  - Challenging due to NP-hardness - uses exact search for small instances, heuristics for larger ones

**Result Codes:**
- **Numbers**: Optimal or best-found solution (number of red vertices)
- **`-1`**: Valid answer meaning "no valid path exists" (counts as solved)
- **`!?`**: Timeout or unable to solve within time limit (does NOT count as solved)
- **`true`/`false`**: Boolean result for SOME problem

See `results.txt` for detailed per-instance results.

