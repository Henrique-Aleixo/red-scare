#!/usr/bin/env python3
"""
none.py — Problem NONE: shortest s-t path that internally avoids R.

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
- Output:
    If path exists: prints length (edge count) on one line, then the path (vertex names) on next.
    If no such path: prints -1

Example:
    python3 none.py data/common-1-20.txt
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

def build_adj_from_edges(n, edges, force_directed=False):
    adj = [[] for _ in range(n)]
    for u, v, directed in edges:
        if force_directed:
            # treat every edge as directed u->v
            adj[u].append(v)
        else:
            if directed:
                adj[u].append(v)
            else:
                adj[u].append(v); adj[v].append(u)
    return adj

def bfs_no_internal_red(adj, s_idx, t_idx, R_idx_set):
    n = len(adj)
    allowed = [True]*n
    for v in range(n):
        if v in R_idx_set and v != s_idx and v != t_idx:
            allowed[v] = False

    q = deque([s_idx])
    prev = [-1]*n
    visited = [False]*n
    visited[s_idx] = True

    while q:
        u = q.popleft()
        if u == t_idx:
            break
        for v in adj[u]:
            if not allowed[v]:
                continue
            if not visited[v]:
                visited[v] = True
                prev[v] = u
                q.append(v)

    if not visited[t_idx]:
        return -1, None

    # reconstruct path indices
    path = []
    x = t_idx
    while x != -1:
        path.append(x)
        x = prev[x]
    path.reverse()
    length = len(path) - 1
    return length, path

def main():
    parser = argparse.ArgumentParser(description="NONE: shortest s-t path that internally avoids R (name-based format)")
    parser.add_argument("input", help="input file (name-based format)")
    parser.add_argument("--force-directed", action="store_true",
                        help="treat every edge as directed u->v (ignores '--' undirected marker)")
    args = parser.parse_args()

    n, m, s_name, t_name, names, R_names, edges = read_graph_name_format(args.input)

    if s_name not in names or t_name not in names:
        print("Error: start or end vertex not present in vertex list.", file=sys.stderr)
        sys.exit(2)

    name_to_idx = {nm:i for i,nm in enumerate(names)}
    s_idx = name_to_idx[s_name]; t_idx = name_to_idx[t_name]
    R_idx_set = set(name_to_idx[nm] for nm in R_names if nm in name_to_idx)

    adj = build_adj_from_edges(n, edges, force_directed=args.force_directed)

    length, path_idx = bfs_no_internal_red(adj, s_idx, t_idx, R_idx_set)
    if length == -1:
        print(-1)
        return

    # print length and path as original names
    print(length)
    print(" ".join(names[i] for i in path_idx))

if __name__ == "__main__":
    main()
