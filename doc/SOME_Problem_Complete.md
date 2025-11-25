# SOME Problem: Complete Documentation

## Problem Statement

**SOME**: Given a graph G, vertices s and t, and a set R of "red" vertices, determine if there exists a **simple path** (no repeated vertices) from s to t that includes **at least one vertex from R**.

## Computational Complexity

The problem is **NP-hard**. A sophisticated hardness argument exists in the research literature:
- **Reference**: "On Existence of Must-Include Paths and Cycles in Undirected Graphs" by Yefim Dinitz and Solomon Eyal Shimony (arXiv:2302.09614, 2023)
- **Implication**: No polynomial-time algorithm can solve it correctly for **all graphs** (unless P=NP)

## Implementation Approaches

### 1. Polynomial-Time Only (`some.py`)
- **Algorithm**: Only solves trees and DAGs
- **Coverage**: 48/154 instances (31.2%)
- **Guarantee**: 100% correctness for solved cases
- **Output**: "!?" for unsolved cases

### 2. Ford-Fulkerson (`some_ff.py`) - Based on Professor's Feedback
- **Algorithm**: Ford-Fulkerson with vertex splitting
- **Coverage**: 128/154 instances with verified results (83.1%)
- **Complexity**: O(|R| * VE²) - polynomial-time
- **Output**: "true"/"false" when verifiable, "!?" otherwise

## Professor's Feedback and Implementation

### The Problem Identified

The professor identified that the original approach had issues:
- Finding all s→R paths first, then R→t paths, can block vertices needed for valid paths
- Example: If we find paths s→A→r1 and s→B→r2 first, we block A and B, which might prevent finding valid r1→t or r2→t paths

### The Solution

Handle each red vertex r **individually**:
1. Find path s → r (target r_in in flow network)
2. If found, find path r → t (start from r_out, block vertices from s→r)
3. If both found, return true with combined path
4. Try next red vertex if current one doesn't work

This avoids blocking issues by processing red vertices separately.

### Verification-Based Approach

We only return "true" or "false" when we can **verify** correctness:
- **"true"**: Path with red vertex found (verifiable - path includes red)
- **"false"**: No s-t path exists (verifiable - checked with BFS)
- **"!?"**: Cannot verify (path exists but no red found - can't prove one doesn't exist)

## Final Results

### Ford-Fulkerson Solver Statistics (154 instances)

- **True (verified)**: 104 instances (67.5%)
- **False (verified)**: 24 instances (15.6%)
- **!? (unverified)**: 26 instances (16.9%)
- **Total verified**: 128 instances (83.1%)

### Comparison

| Approach | Verified | Unverified | Improvement |
|----------|----------|------------|-------------|
| Polynomial-only | 48 (31.2%) | 106 (68.8%) | Baseline |
| Ford-Fulkerson | 128 (83.1%) | 26 (16.9%) | +80 verified cases |

## Comprehensive Testing

All 10 edge cases pass, including:
1. ✅ **Professor's example**: Multiple red vertices sharing common vertex to t
2. ✅ Simple direct path with red
3. ✅ Path must go s→r→t
4. ✅ Cases where we can't verify (correctly returns !?)
5. ✅ Source/target is red
6. ✅ Complex cases

See `comprehensive_test_some.py` for all test cases.

## Key Implementation Details

### Vertex Splitting
- Each vertex v becomes v_in (index v) and v_out (index v + n)
- Edge v_in → v_out has capacity 1 (ensures simple path)
- Original edge (u,v) becomes u_out → v_in

### Algorithm Flow
```
For each red vertex r:
  1. Build flow network for s → r (target r_in)
  2. Run Ford-Fulkerson to find path s → r
  3. If found:
     - Extract vertices used in s→r path (except r)
     - Build flow network for r → t (start from r_out)
     - Block vertices from s→r path
     - Run Ford-Fulkerson to find path r → t
  4. If both found: return True with combined path

If no path with red found:
  - Check if s-t path exists (BFS)
  - If no s-t path: return False (verifiable)
  - If s-t path exists: return !? (can't verify)
```

## Theoretical Analysis

### Why We Can't Solve 100% Correctly

The problem is **NP-hard**, which means:
- No polynomial-time algorithm can solve it correctly for all graphs (unless P=NP)
- Any polynomial-time algorithm will fail on some instances
- We can only guarantee correctness for special cases

### Why Our Approach Works Well

1. **Ford-Fulkerson is polynomial-time**: O(|R| * VE²)
2. **Works well in practice**: Solves 83% of instances with verified results
3. **Honest about limitations**: Returns "!?" when we can't verify
4. **Verifies when possible**: Returns "true"/"false" only when verifiable

### What We're Actually Doing

We're **not** solving an NP-hard problem correctly for 100% of cases. Instead:
- **For cases where we find a path**: We return "true" (verifiable)
- **For cases where no s-t path exists**: We return "false" (verifiable)
- **For cases where path exists but no red found**: We return "!?" (can't verify)

This is acceptable because:
1. The problem is NP-hard, so perfect correctness is impossible with polynomial-time
2. We're honest about uncertainty (return "!?" when can't verify)
3. We verify correctness when possible (83% of cases)

## Files

### Core Solvers
- `solvers/some.py`: Polynomial-time only (trees and DAGs)
- `solvers/some_ff.py`: Ford-Fulkerson with verification (recommended)

### Testing
- `comprehensive_test_some.py`: Comprehensive test suite with professor's example
- `compare_some_approaches.py`: Comparison script for both approaches

### Documentation
- `doc/SOME_Problem_Complete.md`: This file (complete documentation)
- `doc/Professor_Feedback_Analysis.md`: Detailed analysis of professor's feedback
- `doc/SOME_Literature_References.md`: Literature references for the report

## Recommendation

**Use `some_ff.py` as the primary solver** for the SOME problem.

It provides:
- 83% verified coverage (vs 31% for polynomial-only)
- Honest uncertainty reporting (!? when can't verify)
- All edge cases pass (including professor's example)
- Follows professor's guidance
- Polynomial-time efficiency

## Literature Reference

For the sophisticated hardness argument:
- **"On Existence of Must-Include Paths and Cycles in Undirected Graphs"**
- Authors: Yefim Dinitz and Solomon Eyal Shimony
- arXiv: 2302.09614
- Year: 2023

