from __future__ import annotations

from typing import Dict, Set, Tuple
import random

import yaml

Point = Tuple[int, int]


def _random_cells(count: int, width: int, height: int, used: Set[Point]) -> Set[Point]:
    cells: Set[Point] = set()
    while len(cells) < count:
        cell = (random.randint(0, width - 1), random.randint(0, height - 1))
        if cell not in used:
            cells.add(cell)
            used.add(cell)
    return cells


def generate_map(config_path: str = "config.yaml") -> Dict[str, object]:
    # Load configuration
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    width = int(config["map"]["width"])
    height = int(config["map"]["height"])

    obstacle_count = int(config["zones"]["obstacles"])
    denied_count = int(config["zones"]["denied"])
    dangerous_count = int(config["zones"]["dangerous"])

    used: Set[Point] = {(0, 0), (width - 1, height - 1)}

    # Generate zone cells
    obstacles = _random_cells(obstacle_count * 80, width, height, used)
    denied = _random_cells(denied_count * 80, width, height, used)
    dangerous = _random_cells(dangerous_count * 80, width, height, used)

    return {
        "width": width,
        "height": height,
        "obstacles": obstacles,
        "denied": denied,
        "dangerous": dangerous,
        "mode": config["algorithm"]["mode"],
    }
