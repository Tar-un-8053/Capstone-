"""Shortest path: Dijkstra, A*, Bellman-Ford + alternative-route finder.
Every function takes a weight function w(edge) (see traffic.weight_fn); w == inf means the road is closed."""
import heapq, math
from src.graph_model import edge_key

INF = math.inf


def _result(dist, prev, s, t, explored):
    if t not in dist:
        return {"cost": INF, "path": [], "explored": explored}
    path, u = [t], t
    while u != s:
        u = prev[u]; path.append(u)
    return {"cost": dist[t], "path": path[::-1], "explored": explored}


def dijkstra(g, s, t, w):
    """O((V+E) log V) with a binary heap."""
    dist, prev, done, pq = {s: 0}, {}, set(), [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if u in done: continue
        done.add(u)
        if u == t: break
        for v, e in g.neighbors(u):
            c = w(e)
            if c == INF: continue
            if d + c < dist.get(v, INF):
                dist[v] = d + c; prev[v] = u
                heapq.heappush(pq, (d + c, v))
    return _result(dist, prev, s, t, len(done))


def astar(g, s, t, w):
    """A* with a Euclidean heuristic scaled by the cheapest cost-per-unit-length (keeps it admissible)."""
    scale = min((w(e) / max(g.euclid(e.u, e.v), 1e-9) for e in g.edges if w(e) < INF), default=0)
    h = lambda n: g.euclid(n, t) * scale
    dist, prev, done, pq = {s: 0}, {}, set(), [(h(s), s)]
    while pq:
        _, u = heapq.heappop(pq)
        if u in done: continue
        done.add(u)
        if u == t: break
        for v, e in g.neighbors(u):
            c = w(e)
            if c == INF: continue
            nd = dist[u] + c
            if nd < dist.get(v, INF):
                dist[v] = nd; prev[v] = u
                heapq.heappush(pq, (nd + h(v), v))
    return _result(dist, prev, s, t, len(done))


def bellman_ford(g, s, t, w):
    """O(VE). Slower, kept for comparison / validation."""
    dist, prev = {n: INF for n in g.nodes}, {}
    dist[s] = 0
    for _ in range(len(g.nodes) - 1):
        changed = False
        for e in g.edges:
            c = w(e)
            if c == INF: continue
            for a, b in ((e.u, e.v), (e.v, e.u)):
                if dist[a] + c < dist[b]:
                    dist[b] = dist[a] + c; prev[b] = a; changed = True
        if not changed: break
    dist = {n: d for n, d in dist.items() if d < INF}
    return _result(dist, prev, s, t, len(g.nodes))


def alternative_route(g, s, t, w, penalty=1.5):
    """Find a second-best route: penalise roads of the best route, re-run Dijkstra, report the real cost."""
    best = dijkstra(g, s, t, w)
    if not best["path"]: return best
    used = {frozenset(p) for p in zip(best["path"], best["path"][1:])}
    w2 = lambda e: w(e) * penalty if edge_key(e) in used else w(e)
    alt = dijkstra(g, s, t, w2)
    if alt["path"]:
        edge_of = {edge_key(e): e for e in g.edges}
        alt["cost"] = sum(w(edge_of[frozenset(p)]) for p in zip(alt["path"], alt["path"][1:]))
    return alt
