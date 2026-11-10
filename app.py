"""Streamlit dashboard.  Run:  streamlit run src/app.py   (from the project root)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src.city_generator import build_city, write_csvs
from src.graph_model import load_graph, edge_key
from src.traffic import weight_fn, congestion_level
from src.traversal import components, reachable_within
from src.shortest_path import dijkstra, astar, alternative_route
from src.mst import kruskal, prim
from src.visualize import plot_network
from src.analysis import benchmark, plot_benchmark

st.set_page_config(page_title="Smart City Traffic", layout="wide")


@st.cache_resource
def get_graph():
    if not os.path.exists("data/edges.csv"):
        write_csvs(*build_city(8))
    return load_graph("data")


g = get_graph()
names = {n: g.name(n) for n in g.nodes}
st.title("🚦 Smart City Traffic Management & Route Optimisation")

st.sidebar.header("Conditions")
hour = st.sidebar.slider("Hour of day", 0, 23, 8)
labels = {f"{e.u}–{e.v}": edge_key(e) for e in g.edges}
shut = st.sidebar.multiselect("Closed roads (u–v)", list(labels))
closed = {labels[l] for l in shut}

tab1, tab2, tab3, tab4 = st.tabs(["🚗 Commuter", "🏛 Admin: congestion & zones", "🏗 Infrastructure (MST)", "⏱ Performance"])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    s = c1.selectbox("From", list(g.nodes), format_func=names.get, index=0)
    t = c2.selectbox("To", list(g.nodes), format_func=names.get, index=len(g.nodes) - 1)
    mode = c3.radio("Optimise for", ["time", "distance"], horizontal=True)
    algo = c4.radio("Algorithm", ["Dijkstra", "A*"], horizontal=True)
    w = weight_fn(mode, hour, closed)
    r = (dijkstra if algo == "Dijkstra" else astar)(g, s, t, w)
    unit = "min" if mode == "time" else "km"
    if not r["path"]:
        st.error("No route available – the destination is cut off by the closures.")
        st.pyplot(plot_network(g, closed=closed, hour=hour, title="Network"))
    else:
        alt = alternative_route(g, s, t, w)
        m1, m2, m3 = st.columns(3)
        m1.metric(f"Best route ({unit})", f"{r['cost']:.1f}")
        m2.metric("Junctions on route", len(r["path"]))
        m3.metric("Nodes explored", r["explored"])
        st.write("**Route:** " + " → ".join(names[n] for n in r["path"]))
        if alt["path"] and alt["path"] != r["path"]:
            st.write(f"**Alternative (purple):** {alt['cost']:.1f} {unit}")
        st.pyplot(plot_network(g, path=r["path"], alt=alt["path"], closed=closed, hour=hour,
                               title=f"Congestion at {hour:02d}:00 (green/orange/red), route in pink"))

with tab2:
    heavy = sum(congestion_level(e, hour) == "Heavy" for e in g.edges)
    comps = components(g, closed)
    a, b, c = st.columns(3)
    a.metric("Heavily congested roads", f"{heavy}/{len(g.edges)}")
    b.metric("Closed roads", len(closed))
    c.metric("Disconnected zones", len(comps))
    if len(comps) > 1:
        st.warning("Closures split the city! Isolated zones: " +
                   "; ".join(f"{len(z)} junctions" for z in sorted(comps, key=len)[:-1]))
    hub = st.selectbox("Emergency hub – junctions reachable within N road segments", list(g.nodes), format_func=names.get)
    k = st.slider("N hops", 1, 10, 4)
    st.write(f"**{len(reachable_within(g, hub, k, closed))}** junctions reachable (BFS).")
    st.pyplot(plot_network(g, closed=closed, hour=hour, title=f"Congestion heatmap {hour:02d}:00"))

with tab3:
    algo2 = st.radio("MST algorithm", ["Kruskal", "Prim"], horizontal=True)
    tree, total = (kruskal if algo2 == "Kruskal" else prim)(g, weight_fn("distance"))
    full = sum(e.distance for e in g.edges)
    a, b, c = st.columns(3)
    a.metric("MST length (km)", f"{total:.1f}")
    b.metric("Full network (km)", f"{full:.1f}")
    c.metric("Saving", f"{(1 - total / full) * 100:.0f}%")
    st.caption("Minimum road length that still connects every junction – a candidate backbone for new metro / cable / fibre layouts.")
    st.pyplot(plot_network(g, mst=tree, title=f"{algo2} minimum spanning tree (blue)"))

with tab4:
    if st.button("Run benchmark"):
        rows = benchmark()
        st.dataframe(rows)
        st.pyplot(plot_benchmark(rows))
