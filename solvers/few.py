#!/usr/bin/env python3
"""
few.py
Problem FEW: find an s–t path minimizing the number of red vertices.

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
Transform vertex costs into edge weights using vertex splitting. Each vertex v is split
into v_in and v_out connected by an edge of weight 1 if v is red, 0 otherwise. Original
edges connect v_out to u_in with weight 0. Run Dijkstra's algorithm from s_out to t_out
to find the path minimizing the number of red vertices.

Output:
- Minimum number of red vertices on an s–t path.
- If no path exists, prints -1.
"""

import argparse
import heapq
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


def build_split_graph(n, edges, R, force_directed=False):
    """
    Create adjacency list for the vertex-split graph.
    Each vertex v becomes v_in = 2*v, v_out = 2*v + 1.
    Edge (v_in, v_out) has weight = cost(v).
    """
    N = 2 * n
    adj = [[] for _ in range(N)]

    for v in range(n):
        cost = 1 if v in R else 0
        adj[2*v].append((2*v + 1, cost))  # v_in -> v_out with vertex cost

    for u, v, directed in edges:
        if force_directed:
            # treat every edge as directed u->v
            adj[2*u + 1].append((2*v, 0))
        else:
            if directed:
                adj[2*u + 1].append((2*v, 0))
            else:
                # undirected: add both directions
                adj[2*u + 1].append((2*v, 0))
                adj[2*v + 1].append((2*u, 0))
    return adj


def dijkstra(adj, start, goal):
    dist = [float("inf")] * len(adj)
    dist[start] = 0
    pq = [(0, start)]

    while pq:
        d, v = heapq.heappop(pq)
        if d > dist[v]:
            continue
        if v == goal:
            return d
        for u, w in adj[v]:
            nd = d + w
            if nd < dist[u]:
                dist[u] = nd
                heapq.heappush(pq, (nd, u))
    return float("inf")


def main():
    parser = argparse.ArgumentParser(description="FEW: minimize number of red vertices on an s–t path (name-based format)")
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

    adj = build_split_graph(n, edges, R_idx_set, force_directed=args.force_directed)

    s_start = 2*s_idx + 1   # start from s_out (after paying cost if s is red)
    t_goal = 2*t_idx + 1    # reach t_out (after paying t's cost, so t is counted if red)
    best = dijkstra(adj, s_start, t_goal)

    if best == float("inf"):
        print(-1)
    else:
        print(best)

if __name__ == "__main__":
    main()
