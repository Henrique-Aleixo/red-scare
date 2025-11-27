# SOME Problem: Literature References

## The NP-Hardness Result

The SOME problem is NP-hard. The formal proof comes from:

**Dinitz, Y., & Shimony, S. E. (2023). On Existence of Must-Include Paths and Cycles in Undirected Graphs. arXiv preprint arXiv:2302.09614.**

This paper proves that finding a simple path that must include at least one vertex from a set R is computationally hard. While finding any simple path is easy (just use BFS), and finding a path that avoids R is also easy (remove R and check connectivity), requiring a path to include at least one vertex from R makes the problem NP-hard.

## Related Problems

The SOME problem relates to several well-known problems in graph theory:

**k-Path Vertex Cover**: Finding the smallest set of vertices that intersects every path of length k. This is NP-hard for k ≥ 2. The SOME problem asks whether a path exists that intersects the set R.

**Longest Path Problem**: Finding the longest simple path between two vertices is NP-hard. SOME shares similarities since both involve finding specific simple paths under constraints.

**Hamiltonian Path**: If R contains all vertices except s and t, then SOME becomes equivalent to finding a Hamiltonian path, which is NP-complete.

These connections help explain why SOME is hard - it combines aspects of these well-known difficult problems.

## Why This Matters

Since SOME is NP-hard, we can't solve it perfectly for all graphs in polynomial time (unless P=NP). That's why our polynomial-time approach only handles special cases like trees and DAGs, and why our Ford-Fulkerson approach sometimes returns "!?" when we can't verify the answer.
