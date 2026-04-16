from __future__ import annotations

from typing import List, Tuple

import networkx as nx

Point = Tuple[int, int]


def dijkstra_modified(graph: nx.Graph, start: Point, goal: Point) -> List[Point]:
    # Compute a shortest path using weighted Dijkstra
    if start not in graph:
        raise ValueError("Start node is not available in the graph.")
    if goal not in graph:
        raise ValueError("Goal node is not available in the graph.")

    return nx.shortest_path(graph, source=start, target=goal, weight="weight")
