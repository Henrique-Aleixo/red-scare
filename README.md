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

**Problem Statement:** Find the shortest simple path from $s$ to $t$ such that no internal vertex (i.e., vertices other than $s$ and $t$) is red. If $s$ or $t$ is red, they are still allowed as endpoints. If no such path exists, return -1.

- **Complexity**: O(n + m) - Polynomial
- **Algorithm**: Construct a filtered graph $G'$ from $G$ where all internal red vertices are removed:
  - $V' = V \backslash (R \backslash \{s, t\})$
  - $E' = E \cap (V' \times V')$
  - Run breadth-first search (BFS) from $s$ in $G'$ to find the shortest path to $t$
- **Implementation**: 
  - We maintain an array `allowed` of size $n$, initially all True
  - For each vertex $v \in R$ where $v \neq s$ and $v \neq t$, we set `allowed[v] = False`
  - During BFS, we skip any neighbor $v$ where `allowed[v] = False`
  - We use a queue (deque) for BFS and maintain a `prev` array to reconstruct the path
  - The algorithm handles both directed and undirected edges by respecting the edge orientation from the input
  - This approach avoids explicitly constructing a new graph structure, instead filtering vertices on-the-fly during traversal, which is more memory-efficient

### SOME Problem

**Problem Statement:** Determine whether there exists a simple $s$-$t$ path that includes at least one red vertex. Return true if such a path exists, false otherwise.

- **Computational Complexity**: The SOME problem is NP-hard in general. A sophisticated hardness argument exists in the literature (see Dinitz & Shimony, arXiv:2302.09614), which implies that no polynomial-time algorithm can solve it correctly for all graphs. However, the problem becomes tractable for certain graph classes, and we implement two approaches with different trade-offs.

- **Two Approaches Implemented**:

#### Approach 1: Polynomial-Time Only (`some.py`)
- **Complexity**: O(n + m)
- **Coverage**: Only solves trees and DAGs. For all other graph classes, outputs "!?" (unsolved).
- **Algorithm**: 
  - **Trees**: Find the unique $s$-$t$ path and check if it contains a red vertex. Complexity: O(n)
  - **DAGs**: Use dynamic programming to determine if a path with a red vertex exists. Complexity: O(n + m)

#### Approach 2: Ford-Fulkerson with Verification (`some_ff.py`)

**Vertex Splitting:** We construct a flow network $G'$ from $G$ using vertex splitting:
- Each vertex $v$ becomes two nodes: $v_{\text{in}}$ and $v_{\text{out}}$
- Add edge $v_{\text{in}} \rightarrow v_{\text{out}}$ with capacity 1 (ensures each vertex used at most once, guaranteeing simple paths)
- For each original edge $(u, v)$, add edge $u_{\text{out}} \rightarrow v_{\text{in}}$ with capacity 1

The transformed graph has $2n$ vertices and $m+n$ edges.

**Algorithm:** For each red vertex $r \in R$ individually:
1. Find a simple path $s \rightsquigarrow r$: run Ford-Fulkerson from $s_{\text{out}}$ to $r_{\text{in}}$
2. If found, find a simple path $r \rightsquigarrow t$: run Ford-Fulkerson from $r_{\text{out}}$ to $t_{\text{in}}$, blocking all vertices used in the $s \rightsquigarrow r$ path (except $r$ itself) to ensure vertex-disjoint paths
3. If both paths exist, return true with the combined path

**Verification-Based Output Scheme:**
- **"true"**: Path with red vertex found (verifiable - the path includes a red vertex)
- **"false"**: No $s$-$t$ path exists (verifiable - checked with BFS)
- **"!?"**: Cannot verify (a path exists but no red vertex was found - we cannot prove that one doesn't exist)

**Coverage:** 128/154 instances with verified results (83.1%)
- True (verified): 104 instances (67.5%)
- False (verified): 24 instances (15.6%)
- !? (unverified): 26 instances (16.9%)

### FEW Problem

**Problem Statement:** Find an $s$-$t$ path that minimizes the number of red vertices visited. Return the minimum count, or -1 if no path exists.

- **Complexity**: O((n + m) log n) - Polynomial
- **Algorithm**: Shortest path with vertex costs (red = 1, others = 0)
- **Implementation**: Transform vertex costs into edge weights using vertex splitting:
  - Each vertex $v$ is split into $v_{\text{in}}$ and $v_{\text{out}}$ connected by an edge of weight 1 if $v$ is red, 0 otherwise
  - Original edges connect $v_{\text{out}}$ to $u_{\text{in}}$ with weight 0
  - Run Dijkstra's algorithm from $s_{\text{out}}$ to $t_{\text{out}}$ to find the path minimizing the number of red vertices

### ALTERNATE Problem

**Problem Statement:** Determine whether there exists a simple $s$-$t$ path such that consecutive vertices have opposite colors (red/non-red). Return true if such a path exists, false otherwise.

**Definition:** A path $P = (v_1, v_2, \ldots, v_k)$ is alternating if for each $i \in \{1, 2, \ldots, k-1\}$, exactly one of $v_i$ or $v_{i+1}$ is red. Equivalently, every edge $(v_i, v_{i+1})$ in the path connects vertices of different color (one red, one non-red).

- **Complexity**: O(n + m) - Polynomial
- **Algorithm**: We solve ALTERNATE by constructing a filtered subgraph $G_{\text{alt}} = (V, E_{\text{alt}})$ where we keep only edges that connect vertices of different colors:
  - $E_{\text{alt}} = \{(u, v) \in E: (\text{color}(u) = \text{red} \wedge \text{color}(v) \neq \text{red}) \vee (\text{color}(u) \neq \text{red} \wedge \text{color}(v) = \text{red})\}$
  - That is, we remove all edges where both endpoints have the same color (both red or both non-red)
  - We then run breadth-first search (BFS) from $s$ in $G_{\text{alt}}$ to test reachability of $t$
  - If $t$ is reachable, we return true along with a sample alternating path; otherwise we return false
- **Implementation**: 
  - For each edge $(u, v)$ in the original graph, we check if exactly one of $u$ or $v$ is red
  - If the edge is alternating (one endpoint red, one non-red), we add it to the adjacency list
  - If both endpoints have the same color, we skip the edge entirely
  - We handle both directed and undirected edges: for undirected edges, we add both directions if the edge is alternating
  - We run standard BFS from $s$ to $t$ on the filtered graph, maintaining a `prev` array to reconstruct the path if found
  - This approach avoids explicitly storing non-alternating edges, making it memory-efficient

### MANY Problem

**Problem Statement:** Find a simple $s$-$t$ path that maximizes the number of red vertices visited. Return the maximum count, or -1 if no path exists.

**Computational Complexity:** The decision version of MANY ("is there an $s$-$t$ path that visits at least $k$ red vertices?") is NP-complete. In particular, MANY is NP-hard via a reduction from the Longest Path problem.

**Hardness Proof (Reduction):**
Let $L = (G_L, s, t)$ be an instance of Longest Path: given a graph $G_L$ and vertices $s, t$, find the longest simple path from $s$ to $t$. Construct an instance $G$ for MANY by taking $G := G_L$ (same graph and vertices $s, t$) and setting $R := V$ (i.e., every vertex is red).

If we solve MANY on this instance, we find the maximum number of red vertices on any simple $s$-$t$ path. Since all vertices are red, maximizing the number of red vertices visited is equivalent to maximizing the number of vertices visited, which equals the length of the longest path. Therefore, the answer to MANY equals the answer to the original Longest Path problem.

If MANY were solvable in polynomial time, then Longest Path would also be solvable in polynomial time. Since Longest Path is NP-hard, MANY must also be NP-hard.

Membership in NP is immediate for the decision version: a candidate path can be verified in polynomial time by checking simplicity, endpoints, and counting red vertices. Hence the decision version is NP-complete.

Since MANY is NP-hard in general, we implement polynomial-time algorithms only for well-defined graph classes where the problem becomes tractable:

**Polynomial-Time Algorithms for Special Cases:**

1. **Trees** - Complexity: O(n)
   - If $G$ is a tree (connected graph with $m = n-1$ edges for directed trees, or $m = 2(n-1)$ for undirected trees where each edge is counted twice), there exists a unique simple path from $s$ to $t$
   - We solve MANY by:
     - Detecting if the graph is a tree by checking connectivity and edge count
     - Running DFS from $s$ to find the unique $s$-$t$ path
     - Counting red vertices on this path

2. **DAGs** - Complexity: O(n + m)
   - If $G$ is a directed acyclic graph (DAG), we solve MANY using dynamic programming:
     - Detect if the graph is a DAG using iterative DFS cycle detection (to avoid recursion depth limits on large graphs)
     - Compute a topological ordering using Kahn's algorithm
     - Use dynamic programming: for each vertex $v$ in topological order, compute $dp[v] = \max \{\text{reds on path from } s \text{ to } v\}$
     - For each edge $(u, v)$, update $dp[v] = \max(dp[v], dp[u] + c(v))$ where $c(v) = 1$ if $v$ is red, else $c(v) = 0$
     - Reconstruct the optimal path using parent pointers

3. **Other Graphs**
   - For all other graph classes, we output "!?" (unsolved)

**Implementation Details:**
- First checks if an $s$-$t$ path exists using BFS (if none exists, return $-1$)
- Attempts tree detection: checks if the graph is connected and has the correct edge count for a tree (handles both directed and undirected trees)
- If not a tree, attempts DAG detection: uses iterative DFS to avoid stack overflow on large graphs
- If the graph has undirected edges, we also try a "force-directed" conversion: treat all edges as directed and check if the resulting graph is a DAG
- Only uses polynomial-time algorithms; no exponential-time solvers or heuristics are implemented

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

