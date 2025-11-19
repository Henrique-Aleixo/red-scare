# MANY Problem: Strategy to Maximize Solved Instances

## Problem Overview
- **MANY**: Maximize number of red vertices on any simple s-t path
- **Complexity**: NP-hard (longest path with vertex weights)
- **Instance Count**: 154 test instances, ranging from n=3 to n=80000

## Current Implementation Analysis

### Instance Characteristics (from results.txt)
- **Small instances**: n < 100 (e.g., G-ex.txt, P3.txt, grid-5-*.txt)
- **Medium instances**: 100 ≤ n < 1000 (e.g., grid-10-*.txt, common-1-100.txt)
- **Large instances**: 1000 ≤ n < 5000 (e.g., grid-25-*.txt, gnm-*.txt)
- **Very large instances**: n ≥ 5000 (e.g., wall-n-10000.txt, grid-50-*.txt)
- **Graph types**: grids, random graphs (gnm), small-world, wall graphs, ski graphs, etc.

## Multi-Tier Strategy

### Tier 1: Quick Runs (Polynomial-Time Special Cases)

#### 1.1 DAG Detection & Topological Sort
- **If graph is a DAG**: Use dynamic programming
- **Algorithm**: 
  - Topological sort vertices
  - DP[v] = max reds on path from s to v
  - DP[s] = 1 if s in R else 0
  - For each v in topological order: DP[v] = max(DP[u] + (1 if v in R else 0)) for all u→v
- **Time**: O(n + m)
- **Expected instances**: Some directed graphs, possibly some "increase-n" instances

#### 1.2 Tree Detection
- **If graph is a tree**: Unique s-t path exists
- **Algorithm**: Simple DFS from s to t, count reds
- **Time**: O(n)
- **Expected instances**: Some small instances, possibly "wall" graphs

#### 1.3 Small Instance Exact Solve
- **If n ≤ 20**: Always use exact solver (no timeout needed)
- **If 20 < n ≤ 50**: Use exact with generous timeout (30s)
- **Expected instances**: ~15-20 instances

#### 1.4 Very Sparse Graphs
- **If m < 2n**: Graph is very sparse, exact search may be feasible
- **Use**: Exact solver with timeout based on branching factor

### Tier 2: Adaptive Exact Search

#### 2.1 Improved Branch-and-Bound
- **Better upper bound**: Use max-flow/min-cut to estimate reachable reds
- **Vertex ordering**: Prioritize neighbors with:
  1. Higher red density in reachable subgraph
  2. Lower degree (fewer branches)
  3. Closer to t (BFS distance)
- **Early termination**: If upper bound equals known lower bound, stop

#### 2.2 Iterative Deepening
- Start with beam search (fast, gets lower bound)
- Use lower bound to prune exact search more aggressively
- If exact search completes quickly, verify optimality

### Tier 3: Enhanced Heuristics

#### 3.1 Improved Beam Search
- **Adaptive beam width**: 
  - Small graphs (n < 100): beam_width = 200
  - Medium (100 ≤ n < 1000): beam_width = 100
  - Large (n ≥ 1000): beam_width = 50
- **Better scoring function**:
  - Current reds + optimistic estimate
  - Optimistic estimate = min(remaining_reachable_reds, distance_to_t * red_density)
- **Diversity**: Maintain diverse paths in beam (not just top scores)

#### 3.2 Local Search / Simulated Annealing
- Start from greedy solution
- Apply local moves: swap vertices, extend/contract path segments
- Accept worse moves probabilistically (simulated annealing)
- Time limit: 1-2 seconds per instance

#### 3.3 Path Decomposition
- For grid-like graphs: decompose into horizontal/vertical segments
- Solve each segment optimally, combine
- Works well for structured graphs (grids, walls)

### Tier 4: Hybrid Approach

#### 4.1 Progressive Strategy
```
For each instance:
  1. Quick check: Is it a special case? (DAG, tree, very small)
     → Use polynomial-time algorithm
  
  2. Fast heuristic (0.1s): Greedy with 10 restarts
     → Get lower bound L
  
  3. If n < 1000:
     → Try exact search with timeout (5-10s)
     → If timeout, return best-so-far
  
  4. If n ≥ 1000:
     → Beam search with adaptive width
     → If time allows, try local search improvement
  
  5. Return best solution found
```

#### 4.2 Parallel Strategies
- Run multiple heuristics in parallel (with time budget)
- Greedy, beam search, local search simultaneously
- Return best across all

### Tier 5: Graph Structure Exploitation

#### 5.1 Grid Graph Optimization
- Grids have regular structure
- Use dynamic programming along rows/columns
- Time: O(n) for grid graphs

#### 5.2 Component Analysis
- If s and t in different components: return -1 immediately
- If graph has few components: solve each component separately

#### 5.3 Red Vertex Clustering
- If red vertices form clusters: prioritize paths through clusters
- Use red vertex density to guide search

## Implementation Plan

### Phase 1: Foundation (High Priority)
1. **Fix input format** - Make many.py read name-based format like other solvers
2. **Add special case detectors**:
   - DAG detection (cycle detection)
   - Tree detection (m = n-1 and connected)
   - Small instance handler
3. **Implement adaptive timeout** based on instance size
4. **Create run_many_all.py** script for batch processing

### Phase 2: Exact Solver Improvements (Medium Priority)
1. **Better upper bounds**:
   - Max-flow based reachability
   - Red vertex reachability analysis
2. **Improved vertex ordering** in DFS
3. **Iterative deepening** with heuristic lower bound

### Phase 3: Heuristic Enhancements (Medium Priority)
1. **Adaptive beam width** based on graph size
2. **Local search** / simulated annealing
3. **Path decomposition** for structured graphs

### Phase 4: Hybrid System (Low Priority)
1. **Progressive strategy** implementation
2. **Parallel heuristic execution**
3. **Graph structure exploitation**

## Expected Outcomes

### Conservative Estimate
- **Small instances (n < 50)**: 100% solved (exact)
- **Medium instances (50 ≤ n < 500)**: 80-90% solved (exact + heuristic)
- **Large instances (500 ≤ n < 5000)**: 60-70% solved (heuristic, some exact)
- **Very large (n ≥ 5000)**: 50-60% solved (heuristic only)

### Optimistic Estimate
- **Overall**: 70-80% of instances solved optimally or with high-quality solutions
- **Special cases**: 100% of DAGs, trees, small instances
- **Grid graphs**: 90%+ solved optimally using DP

## Testing Strategy

1. **Start with small instances** - Verify exact solver works
2. **Test on medium instances** - Tune timeouts and heuristics
3. **Benchmark on large instances** - Measure success rate
4. **Identify failure patterns** - Which graph types are hardest?
5. **Iterate** - Refine strategies based on results

## Metrics to Track

- **Solve rate**: % of instances with valid solution (not timeout/error)
- **Optimality rate**: % of instances solved optimally (vs heuristic)
- **Average solve time**: Per instance size category
- **Failure analysis**: Which instances fail and why?

