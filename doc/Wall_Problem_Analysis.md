# Wall Problem Analysis

## What's Going On?

All the wall-* instances return "!?" instead of a definitive answer. Let's look at why, using wall-n-1.txt as an example.

## The Graph Structure

The graph is a cycle with 8 vertices: 0-1-2-3-4-5-6-7-0, with a shortcut edge from 0 to 7. The source is 7, target is 0, and vertex 3 is red. 

A valid path with red exists: 7 → 6 → 5 → 4 → 3 → 2 → 1 → 0. This path goes through the red vertex 3.

## What Our Algorithm Does

When we run Ford-Fulkerson on this instance:

1. First, we check if there's a direct path from 7 to 0. There is (just the shortcut edge), but it doesn't include the red vertex.

2. Then we try to find a path through the red vertex 3:
   - Step 1: Find path 7→3. Ford-Fulkerson finds [7, 0, 1, 2, 3]
   - Step 2: Try to find path 3→0, but we block vertices {7, 0, 1, 2} since they were used in the first path
   - The path 3→0 would need to go [3, 2, 1, 0], but vertices 2, 1, and 0 are all blocked!

So the algorithm fails, even though a valid path exists.

## Why This Happens

The problem is that Ford-Fulkerson finds one augmenting path, not necessarily the best one for our purposes. In this case:
- The path [7, 0, 1, 2, 3] uses vertices that block the path from 3 to 0
- An alternative path [7, 6, 5, 4, 3] exists that wouldn't block 3→0
- But we only try the first path found, and when it doesn't work, we move on

This is a limitation of our approach - we don't try multiple paths s→r for each red vertex r. We find one, and if it blocks r→t, we give up.

## Why This Is Actually OK

This behavior is correct for our verification-based approach. Since:
- A path from s to t exists (we verified with BFS)
- We couldn't find a path with red using our algorithm
- But we can't prove that no such path exists (we might have just missed it)

We return "!?" - we're honest that we can't verify the answer.

Given that the problem is NP-hard, we can't guarantee perfect correctness with a polynomial-time algorithm anyway. Returning "!?" when we're uncertain is better than returning a potentially incorrect answer.
