# Professor's Feedback Analysis: SOME Problem

## What the Professor is Saying

### 1. **Debug First - Find Concrete Failures**

The professor wants us to:
- Find specific instances where we **know** the algorithm gives incorrect results
- Trace through the algorithm **by hand** on those instances
- Determine if it's:
  - **Implementation bug**: Algorithm is correct in theory, but code has a bug
  - **Algorithm design flaw**: The approach itself is wrong

**Action**: We need to identify test cases where Ford-Fulkerson returns "false" but we can prove a valid path with red exists.

### 2. **His Diagnosis of the Problem**

The professor suspects we're doing this (which matches what we identified):

```
Current (Problematic) Approach:
1. Find paths from s → R (all red vertices at once)
2. Then try to find paths from R → t

Problem: Finding multiple paths to different red vertices might block 
vertices needed for paths from red vertices to t.
```

**Example of the problem**:
```
Graph:
  s -- A -- r1
  s -- B -- r2
  r1 -- C -- t
  r2 -- C -- t

If we find paths s→A→r1 and s→B→r2 first:
- We block vertices A and B
- Then when trying r1→C→t, we might block C
- But r2→C→t also needs C, which is now blocked
- Even though s→A→r1→C→t would work!
```

### 3. **His Suggested Fix**

**Option A: Fix the Algorithm Logic**

Instead of finding all s→R paths first, do this for **each red vertex individually**:

```
For each red vertex r ∈ R:
  1. Run Ford-Fulkerson to find path s → r
  2. If found, run Ford-Fulkerson to find path r → t
  3. If both found, we have a valid path s→r→t
  4. If not, try next red vertex
```

**Key Point**: When using vertex splitting, be careful about which "r-node" you target:
- For path s→r: Target `r_in` (the input node of r in the split graph)
- For path r→t: Start from `r_out` (the output node of r in the split graph)

**Why this works**: By handling each red vertex separately, we don't block vertices that might be needed for other red vertices' paths.

**Option B: Modify the Graph Structure**

Instead of changing Ford-Fulkerson, modify the graph:
- Add new source/sink nodes
- Force paths to go s→r→t by restructuring the graph
- This is "not trivial" because paths a→b are not equivalent to b→a in residual graphs

## Our Options Moving Forward

### Option 1: **Stick with Polynomial-Time Only** (Current Approach)
- **Pros**: 
  - Guaranteed correctness
  - No heuristics
  - Clean and principled
- **Cons**: 
  - Only solves 31% of instances
  - Might be able to add more special cases (bipartite, bounded treewidth, etc.)

### Option 2: **Fix Ford-Fulkerson Implementation** (Professor's Suggestion)
- **Pros**: 
  - Should solve more instances correctly
  - Uses polynomial-time algorithm (Ford-Fulkerson is O(VE²))
  - If fixed correctly, should be reliable
- **Cons**: 
  - Need to debug and fix the implementation
  - Need to verify correctness on test cases
  - More complex code

### Option 3: **Hybrid Approach**
- Use polynomial-time special cases (trees, DAGs) when detected
- Use fixed Ford-Fulkerson for other cases
- Output "!?" only when we're truly uncertain

## Recommended Next Steps

### Step 1: **Create Test Cases with Known Answers**

Create small graphs where we can verify by hand:
- Graph where Ford-Fulkerson should return "true" but currently returns "false"
- Graph where Ford-Fulkerson should return "false" and does
- Graph where multiple red vertices exist and only some paths work

### Step 2: **Implement Professor's Fix**

Modify the algorithm to:
```
For each red vertex r:
  1. Build flow network for s → r (target r_in)
  2. Run Ford-Fulkerson to find path s → r
  3. If found:
     - Build flow network for r → t (start from r_out)
     - Block vertices used in s→r path (except r itself)
     - Run Ford-Fulkerson to find path r → t
  4. If both found, return true with combined path
```

### Step 3: **Test and Verify**

- Run on test cases from Step 1
- Verify by hand that results are correct
- Run on all 154 instances and compare with previous results

### Step 4: **Decide on Final Approach**

Based on results:
- If Ford-Fulkerson works correctly: Use it for non-special cases
- If still has issues: Stick with polynomial-time only or hybrid

## Key Implementation Details

### Vertex Splitting in Ford-Fulkerson

When we split vertex v:
- `v_in` = index v (input node)
- `v_out` = index v + n (output node)
- Edge `v_in → v_out` has capacity 1 (ensures simple path)

For path s → r:
- Source: `s_out` (s + n)
- Sink: `r_in` (r)

For path r → t:
- Source: `r_out` (r + n)  
- Sink: `t_in` (t)

**Critical**: When blocking vertices used in s→r path:
- Block the `v_in → v_out` edge for each used vertex v (except r)
- This prevents reusing those vertices in r→t path

## Questions to Answer

1. **Do we have instances where we know Ford-Fulkerson fails?**
   - If yes: Use them to debug
   - If no: Create test cases

2. **Should we implement the fix?**
   - Yes, if we want to solve more instances
   - No, if we prefer guaranteed correctness over coverage

3. **What's our priority?**
   - Maximum correctness (polynomial-time only)
   - Maximum coverage (fixed Ford-Fulkerson)
   - Balance (hybrid approach)

