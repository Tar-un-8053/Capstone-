"""Matplotlib drawing of the road network, congestion heatmap, routes, MST and closures."""
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from src.graph_model import edge_key
from src.traffic import congestion_level

COL = {"Free": "#2e9e5b", "Moderate": "#f0a020", "Heavy": "#d93a3a"}


def _segs(g, edges):
    return [[g.pos(e.u), g.pos(e.v)] for e in edges]


def plot_network(g, path=None, alt=None, closed=None, mst=None, hour=None, title="", size=(8, 7)):
    closed = closed or set()
    fig, ax = plt.subplots(figsize=size)
    open_edges = [e for e in g.edges if edge_key(e) not in closed]
    colors = [COL[congestion_level(e, hour)] for e in open_edges] if hour is not None else "#b0b0b0"
    ax.add_collection(LineCollection(_segs(g, open_edges), colors=colors, linewidths=1.6, zorder=1))
    shut = [e for e in g.edges if edge_key(e) in closed]
    if shut:
        ax.add_collection(LineCollection(_segs(g, shut), colors="black", linestyles=":", linewidths=2.5, zorder=2))
    if mst:
        ax.add_collection(LineCollection(_segs(g, mst), colors="#1f5fd1", linewidths=3, zorder=3))
    for p, c, lw in ((alt, "#8e44ad", 3), (path, "#e91e63", 4)):
        if p and len(p) > 1:
            ax.add_collection(LineCollection([[g.pos(a), g.pos(b)] for a, b in zip(p, p[1:])],
                                             colors=c, linewidths=lw, zorder=4))
    xs, ys = zip(*(g.pos(n) for n in g.nodes))
    ax.scatter(xs, ys, s=14, c="#333", zorder=5)
    if path:
        for n in (path[0], path[-1]):
            ax.annotate(g.name(n), g.pos(n), xytext=(5, 5), textcoords="offset points", weight="bold")
    ax.set_title(title); ax.set_aspect("equal"); ax.autoscale(); ax.axis("off")
    return fig
