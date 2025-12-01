# SOME Problem: Literature References

## The NP-Hardness Result

The SOME problem is NP-hard. The formal proof comes from:

**Dinitz, Y., & Shimony, S. E. (2023). On Existence of Must-Include Paths and Cycles in Undirected Graphs. arXiv preprint arXiv:2302.09614.**

This paper proves that finding a simple path that must include at least one vertex from a set R is computationally hard. While finding any simple path is easy (just use BFS), and finding a path that avoids R is also easy (remove R and check connectivity), requiring a path to include at least one vertex from R makes the problem NP-hard.
