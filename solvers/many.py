#!/usr/bin/env python3
"""
many.py
Problem MANY: maximize number of red vertices on any simple s--t path.

Notes:
- This problem is NP-hard in general (longest/simple path with vertex weights).
- This script provides:
    * An exact DFS/backtracking solver with pruning (branch-and-bound).
    * A greedy heuristic and a beam-search heuristic for larger instances.
    * Timeout support: stop after --timeout seconds and return best-so-far.
- Input format (same as other scripts):
n m
s t
r_count r1 r2 ... r_r_count
u1 v1
...
um vm
- Default: undirected graph. Use --directed for directed graphs.

Usage examples:
    python many.py input.txt --exact --timeout 10
    python many.py input.txt --heuristic greedy
    python many.py input.txt --beam 50 --timeout 5

Output:
- If no s-t path exists, prints -1.
- Otherwise prints the maximum number of red vertices found and a path achieving it (best-so-far).
"""

import argparse
import time
from collections import deque, defaultdict
import heapq
import random
import sys

def read_graph(fname):
    with open(fname) as f:
        parts = f.read().strip().split()
    if len(parts) < 5:
        raise ValueError("Input too short / wrong format.")
    it = iter(parts)
    n = int(next(it)); m = int(next(it))
    s = int(next(it)); t = int(next(it))
    r_count = int(next(it))
    R = set()
    for _ in range(r_count):
        R.add(int(next(it)))
    edges = []
    for _ in range(m):
        try:
            u = int(next(it)); v = int(next(it))
        except StopIteration:
            raise ValueError("Not enough edge tokens for m edges.")
        edges.append((u, v))
    return n, m, s, t, R, edges

def build_adj(n, edges, directed=False):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        if not directed:
            adj[v].append(u)
    return adj

def reachable_reds_upper_bound(adj, R, current, visited, t):
    """
    Compute an upper bound on how many additional red vertices can be
    collected along any simple path from `current` to `t`, ignoring
    order constraints but respecting not revisiting 'visited' nodes.
    We'll BFS from current to find nodes reachable without touching visited,
    then count how many red nodes among them that can also reach t (via reversed BFS).
    This is a cheap but effective admissible heuristic (upper bound).
    """
    n = len(adj)
    # BFS from current avoiding visited to get reachable set
    q = deque([current])
    seen = set([current])  # allow current even if visited? current shouldn't be in visited typically
    forbidden = set(visited)
    reachable = set()
    while q:
        v = q.popleft()
        if v in forbidden:
            continue
        reachable.add(v)
        for u in adj[v]:
            if u not in seen and u not in forbidden:
                seen.add(u); q.append(u)

    # If t not reachable at all, upper bound is -inf (no s-t path)
    if t not in reachable:
        # But maybe t is reachable via nodes that were forbidden; caller should handle no-path separately
        # Return 0 as conservative upper bound for red count on s->t via allowed nodes.
        return 0

    # Count reds in reachable (excluding already visited)
    return sum(1 for v in reachable if v in R and v not in forbidden)

def exact_dfs(adj, R, s, t, timeout, directed=False):
    """
    Backtracking DFS exploring simple paths from s to t.
    Uses pruning: if current_reds + upper_bound_reachable <= best_found then prune.
    Returns best_count, best_path.
    """
    start_time = time.time()
    n = len(adj)
    best_count = -1
    best_path = None

    # Precompute nodes that can reach t (reverse BFS), to prune whole unreachable branches.
    rev = [[] for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            rev[v].append(u)
    q = deque([t])
    can_reach_t = [False]*n
    can_reach_t[t] = True
    while q:
        v = q.popleft()
        for u in rev[v]:
            if not can_reach_t[u]:
                can_reach_t[u] = True
                q.append(u)

    if not can_reach_t[s]:
        return -1, None  # no s-t path at all

    visited = [False]*n
    path = []

    # Order neighbors by heuristic: prefer neighbors that are red (more promising)
    def neighbors_order(v):
        neigh = adj[v]
        # sort by (is_red, degree) descending so red and low-degree first
        return sorted(neigh, key=lambda x: ((x in R), -len(adj[x])), reverse=True)

    sys.setrecursionlimit(10000)
    nodes_explored = 0

    def dfs(v, current_reds):
        nonlocal best_count, best_path, nodes_explored
        # timeout check
        if time.time() - start_time > timeout:
            return True  # signal timeout up the stack

        nodes_explored += 1

        # If v cannot reach t at all (via unused nodes), prune
        if not can_reach_t[v]:
            return False

        # Upper bound: count of red nodes reachable from v (excluding visited)
        ub = current_reds + reachable_reds_upper_bound(adj, R, v, {i for i,vis in enumerate(visited) if vis}, t)
        if ub <= best_count:
            return False

        if v == t:
            if current_reds > best_count:
                best_count = current_reds
                best_path = list(path)
            return False

        for u in neighbors_order(v):
            if visited[u]:
                continue
            # small local pruning: if u cannot reach t skip
            if not can_reach_t[u]:
                continue
            visited[u] = True
            path.append(u)
            added = 1 if u in R else 0
            timed_out = dfs(u, current_reds + added)
            if timed_out:
                return True
            path.pop()
            visited[u] = False
        return False

    visited[s] = True
    path.append(s)
    _timed_out = dfs(s, 1 if s in R else 0)
    # _timed_out True means we hit timeout. We still return best-so-far.
    # print(f"nodes_explored={nodes_explored}", file=sys.stderr)
    return best_count, best_path

# ----- Heuristics -----
def greedy_max_red(adj, R, s, t, max_steps=10000):
    """
    Greedy walk: progressively extend path choosing an unvisited neighbor that
    maximizes immediate gain (is red) and keeps t reachable. Random tie-breaking.
    Repeat several random restarts (shuffle neighbor order) and keep best path found.
    """
    n = len(adj)
    rev = [[] for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            rev[v].append(u)
    # Precompute can_reach_t from every node ignoring visited (used as quick check)
    q = deque([t])
    can_reach_t = [False]*n
    can_reach_t[t] = True
    while q:
        v = q.popleft()
        for u in rev[v]:
            if not can_reach_t[u]:
                can_reach_t[u] = True
                q.append(u)

    if not can_reach_t[s]:
        return -1, None

    best_count = -1; best_path = None
    attempts = 50
    for attempt in range(attempts):
        visited = [False]*n
        path = [s]
        visited[s] = True
        cur = s
        cur_reds = 1 if s in R else 0
        steps = 0
        while cur != t and steps < max_steps:
            nbrs = [u for u in adj[cur] if not visited[u] and can_reach_t[u]]
            if not nbrs:
                break
            # prefer red neighbors, tie-break by random
            red_n = [u for u in nbrs if u in R]
            if red_n:
                u = random.choice(red_n)
            else:
                u = random.choice(nbrs)
            path.append(u); visited[u]=True
            if u in R: cur_reds += 1
            cur = u
            steps += 1
        if cur == t and cur_reds > best_count:
            best_count = cur_reds
            best_path = list(path)
    return best_count, best_path

def beam_search(adj, R, s, t, beam_width=50, max_depth=2000):
    """
    Beam search on simple paths, scoring by number of reds collected so far + optimistic estimate.
    Maintains only 'beam_width' best partial paths per depth.
    """
    n = len(adj)
    # Precompute can_reach_t (simple)
    rev = [[] for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            rev[v].append(u)
    q = deque([t])
    can_reach_t = [False]*n
    can_reach_t[t] = True
    while q:
        v = q.popleft()
        for u in rev[v]:
            if not can_reach_t[u]:
                can_reach_t[u] = True
                q.append(u)
    if not can_reach_t[s]:
        return -1, None

    # Beam: list of tuples (score, reds_count, path, visited_set)
    start_score = 1 if s in R else 0
    beam = [(start_score, start_score, [s], set([s]))]
    best_count = -1; best_path = None

    for depth in range(max_depth):
        candidates = []
        for score, reds, path, visited in beam:
            cur = path[-1]
            if cur == t:
                if reds > best_count:
                    best_count = reds; best_path = list(path)
                # don't expand finished paths
                candidates.append((score, reds, path, visited))
                continue
            for u in adj[cur]:
                if u in visited: continue
                if not can_reach_t[u]: continue
                new_visited = set(visited)
                new_visited.add(u)
                new_path = list(path); new_path.append(u)
                new_reds = reds + (1 if u in R else 0)
                # optimistic estimate: add number of reds reachable from u (cheap upper bound)
                optimistic = new_reds + reachable_reds_upper_bound(adj, R, u, new_visited, t)
                candidates.append((optimistic, new_reds, new_path, new_visited))
        if not candidates:
            break
        # pick top beam_width by optimistic score
        candidates.sort(key=lambda x: x[0], reverse=True)
        beam = candidates[:beam_width]
        # update best if any path reached t
        for _, reds, path, _ in beam:
            if path[-1] == t and reds > best_count:
                best_count = reds; best_path = list(path)
    return best_count, best_path

# ----- CLI & orchestrator -----
def main():
    parser = argparse.ArgumentParser(description="MANY: maximize number of red vertices on an s-t simple path")
    parser.add_argument("input", help="input file")
    parser.add_argument("--directed", action="store_true", help="treat edges as directed")
    parser.add_argument("--exact", action="store_true", help="run exact backtracking (may be slow)")
    parser.add_argument("--heuristic", choices=["greedy", "beam"], default="beam", help="heuristic to use when not exact")
    parser.add_argument("--timeout", type=float, default=5.0, help="timeout in seconds (for exact/backtracking); returns best-so-far")
    parser.add_argument("--beam", type=int, default=100, help="beam width for beam search")
    args = parser.parse_args()

    n, m, s, t, R, edges = read_graph(args.input)
    adj = build_adj(n, edges, directed=args.directed)

    # Quick check: is there any s-t path at all (simple reachability)
    q = deque([s])
    seen = [False]*n
    seen[s] = True
    while q:
        v = q.popleft()
        for u in adj[v]:
            if not seen[u]:
                seen[u] = True; q.append(u)
    if not seen[t]:
        print(-1)
        return

    if args.exact:
        best_count, best_path = exact_dfs(adj, R, s, t, timeout=args.timeout, directed=args.directed)
        if best_count == -1:
            print(-1)
            return
        if best_path is None:
            # no complete path found before timeout but s->t exists; best_count may be -1
            print(best_count if best_count>=0 else -1)
            if best_path:
                print(" ".join(map(str,best_path)))
            return
        print(best_count)
        print(" ".join(map(str, best_path)))
        return

    # heuristics
    if args.heuristic == "greedy":
        best_count, best_path = greedy_max_red(adj, R, s, t)
    else:
        best_count, best_path = beam_search(adj, R, s, t, beam_width=args.beam)

    if best_count == -1:
        print(-1)
    else:
        print(best_count)
        if best_path:
            print(" ".join(map(str, best_path)))

if __name__ == "__main__":
    main()
