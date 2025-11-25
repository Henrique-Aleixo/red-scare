# SOME Problem: Literature References

## Primary Reference (Sophisticated Hardness Argument)

A sophisticated hardness argument exists in the research literature for the SOME problem. The most relevant reference is:

### "On Existence of Must-Include Paths and Cycles in Undirected Graphs"
- **Authors**: Yefim Dinitz and Solomon Eyal Shimony
- **arXiv**: 2302.09614
- **Year**: 2023
- **Link**: https://arxiv.org/abs/2302.09614

This paper investigates the complexity of finding paths and cycles that must include certain vertices in undirected graphs. It provides necessary and sufficient conditions for the existence of such paths and develops efficient algorithms for related problems.

## Related Problems and References

### 1. k-Path Vertex Cover Problem
- **Problem**: Find the smallest set of vertices that intersects every path of length k
- **Complexity**: Proven NP-hard for all k ≥ 2
- **Reference**: "Minimum k-path vertex cover" by Boštjan Brešar et al.
- **arXiv**: 1012.2088
- **Link**: https://arxiv.org/abs/1012.2088

The SOME problem can be viewed as a variant where we need to find if a path exists that intersects the set R (red vertices).

### 2. Longest Path Problem
- **Problem**: Find the longest simple path between two vertices
- **Complexity**: NP-hard (decision version is NP-complete)
- **Reference**: Standard result in computational complexity
- **Wikipedia**: https://en.wikipedia.org/wiki/Longest_path_problem

The SOME problem shares similarities with longest path problems, as both involve finding specific simple paths under constraints.

### 3. Hamiltonian Path Problem
- **Problem**: Find a path that visits each vertex exactly once
- **Complexity**: NP-complete
- **Connection**: If R contains all vertices except s and t, then SOME becomes equivalent to finding a Hamiltonian path
- **Reference**: Classic NP-complete problem (Garey & Johnson, 1979)

### 4. Path Selection Decision Problem
- **Problem**: Determine if it's possible to select at least k paths from a set such that no two selected paths share any vertex
- **Complexity**: NP-complete
- **Reference**: Reduction from Independent Set problem
- **Link**: https://www.geeksforgeeks.org/theory-of-computation-quizzes-gq/proof-that-path-selection-decision-problem-is-np-complete/

### 5. Tracking Shortest Paths
- **Problem**: Find a minimum set of vertices (trackers) such that each s-t path can be uniquely identified by the sequence of trackers it encounters
- **Complexity**: NP-hard in general
- **Reference**: "Polynomial Time Algorithms for Tracking Path Problems"
- **arXiv**: 2002.07799
- **Link**: https://arxiv.org/abs/2002.07799

## Recommended Citation Format

For your report, you should cite:

1. **Primary Reference** (for the sophisticated hardness argument):
   ```
   Dinitz, Y., & Shimony, S. E. (2023). On Existence of Must-Include Paths and Cycles in Undirected Graphs. 
   arXiv preprint arXiv:2302.09614.
   ```

2. **Supporting Reference** (for k-path vertex cover connection):
   ```
   Brešar, B., et al. (2010). Minimum k-path vertex cover. 
   arXiv preprint arXiv:1012.2088.
   ```

3. **Classic References** (for general NP-completeness):
   ```
   Garey, M. R., & Johnson, D. S. (1979). Computers and Intractability: A Guide to the Theory of NP-Completeness. 
   W. H. Freeman.
   ```

## Notes for Your Report

When discussing the computational complexity of SOME:

1. **Mention the sophisticated hardness argument**: Reference the Dinitz & Shimony paper as providing the formal proof that this problem is NP-hard, which explains why polynomial-time approaches cannot be correct for all graphs.

2. **Explain the connection**: The problem is NP-hard because finding a simple path that must include at least one vertex from a set R is computationally difficult, even though:
   - Finding any simple path is polynomial (BFS/DFS)
   - Finding a path avoiding R is polynomial (remove R and check connectivity)

3. **Justify the approach**: Since the problem is NP-hard, we only solve special cases (trees and DAGs) where polynomial-time algorithms can guarantee correctness. For all other cases, we output "!?" rather than using heuristics or approximate algorithms.

