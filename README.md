# Smart City Traffic Management & Route Optimisation System

Models a city as a weighted graph (junctions = nodes, roads = edges) and uses graph algorithms – all implemented
from scratch – for routing, traffic analysis and infrastructure planning.

## Features
| Area | Algorithms / features | Complexity |
|---|---|---|
| Traversal | BFS, DFS, connected components, N-hop reachability (emergency coverage, isolated zones after closures) | O(V+E) |
| Shortest path | Dijkstra, A\*, Bellman-Ford, alternative route | O((V+E)logV), A\* same worst case, O(VE) |
| MST | Kruskal (union-find), Prim (heap) – cheapest backbone for metro/cable layout | O(E log E), O(E log V) |
| Traffic model | Time-of-day rush-hour congestion, capacity-based delay, road closures | – |
| Dashboard | Streamlit app: commuter view, admin heatmap/zones, MST planner, benchmark | – |
| Analysis | Runtime & nodes-explored vs city size, charts | – |

## Setup & run
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.city_generator       # (re)generate sample data into data/
python run_demo.py                 # runs every algorithm, writes results/*.png and results/run_log.txt
streamlit run src/app.py           # interactive dashboard
pytest -q                          # unit tests (cross-checked against NetworkX)
```

## Folder structure
```
data/      nodes.csv, edges.csv, traffic_log.csv   (sample data)
src/       graph_model, traversal, shortest_path, mst, traffic, city_generator, visualize, analysis, app
tests/     test_algorithms.py
results/   screenshots, benchmark chart, run_log.txt
docs/      capstone report outline
```

## Data format
- `nodes.csv`: id, name, x, y (km)  - `edges.csv`: u, v, distance (km), base_time (min), capacity (veh/h)
- `traffic_log.csv`: u, v, hour, congestion_index (sample hourly log)

## Traffic model
`travel_time = base_time × (1 + 0.8 × utilisation)`, where `utilisation = peak(hour) × 1000 / capacity`.
Closed roads have infinite weight and are skipped by every algorithm.
