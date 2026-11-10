"""Minimum spanning tree (forest if the network is disconnected): Kruskal O(E log E), Prim O(E log V)."""
import heapq, math


class DSU:
    def __init__(self, items):
        self.p = {i: i for i in items}

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb: return False
        self.p[ra] = rb; return True


def kruskal(g, w):
    dsu, tree, total = DSU(g.nodes), [], 0
    for e in sorted((e for e in g.edges if w(e) < math.inf), key=w):
        if dsu.union(e.u, e.v):
            tree.append(e); total += w(e)
    return tree, total


def prim(g, w):
    seen, tree, total = set(), [], 0
    for start in g.nodes:                      # loop handles disconnected graphs
        if start in seen: continue
        seen.add(start)
        pq = [(w(e), start, v, e) for v, e in g.neighbors(start) if w(e) < math.inf]
        heapq.heapify(pq)
        while pq:
            c, u, v, e = heapq.heappop(pq)
            if v in seen: continue
            seen.add(v); tree.append(e); total += c
            for x, e2 in g.neighbors(v):
                if x not in seen and w(e2) < math.inf:
                    heapq.heappush(pq, (w(e2), v, x, e2))
    return tree, total
