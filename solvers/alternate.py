#!/usr/bin/env python3
"""
alternate.py
Problem ALTERNATE: does there exist an s-t path that alternates between red and non-red vertices?

A path v1, ..., vl is alternating if for each i ∈ {1, ..., l-1}, exactly one endpoint 
of the edge vivi+1 is red.

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
1. Filter edges: only keep edges where exactly one endpoint is red (alternating edges).
2. Run BFS from s to t on the filtered graph.
3. If a path exists, return "true" and the path; otherwise return "false".

Output:
- Prints "true" and a sample path (vertex names) if one exists.
- Prints "false" otherwise.
"""
import argparse
from collections import deque
import sys
import re

def read_graph_name_format(fname):
    with open(fname, "r", encoding="utf-8") as f:
        # read non-empty lines preserving order
        lines = [line.rstrip("\n") for line in f.readlines()]
    # strip BOM / whitespace lines
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
        # vertex name may be like "purls *" or "purls*"? spec says followed by " *"
        # accept both "name *" and "name*" just in case
        if vl.endswith("*"):
            # trim trailing '*' and whitespace
            base = vl[:-1].strip()
            names.append(base)
            R_names.add(base)
        else:
            names.append(vl)
    # Build mapping
    for i, nm in enumerate(names):
        name_to_idx[nm] = i

    # Validate r_count matches discovered red count (best-effort warning)
    if len(R_names) != r_count:
        # not fatal — data sometimes inconsistent; warn
        print(f"warning: r_count={r_count} but found {len(R_names)} red markers in vertex list", file=sys.stderr)

    # remaining lines are edges
    edge_lines = lines[2+n:]
    if len(edge_lines) < m:
        # allow fewer only if m==0; otherwise error
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

def build_alternating_adj(n, edges, R_idx_set, force_directed=False):
    """
    Build adjacency list containing only alternating edges.
    An edge (u, v) is alternating if exactly one of u or v is red.
    """
    adj = [[] for _ in range(n)]
    for u, v, directed in edges:
        # Check if edge is alternating: exactly one endpoint is red
        u_red = u in R_idx_set
        v_red = v in R_idx_set
        is_alternating = (u_red and not v_red) or (not u_red and v_red)
        
        if not is_alternating:
            continue  # Skip non-alternating edges
        
        if force_directed:
            # treat every edge as directed u->v
            adj[u].append(v)
        else:
            if directed:
                adj[u].append(v)
            else:
                # undirected: add both directions
                adj[u].append(v)
                adj[v].append(u)
    return adj

def bfs_alternating(adj, s_idx, t_idx):
    """
    Run BFS to find an s-t path in the alternating graph.
    Returns (found, path) where found is a boolean and path is a list of vertex indices.
    """
    n = len(adj)
    q = deque([s_idx])
    prev = [-1] * n
    visited = [False] * n
    visited[s_idx] = True

    while q:
        u = q.popleft()
        if u == t_idx:
            # Reconstruct path
            path = []
            x = t_idx
            while x != -1:
                path.append(x)
                x = prev[x]
            path.reverse()
            return True, path
        
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                prev[v] = u
                q.append(v)
    
    return False, []

def main():
    parser = argparse.ArgumentParser(description="ALTERNATE: does there exist an s-t path that alternates between red and non-red vertices? (name-based format)")
    parser.add_argument("input", help="input file (name-based format)")
    parser.add_argument("--force-directed", action="store_true",
                        help="treat every edge as directed u->v (ignores '--' undirected marker)")
    args = parser.parse_args()

    n, m, s_name, t_name, names, R_names, edges = read_graph_name_format(args.input)

    if s_name not in names or t_name not in names:
        print("Error: start or end vertex not present in vertex list.", file=sys.stderr)
        sys.exit(2)

    name_to_idx = {nm: i for i, nm in enumerate(names)}
    s_idx = name_to_idx[s_name]
    t_idx = name_to_idx[t_name]
    R_idx_set = set(name_to_idx[nm] for nm in R_names if nm in name_to_idx)

    # Build adjacency list with only alternating edges
    adj = build_alternating_adj(n, edges, R_idx_set, force_directed=args.force_directed)

    # Run BFS to find alternating path
    found, path_idx = bfs_alternating(adj, s_idx, t_idx)
    
    if found:
        print("true")
        print(" ".join(names[i] for i in path_idx))
    else:
        print("false")

if __name__ == "__main__":
    main()

