import math, random
import networkx as nx
from src.city_generator import build_city
from src.graph_model import build_graph, edge_key
from src.traffic import weight_fn
from src.traversal import bfs, dfs, components, reachable_within
from src.shortest_path import dijkstra, astar, bellman_ford, alternative_route
from src.mst import kruskal, prim


def city(n=7, seed=3):
    return build_graph(*build_city(n, seed))


def to_nx(g, w):
    G = nx.Graph()
    G.add_nodes_from(g.nodes)
    for e in g.edges:
        if w(e) < math.inf:
            G.add_edge(e.u, e.v, weight=w(e))
    return G


def test_shortest_paths_agree_with_networkx():
    g = city(); w = weight_fn("time", 8)
    G = to_nx(g, w)
    rnd = random.Random(0)
    for _ in range(15):
        s, t = rnd.sample(list(g.nodes), 2)
        ref = nx.dijkstra_path_length(G, s, t)
        for algo in (dijkstra, astar, bellman_ford):
            assert math.isclose(algo(g, s, t, w)["cost"], ref, rel_tol=1e-9), algo.__name__


def test_astar_explores_no_more_than_dijkstra():
    g = city(10); w = weight_fn("distance")
    assert astar(g, 0, 99, w)["explored"] <= dijkstra(g, 0, 99, w)["explored"]


def test_rush_hour_is_slower_than_night():
    g = city()
    assert dijkstra(g, 0, 48, weight_fn("time", 8))["cost"] > dijkstra(g, 0, 48, weight_fn("time", 3))["cost"]


def test_road_closure_reroutes_and_never_uses_closed_road():
    g = city(); w = weight_fn("time", 12)
    base = dijkstra(g, 0, 48, w)
    a, b = base["path"][0], base["path"][1]
    closed = {frozenset((a, b))}
    new = dijkstra(g, 0, 48, weight_fn("time", 12, closed))
    assert frozenset((a, b)) not in {frozenset(p) for p in zip(new["path"], new["path"][1:])}
    assert new["cost"] >= base["cost"]


def test_unreachable_destination():
    g = city()
    closed = {edge_key(e) for _, e in g.neighbors(0)}   # isolate node 0
    r = dijkstra(g, 0, 48, weight_fn("time", 8, closed))
    assert r["path"] == [] and r["cost"] == math.inf
    assert len(components(g, closed)) == 2


def test_alternative_route_is_valid():
    g = city(); w = weight_fn("time", 8)
    alt = alternative_route(g, 0, 48, w)
    assert alt["path"][0] == 0 and alt["path"][-1] == 48


def test_kruskal_equals_prim_equals_networkx():
    g = city(); w = weight_fn("distance")
    tk, ck = kruskal(g, w); tp, cp = prim(g, w)
    ref = nx.minimum_spanning_tree(to_nx(g, w)).size(weight="weight")
    assert len(tk) == len(tp) == len(g.nodes) - 1
    assert math.isclose(ck, cp) and math.isclose(ck, ref)


def test_bfs_dfs_visit_all_nodes_and_hops():
    g = city()
    order, hops = bfs(g, 0)
    assert sorted(order) == sorted(g.nodes) == sorted(dfs(g, 0))
    assert hops[0] == 0 and set(reachable_within(g, 0, 1)) == {0} | {v for v, _ in g.neighbors(0)}
