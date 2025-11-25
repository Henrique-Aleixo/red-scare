#!/usr/bin/env python3
"""
some_ff.py
Problem SOME: does there exist an s-t path that includes at least one vertex from R?

Ford-Fulkerson approach:
- For each red vertex r individually:
  1. Run Ford-Fulkerson to find path s → r (target r_in)
  2. If found, run Ford-Fulkerson to find path r → t (start from r_out)
  3. Block vertices used in s→r path (except r itself) when finding r→t
  4. If both found, return true with combined path

Uses vertex splitting to ensure simple paths (no repeated vertices).

New input format (name-based):
n m r
s t
<vertices>           # n lines, vertex names ([_a-z0-9]+). If a vertex is red it ends with ' *'
<edges>              # m lines, each either "u -- v" (undirected) or "u -> v" (directed)

Output:
- Prints "true" and a sample path if one exists (verifiable - path includes red).
- Prints "false" if we can verify no such path exists (e.g., no s-t path at all).
- Prints "!?" if we cannot verify the result is correct.
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

def build_flow_network(n, adj, source_vertex, sink_vertex, blocked_vertices=None):
    """
    Build flow network with vertex splitting to ensure simple paths.
    
    Vertex splitting:
    - Each vertex v becomes v_in (index v) and v_out (index v + n)
    - v_in -> v_out has capacity 1 (ensures each vertex used at most once)
    - Original edge (u,v) becomes u_out -> v_in with capacity 1
    
    For path source -> sink:
    - Source: source_out (source + n)
    - Sink: sink_in (sink)
    
    Args:
        n: number of vertices in original graph
        adj: adjacency list of original graph
        source_vertex: source vertex index in original graph
        sink_vertex: sink vertex index in original graph
        blocked_vertices: set of vertex indices to block (by setting capacity to 0)
    
    Returns:
        flow_adj: adjacency list for flow network (2*n nodes)
        capacities: dict mapping (u, v) -> capacity
        source: source node in flow network
        sink: sink node in flow network
    """
    flow_n = 2 * n
    flow_adj = [[] for _ in range(flow_n)]
    capacities = {}
    
    # Vertex splitting: v_in -> v_out with capacity 1
    for v in range(n):
        v_in = v
        v_out = v + n
        
        # Block vertex if requested (set capacity to 0)
        if blocked_vertices is not None and v in blocked_vertices:
            capacities[(v_in, v_out)] = 0
        else:
            flow_adj[v_in].append(v_out)
            capacities[(v_in, v_out)] = 1
    
    # Original edges: u_out -> v_in with capacity 1
    for u in range(n):
        for v in adj[u]:
            u_out = u + n
            v_in = v
            flow_adj[u_out].append(v_in)
            capacities[(u_out, v_in)] = 1
    
    # Source is source_out, sink is sink_in
    source = source_vertex + n  # source_out
    sink = sink_vertex  # sink_in
    
    return flow_adj, capacities, source, sink

def find_augmenting_path(flow_adj, capacities, flow, source, sink):
    """
    Find augmenting path using BFS (Edmonds-Karp).
    Returns path if found, None otherwise.
    """
    parent = [-1] * len(flow_adj)
    visited = [False] * len(flow_adj)
    q = deque([source])
    visited[source] = True
    
    while q:
        u = q.popleft()
        if u == sink:
            # Reconstruct path
            path = []
            cur = sink
            while cur != -1:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            return path
        
        for v in flow_adj[u]:
            # Check if there's residual capacity
            residual = capacities.get((u, v), 0) - flow.get((u, v), 0)
            if residual > 0 and not visited[v]:
                visited[v] = True
                parent[v] = u
                q.append(v)
    
    return None

def extract_vertex_path(flow_path, n, source_vertex, sink_vertex):
    """
    Extract original vertex path from flow network path.
    
    Flow path goes from source (v_out node) to sink (v_in node).
    We extract all v_in nodes visited, plus the source vertex.
    """
    actual_path = []
    seen = set()
    
    # Add source vertex (since source is v_out, we need to add corresponding v_in)
    source_vertex_orig = source_vertex - n if source_vertex >= n else source_vertex
    if source_vertex_orig not in seen:
        actual_path.append(source_vertex_orig)
        seen.add(source_vertex_orig)
    
    # Add all v_in nodes in the path
    for node in flow_path:
        if node < n:  # v_in node
            v = node
            if v not in seen:
                actual_path.append(v)
                seen.add(v)
    
    return actual_path

def ford_fulkerson_path(flow_adj, capacities, source, sink):
    """
    Run Ford-Fulkerson (Edmonds-Karp) to find a single augmenting path.
    Returns the path if found, None otherwise.
    """
    flow = {}  # (u, v) -> flow value
    
    # Find one augmenting path
    path = find_augmenting_path(flow_adj, capacities, flow, source, sink)
    
    if path is None:
        return None
    
    # Augment flow along this path
    min_capacity = float('inf')
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        cap = capacities.get((u, v), 0)
        min_capacity = min(min_capacity, cap)
    
    # Update flow (though we don't actually need to track it for single path)
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        flow[(u, v)] = flow.get((u, v), 0) + min_capacity
        flow[(v, u)] = flow.get((v, u), 0) - min_capacity
    
    return path

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

def solve_some_ff(n, adj, s, t, R):
    """
    Solve SOME problem using Ford-Fulkerson approach.
    
    For each red vertex r:
    1. Find path s → r (target r_in)
    2. If found, find path r → t (start from r_out, block vertices from s→r)
    3. If both found, return true with combined path
    
    Returns: 
    - (True, path) if path with red exists (verifiable - path includes red)
    - (False, None) if we can verify no path exists (e.g., no s-t path at all)
    - (None, None) if we can't find a path but can't verify it doesn't exist (!?)
    """
    # First, check if there's a direct path s→t that includes red
    # (this handles the case where s or t is red, or path directly goes through red)
    flow_adj, capacities, source, sink = build_flow_network(n, adj, s, t)
    path = ford_fulkerson_path(flow_adj, capacities, source, sink)
    
    if path is not None:
        path_original = extract_vertex_path(path, n, source, sink)
        # Check if path includes any red vertex
        if any(v in R for v in path_original):
            return True, path_original
    
    # If no direct path with red, try s→r→t for each red vertex r
    for r in R:
        # Step 1: Find path s → r (target r_in)
        flow_adj_sr, capacities_sr, source_sr, sink_sr = build_flow_network(n, adj, s, r)
        path_sr = ford_fulkerson_path(flow_adj_sr, capacities_sr, source_sr, sink_sr)
        
        if path_sr is None:
            continue  # No path from s to r
        
        # Extract vertices used in s→r path (except r itself)
        path_sr_vertices = set(extract_vertex_path(path_sr, n, source_sr, sink_sr))
        path_sr_vertices.discard(r)  # Remove r, it's allowed in both paths
        
        # Step 2: Find path r → t (start from r_out, block vertices from s→r)
        flow_adj_rt, capacities_rt, source_rt, sink_rt = build_flow_network(
            n, adj, r, t, blocked_vertices=path_sr_vertices
        )
        path_rt = ford_fulkerson_path(flow_adj_rt, capacities_rt, source_rt, sink_rt)
        
        if path_rt is None:
            continue  # No path from r to t avoiding s→r vertices
        
        # Step 3: Combine paths s→r→t
        path_sr_orig = extract_vertex_path(path_sr, n, source_sr, sink_sr)
        path_rt_orig = extract_vertex_path(path_rt, n, source_rt, sink_rt)
        
        # Combine: path_sr_orig should end with r, path_rt_orig should start with r
        # Remove duplicate r when combining
        if path_sr_orig and path_sr_orig[-1] == r:
            combined_path = path_sr_orig[:-1] + path_rt_orig
        else:
            # If r not at end of first path, just combine (r should be in both)
            combined_path = path_sr_orig + [v for v in path_rt_orig if v != r]
        
        return True, combined_path
    
    # No path with red vertex found
    # Check if we can verify "false" is correct:
    # - If there's no path from s to t at all, then "false" is definitely correct
    if not is_connected(adj, n, s, t):
        return False, None  # No s-t path exists, so definitely false
    
    # Otherwise, we can't verify that "false" is correct
    # (maybe a path exists but we missed it due to algorithm limitations)
    return None, None  # Can't verify - return !?

def main():
    parser = argparse.ArgumentParser(
        description="SOME: does there exist an s-t path that includes at least one vertex from R? (Ford-Fulkerson approach)"
    )
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

    adj = build_adj(n, edges, force_directed=args.force_directed)

    result, path_idx = solve_some_ff(n, adj, s_idx, t_idx, R_idx_set)
    
    if result is True:
        print("true")
        print(" ".join(names[i] for i in path_idx))
    elif result is False:
        print("false")
    else:  # result is None - can't verify
        print("!?")

if __name__ == "__main__":
    main()

