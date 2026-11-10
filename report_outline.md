# Capstone Report Outline (copy into Word/PDF and add your screenshots)

1. **Problem statement & objectives** – congestion, route choice, planning; what the system must do.
2. **Design** – graph model, data format, module diagram, algorithm choices and why.
3. **Implementation** – key code snippets, complexity table (see README), traffic model formula.
4. **Testing** – `pytest` output (8 tests, NetworkX cross-check), edge cases: closures, unreachable node, disconnected graph.
5. **Results** – paste `results/route_rush_hour.png`, `closure_reroute.png`, `mst.png`, `heatmap_0800.png`, `benchmark.png`, and `run_log.txt`.
   Discuss: rush-hour vs night time, Dijkstra vs A* nodes explored, Kruskal vs Prim, MST saving %.
6. **Conclusion & future work** – real map data (OSMnx), live traffic API, dynamic re-routing, directed one-way roads.
7. **References** – CLRS, NetworkX docs, Streamlit docs.
