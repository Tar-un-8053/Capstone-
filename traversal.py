"""Graph traversal: BFS, DFS, connected components, N-hop reachability. O(V + E)."""
from collections import deque
from src.graph_model import edge_key


def bfs(g, s, closed=frozenset()):
    """Return (visit order, hops from s). Closed roads are not traversed."""
    hops, order, q = {s: 0}, [], deque([s])
    while q:
        u = q.popleft(); order.append(u)
        for v, e in g.neighbors(u):
            if v not in hops and edge_key(e) not in closed:
                hops[v] = hops[u] + 1; q.append(v)
    return order, hops


def dfs(g, s, closed=frozenset()):
    """Iterative DFS; returns visit order."""
    seen, order, stack = set(), [], [s]
    while stack:
        u = stack.pop()
        if u in seen: continue
        seen.add(u); order.append(u)
        for v, e in reversed(g.neighbors(u)):
            if v not in seen and edge_key(e) not in closed:
                stack.append(v)
    return order


def components(g, closed=frozenset()):
    """Connected components = zones that can still reach each other after closures."""
    seen, comps = set(), []
    for n in g.nodes:
        if n not in seen:
            comp = bfs(g, n, closed)[0]
            seen.update(comp); comps.append(comp)
    return comps


def reachable_within(g, s, k, closed=frozenset()):
    return [n for n, h in bfs(g, s, closed)[1].items() if h <= k]
