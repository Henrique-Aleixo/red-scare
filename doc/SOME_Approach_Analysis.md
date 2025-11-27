# SOME Problem Approach Analysis

## The Problem We Faced

When we first implemented the Ford-Fulkerson approach for SOME, we ran into an issue. The naive approach was to find all paths from s to red vertices first, then try to connect those red vertices to t. But this created blocking problems - vertices needed for one path would get blocked by another.

Take this example:
```
s -- A -- r1
s -- B -- r2
r1 -- C -- t
r2 -- C -- t
```

If we find paths s→A→r1 and s→B→r2 first, we block vertices A and B. Then when trying to find paths from r1 and r2 to t, we might block C while processing r1, which prevents r2 from using it. Even though s→A→r1→C→t would work fine if we just processed r1 individually!

## Our Solution

Instead of trying to find all paths to all red vertices at once, we process each red vertex individually. For each red vertex r:

1. Find a path from s to r
2. If found, find a path from r to t (making sure not to reuse vertices from the first path, except r itself)
3. If both paths exist, we're done - return true

This way, we don't create conflicts between different red vertices. When we're looking for a path through r1, we're not blocking things needed for r2, and vice versa.

## Vertex Splitting Details

We use vertex splitting to ensure we only use each vertex once. Each vertex v becomes two nodes: v_in and v_out, connected by an edge with capacity 1. Original edges become connections from u_out to v_in.

When looking for a path s→r, we target r_in. When looking for a path r→t, we start from r_out. This ensures that if we use vertex r in the first path, we can still use it as the connection point for the second path.

## Why We Return "!?" Sometimes

Even with this approach, we can't always verify the answer. Here's when we return what:

- **"true"**: We found a path that includes a red vertex. This is verifiable - we can show you the path.
- **"false"**: No path exists from s to t at all. This is verifiable - we can prove it with BFS.
- **"!?"**: A path exists from s to t, but we couldn't find one that includes a red vertex. Since the problem is NP-hard, we can't be sure that no such path exists - we might just have missed it.

The wall problems are a good example of this. The algorithm finds one path s→r, and if that path blocks r→t, we give up. But there might be another path s→r that wouldn't block r→t. Finding all such paths would be exponential, so we return "!?" - we're honest that we're not sure.

## Results

This approach solved 128 out of 154 instances with verified results (83.1%). That's a big improvement over the polynomial-time only approach which only handled 31.2%. The remaining 26 instances return "!?" because we can't verify them, but that's acceptable given the NP-hardness of the problem.
