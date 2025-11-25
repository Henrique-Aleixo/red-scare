#!/usr/bin/env python3
"""
some.py
Problem SOME: does there exist an s-t path that includes at least one vertex from R?

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
Uses polynomial-time algorithms only for special cases:
- Trees: Find unique s-t path, check if it includes any red vertex. O(n).
- DAGs: Dynamic programming to check if path with red exists. O(n + m).
- All other graphs: Output "!?" (unsolved).

Output:
- Prints "true" and a sample path if one exists (for solved cases).
- Prints "false" if no such path exists (for solved cases).
- Prints "!?" for unsolved cases.
"""
import argparse
from collections import deque
from typing import List, Set, Tuple, Optional
import sys
import re

def read_graph_name_format(fname):
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
    edges = []
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
    """Build adjacency list from edges."""
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

def is_connected(adj, n, s, t):
    """Check if t is reachable from s using BFS."""
    if s == t:
        return True
    visited = [False] * n
    q = deque([s])
    visited[s] = True
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v == t:
                return True
            if not visited[v]:
                visited[v] = True
                q.append(v)
    return False

def is_tree(adj, n):
    """Check if graph is a tree: connected and m = n-1."""
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
    """Solve SOME for tree: find unique s-t path and check if it includes red. O(n)."""
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
        return False, None
    
    # Check if path includes any red vertex
    has_red = any(v in R for v in path)
    return has_red, path

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
    """Solve SOME for DAG using dynamic programming. O(n + m).
    Returns (True, path) if path with red exists, (False, None) if path exists but no red, 
    (None, None) if no path exists.
    """
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
    
    if len(topo_order) != n:
        return None, None  # Not a DAG (shouldn't happen if is_dag is correct)
    
    # DP: dp[v] = True if there exists a path from s to v that includes at least one red vertex
    #     reachable[v] = True if v is reachable from s
    dp = [False] * n
    reachable = [False] * n
    parent = [-1] * n
    
    s_pos = topo_order.index(s) if s in topo_order else -1
    if s_pos == -1:
        return None, None
    
    reachable[s] = True
    if s in R:
        dp[s] = True
    
    # Process vertices in topological order starting from s
    for i in range(s_pos, n):
        u = topo_order[i]
        if not reachable[u]:
            continue
        
        for v in adj[u]:
            if not reachable[v]:
                reachable[v] = True
                parent[v] = u  # Track parent for all reachable vertices
            # Path from s to v has red if: path to u has red OR v is red
            if (dp[u] or v in R) and not dp[v]:
                dp[v] = True
                parent[v] = u  # Update parent when we find path with red
    
    if not reachable[t]:
        return None, None  # No path from s to t
    
    if dp[t]:
        # Reconstruct path with red
        path = []
        cur = t
        while cur != -1:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        return True, path
    else:
        return False, None

def main():
    parser = argparse.ArgumentParser(description="SOME: does there exist an s-t path that includes at least one vertex from R? (polynomial-time only)")
    parser.add_argument("input", help="input file (name-based format)")
    parser.add_argument("--force-directed", action="store_true",
                        help="treat every edge as directed u->v (ignores '--' undirected marker)")
    args = parser.parse_args()

    n, m, s_name, t_name, names, R_names, edges = read_graph_name_format(args.input)

    if s_name not in names or t_name not in names:
        print("Error: start or end vertex not present in vertex list.", file=sys.stderr)
        sys.exit(2)

    name_to_idx = {nm:i for i,nm in enumerate(names)}
    s_idx = name_to_idx[s_name]
    t_idx = name_to_idx[t_name]
    R_idx_set = set(name_to_idx[nm] for nm in R_names if nm in name_to_idx)

    adj = build_adj(n, edges, force_directed=args.force_directed)
    
    # Check if t is reachable from s
    if not is_connected(adj, n, s_idx, t_idx):
        print("false")
        return
    
    # Check for special cases (polynomial-time solvers only)
    
    # 1. Check if it's a tree
    if is_tree(adj, n):
        has_red, path = solve_tree(adj, R_idx_set, s_idx, t_idx, n)
        if path is None:
            print("false")
        elif has_red:
            print("true")
            path_names = [names[v] for v in path]
            print(" ".join(path_names))
        else:
            print("false")
        return
    
    # 2. Check if it's a DAG (only makes sense if all edges are directed)
    all_directed = all(directed for _, _, directed in edges) or args.force_directed
    if all_directed and is_dag(adj, n):
        result, path = solve_dag(adj, R_idx_set, s_idx, t_idx, n)
        if result is None:
            print("false")  # No path exists
        elif result:
            print("true")
            path_names = [names[v] for v in path]
            print(" ".join(path_names))
        else:
            print("false")
        return
    
    # 3. For all other graphs, output !? (unsolved)
    print("!?")

if __name__ == "__main__":
    main()
