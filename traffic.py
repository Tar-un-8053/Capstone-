"""Traffic model: time-of-day congestion, road closures and edge-weight functions."""
import math
from src.graph_model import edge_key

INF = math.inf


def peak_factor(hour):
    """0.1 (night) .. 1.0 (morning/evening rush). Two smooth peaks at ~08:30 and ~17:30."""
    h = hour % 24
    am = math.exp(-((h - 8.5) ** 2) / (2 * 1.2 ** 2))
    pm = math.exp(-((h - 17.5) ** 2) / (2 * 1.5 ** 2))
    return 0.1 + 0.9 * max(am, pm)


def utilisation(e, hour):
    """Load / capacity style index. Small roads saturate faster."""
    return peak_factor(hour) * 1000 / e.capacity


def travel_time(e, hour):
    return e.base_time * (1 + 0.8 * utilisation(e, hour))


def congestion_level(e, hour):
    u = utilisation(e, hour)
    return "Free" if u < 0.5 else "Moderate" if u < 0.9 else "Heavy"


def weight_fn(mode="time", hour=8, closed=None):
    """Return w(edge) -> cost. Closed roads cost infinity (algorithms skip them)."""
    closed = closed or set()

    def w(e):
        if edge_key(e) in closed:
            return INF
        return e.distance if mode == "distance" else travel_time(e, hour)
    return w
