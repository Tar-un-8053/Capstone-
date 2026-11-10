"""Graph model of the city: intersections = nodes, roads = weighted undirected edges."""
import csv, math, os
from collections import namedtuple

Edge = namedtuple("Edge", "u v distance base_time capacity")  # km, minutes, vehicles/hour


def edge_key(e):
    """Direction-independent identifier of a road (used for closures)."""
    return frozenset((e.u, e.v))


class Graph:
    def __init__(self):
        self.nodes = {}   # id -> (name, x, y)
        self.adj = {}     # id -> [(neighbour, Edge)]
        self.edges = []

    def add_node(self, i, name, x, y):
        self.nodes[i] = (name, x, y)
        self.adj.setdefault(i, [])

    def add_edge(self, u, v, distance, base_time, capacity):
        e = Edge(u, v, distance, base_time, capacity)
        self.edges.append(e)
        self.adj[u].append((v, e))
        self.adj[v].append((u, e))

    def neighbors(self, u):
        return self.adj[u]

    def pos(self, i):
        return self.nodes[i][1], self.nodes[i][2]

    def euclid(self, a, b):
        (x1, y1), (x2, y2) = self.pos(a), self.pos(b)
        return math.hypot(x1 - x2, y1 - y2)

    def name(self, i):
        return self.nodes[i][0]


def build_graph(nodes, edges):
    g = Graph()
    for i, name, x, y in nodes:
        g.add_node(i, name, x, y)
    for u, v, d, t, c in edges:
        g.add_edge(u, v, d, t, c)
    return g


def load_graph(data_dir="data"):
    with open(os.path.join(data_dir, "nodes.csv")) as f:
        nodes = [(int(r["id"]), r["name"], float(r["x"]), float(r["y"])) for r in csv.DictReader(f)]
    with open(os.path.join(data_dir, "edges.csv")) as f:
        edges = [(int(r["u"]), int(r["v"]), float(r["distance"]), float(r["base_time"]), int(r["capacity"]))
                 for r in csv.DictReader(f)]
    return build_graph(nodes, edges)
