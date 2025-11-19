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
Ford-Fulkerson (Edmonds-Karp) with vertex splitting to ensure simple paths.
This approach guarantees that paths found are simple (no repeated vertices) by modeling
vertex capacities as edge capacities in a flow network.

Key steps:
1. Vertex splitting: Each vertex v is split into v_in (index v) and v_out (index v+n),
   connected by an edge with capacity 1. This ensures each vertex can be used at most once.
2. Edge transformation: Original edges (u,v) become u_out -> v_in with capacity 1.
3. Flow network: Source is s_out (s+n), sink is t_in (t). We seek a flow of 1 from source to sink.
4. Augmenting paths: Use BFS (Edmonds-Karp) to find augmenting paths in the residual graph.
   Each augmenting path corresponds to a simple s-t path in the original graph.
5. Red vertex check: For each augmenting path found, check if it includes at least one red vertex.
   If a direct path doesn't use red, we check for paths s->r->t for each red vertex r,
   ensuring the combined path is simple by blocking vertices used in the first segment.

Output:
- Prints "true" and a sample path (vertex names) if one exists.
- Prints "false" otherwise.
"""
import argparse
from collections import deque
from typing import List, Set, Tuple
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
    rev = [[] for _ in range(n)]
    for u, v, directed in edges:
        if force_directed:
            # treat every edge as directed u->v
            adj[u].append(v)
            rev[v].append(u)
        else:
            if directed:
                adj[u].append(v)
                rev[v].append(u)
            else:
                adj[u].append(v); adj[v].append(u)
                rev[u].append(v); rev[v].append(u)
    return adj, rev

def build_flow_network(n, adj, s, t):
    """
    Build flow network with vertex splitting to ensure simple paths.
    Each vertex v becomes v_in (index v) and v_out (index v + n).
    - v_in -> v_out has capacity 1 (vertex capacity)
    - Original edge (u,v) becomes u_out -> v_in with capacity 1
    - Source is s_out (s + n), sink is t_in (t)
    Returns: flow_adj (adjacency list for flow network), capacities dict
    """
    # Flow network has 2*n nodes: 0..n-1 are v_in, n..2*n-1 are v_out
    flow_n = 2 * n
    flow_adj = [[] for _ in range(flow_n)]
    capacities = {}  # (u, v) -> capacity
    
    # Vertex splitting: v_in -> v_out with capacity 1
    for v in range(n):
        v_in = v
        v_out = v + n
        flow_adj[v_in].append(v_out)
        capacities[(v_in, v_out)] = 1
    
    # Original edges: u_out -> v_in with capacity 1
    for u in range(n):
        for v in adj[u]:
            u_out = u + n
            v_in = v
            flow_adj[u_out].append(v_in)
            capacities[(u_out, v_in)] = 1
    
    # Source is s_out, sink is t_in
    source = s + n  # s_out
    sink = t  # t_in
    
    return flow_adj, capacities, source, sink

def find_augmenting_path(flow_adj, capacities, flow, source, sink, n, R):
    """
    Find augmenting path using BFS (Edmonds-Karp).
    Returns path if found, None otherwise.
    Also tracks if path uses any red vertex.
    """
    parent = [-1] * len(flow_adj)
    visited = [False] * len(flow_adj)
    q = deque([source])
    visited[source] = True
    parent[source] = -1
    
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

def extract_vertex_path(path, n, source, sink):
    """Extract original vertex path from flow network path.
    Path goes from source (v_out node) to sink (v_in node).
    We extract all v_in nodes visited, plus the source vertex if source is v_out.
    """
    actual_path = []
    seen = set()
    
    # If source is a v_out node (>= n), add the corresponding v_in
    if source >= n:
        source_vertex = source - n
        actual_path.append(source_vertex)
        seen.add(source_vertex)
    
    # Add all v_in nodes in the path
    for node in path:
        if node < n:  # v_in node
            v = node
            if v not in seen:
                actual_path.append(v)
                seen.add(v)
    
    return actual_path

def ford_fulkerson_some(n, adj, s, t, R) -> Tuple[bool, List[int]]:
    """
    Ford-Fulkerson (Edmonds-Karp) to find simple s-t path that includes at least one red vertex.
    Uses vertex splitting to ensure simple paths.
    Strategy: Find augmenting paths until we find one that uses a red vertex.
    """
    flow_adj, capacities, source, sink = build_flow_network(n, adj, s, t)
    flow = {}  # (u, v) -> flow value
    
    # Try to find augmenting paths, checking each for red vertex usage
    max_iterations = n  # Limit iterations (Edmonds-Karp is O(VE^2) but we limit to n paths)
    
    for iteration in range(max_iterations):
        path = find_augmenting_path(flow_adj, capacities, flow, source, sink, n, R)
        if path is None:
            # No more augmenting paths
            break
        
        # Extract original vertex path and check if it uses red
        path_original = extract_vertex_path(path, n, source, sink)
        uses_red = any(v in R for v in path_original)
        
        # Augment flow along this path
        min_capacity = float('inf')
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            cap = capacities.get((u, v), 0)
            min_capacity = min(min_capacity, cap)
        
        # Update flow
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            flow[(u, v)] = flow.get((u, v), 0) + min_capacity
            flow[(v, u)] = flow.get((v, u), 0) - min_capacity
        
        # If this path uses a red vertex, we're done!
        if uses_red:
            return True, path_original
    
    # If we exhausted all augmenting paths and none used red, check if there's
    # a path s -> r -> t for any red r (ensuring simple path overall)
    # We do this by checking if we can find a simple path from s to r and from r to t
    # that don't share any vertices (except r)
    for r in R:
        # Check if there's a simple path s -> r -> t
        # Build flow network from s to r, and from r to t
        # If both have flow > 0 and the paths don't share vertices (except r), we're done
        
        # Check s -> r path
        flow_sr, capacities_sr, source_sr, sink_sr = build_flow_network(n, adj, s, r)
        flow_sr_dict = {}
        path_sr = find_augmenting_path(flow_sr, capacities_sr, flow_sr_dict, source_sr, sink_sr, n, R)
        if path_sr is None:
            continue  # No path from s to r
        
        # Check r -> t path, but we need to avoid vertices used in s->r path (except r)
        path_sr_vertices = set(extract_vertex_path(path_sr, n, source_sr, sink_sr))
        path_sr_vertices.discard(r)  # Remove r, it's allowed in both paths
        
        # Build flow network for r->t, but block vertices used in s->r (except r)
        # We can do this by setting capacities to 0 for those vertices' in->out edges
        flow_rt, capacities_rt, source_rt, sink_rt = build_flow_network(n, adj, r, t)
        # Block vertices used in s->r path (except r itself)
        for v in path_sr_vertices:
            v_in = v
            v_out = v + n
            capacities_rt[(v_in, v_out)] = 0  # Block this vertex
        
        flow_rt_dict = {}
        path_rt = find_augmenting_path(flow_rt, capacities_rt, flow_rt_dict, source_rt, sink_rt, n, R)
        if path_rt is None:
            continue  # No path from r to t avoiding s->r vertices
        
        # Combine paths: s->r->t
        path_sr_orig = extract_vertex_path(path_sr, n, source_sr, sink_sr)
        path_rt_orig = extract_vertex_path(path_rt, n, source_rt, sink_rt)
        # Combine paths: path_sr_orig should end with r, path_rt_orig should start with r
        # Remove duplicate r when combining
        if path_sr_orig and path_sr_orig[-1] == r:
            combined_path = path_sr_orig[:-1] + path_rt_orig
        else:
            # If r not at end of first path, just combine (r should be in both)
            combined_path = path_sr_orig + [v for v in path_rt_orig if v != r]
        return True, combined_path
    
    # If no augmenting path found at all, no s-t path exists
    return False, []

def main():
    parser = argparse.ArgumentParser(description="SOME: does there exist an s-t path that includes at least one vertex from R? (name-based format)")
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

    adj, _ = build_adj_from_edges(n, edges, force_directed=args.force_directed)

    ok, path_idx = ford_fulkerson_some(n, adj, s_idx, t_idx, R_idx_set)
    if ok:
        print("true")
        print(" ".join(names[i] for i in path_idx))
    else:
        print("false")

if __name__ == "__main__":
    main()
