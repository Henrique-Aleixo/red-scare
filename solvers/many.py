#!/usr/bin/env python3
"""
many.py
Problem MANY: maximize number of red vertices on any simple s--t path.

Notes:
- This problem is NP-hard in general (longest/simple path with vertex weights).
- This script provides polynomial-time solutions only for:
    * Trees: unique s-t path exists, count red vertices on that path.
    * DAGs: dynamic programming with topological sort.
- For all other instances, outputs "!?" (unsolved).

New input format (name-based):
n m r
s t
<vertices>           # n lines, vertex names ([_a-z0-9]+). If a vertex is red it ends with ' *'
<edges>              # m lines, each either "u -- v" (undirected) or "u -> v" (directed)

Behavior:
- Internally the script maps vertex names to indices.
- Edges are parsed by the connector in each line:
    --  => undirected (adds both directions)
    ->  => directed (u -> v only)
- By default the script honors per-edge directionality found in the file.
- You can force all edges to be treated as directed with --force-directed.

Implementation:
Uses polynomial-time algorithms only:
- Trees: DFS to find unique s-t path, count red vertices. O(n).
- DAGs: Topological sort + dynamic programming. O(n + m).
- Other graphs: Output "!?" (unsolved).

Usage:
    python many.py input.txt [--force-directed]

Output:
- If no s-t path exists, prints -1.
- If graph is a tree or DAG, prints the maximum number of red vertices and the path.
- Otherwise, prints "!?" (unsolved).
"""

import argparse
from collections import deque
import sys
import re

def read_graph_name_format(fname):
    """Read graph in name-based format (same as few.py, some.py, none.py)."""
    with open(fname, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f.readlines()]
    lines = [ln.strip() for ln in lines if ln.strip() != ""]

    if len(lines) < 2:
        raise ValueError("File too short: need at least two lines (header and s t).")

    # header: n m r
    header = lines[0].split()
    if len(header) < 3:
        raise ValueError("Header line must be: n m r")
    n = int(header[0]); m = int(header[1]); r_count = int(header[2])

    # s t on second line (names)
    st = lines[1].split()
    if len(st) < 2:
        raise ValueError("Second line must contain start and end vertex names.")
    s_name, t_name = st[0], st[1]

    # next n lines: vertex names (with optional trailing * for red)
    if len(lines) < 2 + n:
        raise ValueError(f"Expected {n} vertex lines after header; file has fewer.")
    vertex_lines = lines[2:2+n]

    names = []
    R_names = set()
    name_to_idx = {}
    for i, vl in enumerate(vertex_lines):
        if vl.endswith("*"):
            base = vl[:-1].strip()
            names.append(base)
            R_names.add(base)
        else:
            names.append(vl)
    for i, nm in enumerate(names):
        name_to_idx[nm] = i

    if len(R_names) != r_count:
        print(f"warning: r_count={r_count} but found {len(R_names)} red markers in vertex list", file=sys.stderr)

    # remaining lines are edges
    edge_lines = lines[2+n:]
    if len(edge_lines) < m:
        if m != 0:
            raise ValueError(f"Expected {m} edge lines but file has {len(edge_lines)}")
    edges = []  # list of (u_idx, v_idx, directed_bool)
    edge_re_arrow = re.compile(r'^\s*([_a-z0-9]+)\s*(->|--)\s*([_a-z0-9]+)\s*$')
    for el in edge_lines[:m]:
        mo = edge_re_arrow.match(el)
        if not mo:
            raise ValueError(f"Edge line has wrong format: '{el}' (expected 'u -- v' or 'u -> v')")
        u_name, conn, v_name = mo.group(1), mo.group(2), mo.group(3)
        if u_name not in name_to_idx or v_name not in name_to_idx:
            raise ValueError(f"Edge references unknown vertex: {u_name} or {v_name}")
        u = name_to_idx[u_name]; v = name_to_idx[v_name]
        directed = (conn == "->")
        edges.append((u, v, directed))

    return n, m, s_name, t_name, names, R_names, edges

def build_adj(n, edges, force_directed=False):
    """Build adjacency list from edges. Handles both directed and undirected edges."""
    adj = [[] for _ in range(n)]
    for u, v, directed in edges:
        if force_directed:
            adj[u].append(v)
        else:
            if directed:
                adj[u].append(v)
            else:
                adj[u].append(v)
                adj[v].append(u)
    return adj

# ----- Special Case Solvers (Polynomial Time) -----

def is_dag(adj, n):
    """Check if graph is a DAG using DFS cycle detection."""
    visited = [False] * n
    rec_stack = [False] * n
    
    def has_cycle(v):
        visited[v] = True
        rec_stack[v] = True
        for u in adj[v]:
            if not visited[u]:
                if has_cycle(u):
                    return True
            elif rec_stack[u]:
                return True
        rec_stack[v] = False
        return False
    
    for i in range(n):
        if not visited[i]:
            if has_cycle(i):
                return False
    return True

def solve_dag(adj, R, s, t, n):
    """Solve MANY for DAG using dynamic programming. O(n + m)."""
    # Topological sort using Kahn's algorithm
    in_degree = [0] * n
    for u in range(n):
        for v in adj[u]:
            in_degree[v] += 1
    
    q = deque([i for i in range(n) if in_degree[i] == 0])
    topo_order = []
    
    while q:
        u = q.popleft()
        topo_order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                q.append(v)
    
    # If we didn't process all vertices, there's a cycle (shouldn't happen if is_dag is correct)
    if len(topo_order) != n:
        return None, None
    
    # DP: dp[v] = max reds on path from s to v
    dp = [-1] * n
    parent = [-1] * n
    
    # Find s in topological order
    s_pos = topo_order.index(s) if s in topo_order else -1
    if s_pos == -1:
        return -1, None
    
    dp[s] = 1 if s in R else 0
    
    # Process vertices in topological order starting from s
    for i in range(s_pos, n):
        u = topo_order[i]
        if dp[u] == -1:
            continue  # unreachable from s
        for v in adj[u]:
            new_val = dp[u] + (1 if v in R else 0)
            if new_val > dp[v]:
                dp[v] = new_val
                parent[v] = u
    
    if dp[t] == -1:
        return -1, None
    
    # Reconstruct path
    path = []
    cur = t
    while cur != -1:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    
    return dp[t], path

def is_tree(adj, n):
    """Check if graph is a tree: connected and m = n-1."""
    # Count edges
    m = sum(len(adj[i]) for i in range(n))
    if n == 0:
        return True
    if m != 2 * (n - 1):  # For undirected, each edge counted twice
        return False
    
    # Check connectivity
    visited = [False] * n
    stack = [0]
    visited[0] = True
    count = 1
    
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                stack.append(v)
                count += 1
    
    return count == n

def solve_tree(adj, R, s, t, n):
    """Solve MANY for tree: unique s-t path exists. O(n)."""
    # DFS to find unique path from s to t
    visited = [False] * n
    path = []
    found = False
    
    def dfs(u, target):
        nonlocal found
        if found:
            return
        visited[u] = True
        path.append(u)
        if u == target:
            found = True
            return
        for v in adj[u]:
            if not visited[v]:
                dfs(v, target)
                if found:
                    return
        if not found:
            path.pop()
    
    dfs(s, t)
    
    if not found:
        return -1, None
    
    red_count = sum(1 for v in path if v in R)
    return red_count, path


# ----- CLI & orchestrator -----
def main():
    parser = argparse.ArgumentParser(description="MANY: maximize number of red vertices on an s-t simple path (polynomial-time only)")
    parser.add_argument("input", help="input file (name-based format)")
    parser.add_argument("--force-directed", action="store_true", help="treat all edges as directed")
    args = parser.parse_args()

    # Read graph in name-based format
    n, m, s_name, t_name, names, R_names, edges = read_graph_name_format(args.input)
    
    # Map names to indices
    name_to_idx = {nm: i for i, nm in enumerate(names)}
    if s_name not in name_to_idx or t_name not in name_to_idx:
        print("Error: start or end vertex not present in vertex list.", file=sys.stderr)
        sys.exit(2)
    
    s = name_to_idx[s_name]
    t = name_to_idx[t_name]
    R = set(name_to_idx[nm] for nm in R_names if nm in name_to_idx)
    
    # Build adjacency list
    adj = build_adj(n, edges, force_directed=args.force_directed)
    
    # Check if graph is all directed (for DAG detection)
    all_directed = all(directed for _, _, directed in edges)
    
    # Quick check: is there any s-t path at all (simple reachability)
    q = deque([s])
    seen = [False]*n
    seen[s] = True
    while q:
        v = q.popleft()
        for u in adj[v]:
            if not seen[u]:
                seen[u] = True
                q.append(u)
    if not seen[t]:
        print(-1)
        return

    # Check for special cases (polynomial-time solvers only)
    
    # Check if it's a tree
    if is_tree(adj, n):
        best_count, best_path = solve_tree(adj, R, s, t, n)
        if best_count == -1:
            print(-1)
        else:
            print(best_count)
            if best_path:
                # Convert indices back to names for output
                path_names = [names[v] for v in best_path]
                print(" ".join(path_names))
        return
    
    # Check if it's a DAG (only makes sense if all edges are directed)
    if all_directed and is_dag(adj, n):
        best_count, best_path = solve_dag(adj, R, s, t, n)
        if best_count is None:
            # Shouldn't happen if is_dag is correct, but output !? to be safe
            print("!?")
        elif best_count == -1:
            print(-1)
        else:
            print(best_count)
            if best_path:
                path_names = [names[v] for v in best_path]
                print(" ".join(path_names))
        return

    # For all other graphs (not tree, not DAG), output !? (unsolved)
    print("!?")

if __name__ == "__main__":
    main()
