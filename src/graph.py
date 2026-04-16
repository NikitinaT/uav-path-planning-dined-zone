from __future__ import annotations

from typing import Dict, Tuple

import networkx as nx

Point = Tuple[int, int]


def build_graph(env: Dict[str, object]) -> nx.Graph:
    # Create a grid graph and remove forbidden nodes
    width = int(env["width"])
    height = int(env["height"])
    obstacles = set(env["obstacles"])
    denied = set(env["denied"])
    dangerous = set(env["dangerous"])
    mode = str(env["mode"])

    graph = nx.grid_2d_graph(width, height)

    forbidden = obstacles | denied
    graph.remove_nodes_from([node for node in graph.nodes if node in forbidden])

    # Assign edge weights
    for u, v in graph.edges:
        weight = 1.0
        if mode == "risk-aware" and (u in dangerous or v in dangerous):
            weight += 5.0
        graph[u][v]["weight"] = weight

    return graph
