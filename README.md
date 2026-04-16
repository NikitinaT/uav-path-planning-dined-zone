# UAV Path Planning Prototype for Denied and Dangerous Environments

This project is a minimal Python prototype for UAV path planning in denied and dangerous environments.
It generates a synthetic map, builds a graph representation with NetworkX, computes a route using a modified Dijkstra algorithm, and visualizes the result.

## Features

- Synthetic map generation
- Graph-based environment representation
- Modified Dijkstra path planning
- Visualization of zones and computed path

## Project Structure

```text
uav-path-planning/
├── README.md
├── requirements.txt
├── main.py
├── config.yaml
└── src/
    ├── map.py
    ├── graph.py
    ├── dijkstra.py
    └── visualize.py
```

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Notes

This is a compact research-oriented baseline that can be extended with:

- connectivity constraints
- reconnection zones
- risk-aware penalties
- real-world map layers
- experiment pipelines
