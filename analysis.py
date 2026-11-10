"""Performance analysis: runtime and nodes explored vs. city size."""
import time
import matplotlib.pyplot as plt
from src.city_generator import build_city
from src.graph_model import build_graph
from src.traffic import weight_fn
from src.traversal import bfs
from src.shortest_path import dijkstra, astar
from src.mst import kruskal, prim


def _time(f, repeats):
    best, r = float("inf"), None
    for _ in range(repeats):
        t0 = time.perf_counter(); r = f(); best = min(best, time.perf_counter() - t0)
    return best * 1000, r


def benchmark(sizes=(5, 8, 12, 16, 20, 25), repeats=3, hour=8):
    rows = []
    for n in sizes:
        g = build_graph(*build_city(n))
        w, wd = weight_fn("time", hour), weight_fn("distance")
        s, t = 0, n * n - 1
        row = {"grid": f"{n}x{n}", "V": len(g.nodes), "E": len(g.edges)}
        row["bfs_ms"], _ = _time(lambda: bfs(g, s), repeats)
        row["dijkstra_ms"], d = _time(lambda: dijkstra(g, s, t, w), repeats)
        row["astar_ms"], a = _time(lambda: astar(g, s, t, w), repeats)
        row["dijkstra_explored"], row["astar_explored"] = d["explored"], a["explored"]
        row["kruskal_ms"], _ = _time(lambda: kruskal(g, wd), repeats)
        row["prim_ms"], _ = _time(lambda: prim(g, wd), repeats)
        rows.append({k: round(v, 3) if isinstance(v, float) else v for k, v in row.items()})
    return rows


def plot_benchmark(rows, path=None):
    V = [r["V"] for r in rows]
    fig, ax = plt.subplots(1, 3, figsize=(15, 4))
    for k, lab in (("bfs_ms", "BFS"), ("dijkstra_ms", "Dijkstra"), ("astar_ms", "A*")):
        ax[0].plot(V, [r[k] for r in rows], "o-", label=lab)
    ax[0].set_title("Traversal / shortest path runtime"); ax[0].set_ylabel("ms")
    for k, lab in (("kruskal_ms", "Kruskal"), ("prim_ms", "Prim")):
        ax[1].plot(V, [r[k] for r in rows], "o-", label=lab)
    ax[1].set_title("MST runtime"); ax[1].set_ylabel("ms")
    for k, lab in (("dijkstra_explored", "Dijkstra"), ("astar_explored", "A*")):
        ax[2].plot(V, [r[k] for r in rows], "o-", label=lab)
    ax[2].set_title("Nodes explored (corner to corner)")
    for a in ax: a.set_xlabel("Intersections (V)"); a.legend(); a.grid(alpha=.3)
    fig.tight_layout()
    if path: fig.savefig(path, dpi=130)
    return fig
