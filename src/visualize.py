from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt

Point = Tuple[int, int]


def _scatter(points: Iterable[Point], label: str, marker: str, size: int) -> None:
    points = list(points)
    if not points:
        return
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    plt.scatter(xs, ys, label=label, marker=marker, s=size)


def plot(env: Dict[str, object], path: List[Point], start: Point, goal: Point) -> None:
    # Plot map layers and path
    plt.figure(figsize=(8, 8))

    _scatter(env["obstacles"], "Obstacles", "s", 18)
    _scatter(env["denied"], "Denied zones", "x", 18)
    _scatter(env["dangerous"], "Dangerous zones", ".", 10)

    if path:
        xs = [p[0] for p in path]
        ys = [p[1] for p in path]
        plt.plot(xs, ys, linewidth=2, label="Path")

    plt.scatter([start[0]], [start[1]], marker="o", s=70, label="Start")
    plt.scatter([goal[0]], [goal[1]], marker="*", s=100, label="Goal")

    plt.xlim(0, int(env["width"]))
    plt.ylim(0, int(env["height"]))
    plt.title("UAV Path Planning Prototype")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
