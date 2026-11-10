"""One-shot demo: generates data, runs every algorithm, saves screenshots + run_log.txt to results/."""
import os
import matplotlib; matplotlib.use("Agg")
from src.city_generator import build_city, write_csvs
from src.graph_model import load_graph, edge_key
from src.traffic import weight_fn
from src.traversal import bfs, dfs, components, reachable_within
from src.shortest_path import dijkstra, astar, bellman_ford, alternative_route
from src.mst import kruskal, prim
from src.visualize import plot_network
from src.analysis import benchmark, plot_benchmark

os.makedirs("results", exist_ok=True)
if not os.path.exists("data/edges.csv"):
    write_csvs(*build_city(8))
g = load_graph("data")
log = []
def out(*a):
    s = " ".join(str(x) for x in a); print(s); log.append(s)

S, T = 0, len(g.nodes) - 1
out(f"City: {len(g.nodes)} junctions, {len(g.edges)} roads\n")

out("== 1. Traversal ==")
out("BFS order (first 10):", bfs(g, S)[0][:10]); out("DFS order (first 10):", dfs(g, S)[:10])
out("Junctions within 3 hops of J0:", len(reachable_within(g, S, 3)), "\n")

out("== 2. Shortest path (J0 -> J%d) ==" % T)
for hour in (3, 8, 12, 17):
    for name, f in (("Dijkstra", dijkstra), ("A*", astar), ("Bellman-Ford", bellman_ford)):
        r = f(g, S, T, weight_fn("time", hour))
        out(f"hour {hour:02d}  {name:13s} {r['cost']:6.2f} min  explored={r['explored']:3d}  hops={len(r['path'])-1}")
w8 = weight_fn("time", 8)
best = dijkstra(g, S, T, w8); alt = alternative_route(g, S, T, w8)
fig = plot_network(g, path=best["path"], alt=alt["path"], hour=8, title="Rush-hour route (pink) and alternative (purple)")
fig.savefig("results/route_rush_hour.png", dpi=130)
out(f"Best {best['cost']:.2f} min, alternative {alt['cost']:.2f} min\n")

out("== 3. Road-closure what-if ==")
a, b = best["path"][len(best["path"]) // 2], best["path"][len(best["path"]) // 2 + 1]
closed = {frozenset((a, b))}
new = dijkstra(g, S, T, weight_fn("time", 8, closed))
out(f"Closing road {a}-{b}: {best['cost']:.2f} -> {new['cost']:.2f} min, new route {new['path']}")
plot_network(g, path=new["path"], closed=closed, hour=8, title="After closing a road").savefig("results/closure_reroute.png", dpi=130)
cut = {edge_key(e) for _, e in g.neighbors(S)}
out("Isolating J0 -> zones:", [len(z) for z in components(g, cut)], "\n")

out("== 4. Minimum spanning tree (distance) ==")
tk, ck = kruskal(g, weight_fn("distance")); tp, cp = prim(g, weight_fn("distance"))
full = sum(e.distance for e in g.edges)
out(f"Kruskal {ck:.2f} km | Prim {cp:.2f} km | full network {full:.2f} km | saving {(1-ck/full)*100:.0f}%\n")
plot_network(g, mst=tk, title="Minimum spanning tree (Kruskal)").savefig("results/mst.png", dpi=130)
plot_network(g, hour=8, title="Congestion heatmap 08:00").savefig("results/heatmap_0800.png", dpi=130)

out("== 5. Performance benchmark ==")
rows = benchmark()
for r in rows: out(r)
plot_benchmark(rows, "results/benchmark.png")
open("results/run_log.txt", "w").write("\n".join(log))
print("\nSaved screenshots and log to results/")
