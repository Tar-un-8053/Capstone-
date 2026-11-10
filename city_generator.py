"""Generates a synthetic city (grid + diagonal arterials, some roads removed) and sample CSV data."""
import csv, os, random
from src.traffic import peak_factor


def _connected(n_nodes, edge_set):
    adj = {i: [] for i in range(n_nodes)}
    for u, v in edge_set:
        adj[u].append(v); adj[v].append(u)
    seen, stack = {0}, [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); stack.append(v)
    return len(seen) == n_nodes


def build_city(n=6, seed=42, drop=0.12):
    rnd = random.Random(seed)
    nodes = [(r * n + c, f"J{r * n + c}", round(c + rnd.uniform(-.2, .2), 3), round(r + rnd.uniform(-.2, .2), 3))
             for r in range(n) for c in range(n)]
    pos = {i: (x, y) for i, _, x, y in nodes}
    grid = []
    for r in range(n):
        for c in range(n):
            i = r * n + c
            if c + 1 < n: grid.append((i, i + 1))
            if r + 1 < n: grid.append((i, i + n))
    arterials = set()
    for _ in range(max(1, n // 2)):
        r, c = rnd.randrange(n - 1), rnd.randrange(n - 1)
        arterials.add((r * n + c, (r + 1) * n + c + 1))
    edge_set = set(grid) | arterials
    for e in rnd.sample(sorted(grid), int(len(grid) * drop)):   # remove some roads, keep connectivity
        edge_set.discard(e)
        if not _connected(len(nodes), edge_set):
            edge_set.add(e)
    edges = []
    for u, v in sorted(edge_set):
        (x1, y1), (x2, y2) = pos[u], pos[v]
        dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5 * rnd.uniform(1.0, 1.15)
        fast = (u, v) in arterials or rnd.random() < 0.2
        speed = 60 if fast else rnd.choice([30, 40, 50])
        cap = rnd.randint(1500, 2000) if fast else rnd.randint(600, 1200)
        edges.append((u, v, round(dist, 3), round(dist / speed * 60, 3), cap))
    return nodes, edges


def write_csvs(nodes, edges, data_dir="data", seed=1):
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "nodes.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "name", "x", "y"]); w.writerows(nodes)
    with open(os.path.join(data_dir, "edges.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["u", "v", "distance", "base_time", "capacity"]); w.writerows(edges)
    rnd = random.Random(seed)
    with open(os.path.join(data_dir, "traffic_log.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["u", "v", "hour", "congestion_index"])
        for u, v, _, _, cap in edges:
            for h in range(24):
                w.writerow([u, v, h, round(peak_factor(h) * 1000 / cap * rnd.uniform(0.85, 1.15), 3)])


if __name__ == "__main__":
    nodes, edges = build_city(8)
    write_csvs(nodes, edges)
    print(f"Wrote {len(nodes)} nodes, {len(edges)} edges to data/")
