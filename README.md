# UAV Path Planning Prototype in a Communication-Denied Environment

This repository contains a Python prototype for **connectivity-constrained UAV path planning** in a partially connected or communication-denied environment.  
The main script generates a synthetic communication map, forms reconnection-zone boundaries, constructs a graph, and computes a feasible route from the start point `A` to the destination point `B` under an offline-time constraint.

## Repository Structure

```text
uav-path-planning-dined-zone/
├── main.py
├── config.py                     # optional, if parameters are moved out of main.py
├── README.md
├── requirements.txt
│
├── examples/
│   ├── boundary_gen.py           # boundary generation example
│   └── map_coverage.py           # coverage map example
│
└── src/
    ├── map.jpg
    ├── reconnection_zone_ConvexHull.png
    ├── coverage_map.png
    └── graph_PP.png
```

## Main Idea

The prototype models a synthetic navigation environment with Wi-Fi communication clusters.  
The UAV must move from point `A` to point `B` while periodically reconnecting to communication zones and never exceeding the allowed offline time.

The graph-based route is computed using a **modified Dijkstra algorithm** that tracks accumulated disconnected time and discards routes violating the connectivity constraint.

## Input Parameters

The main program uses the following parameters.

| Parameter | Meaning |
|---|---|
| `A` | Start point of the UAV mission |
| `B` | Destination point of the UAV mission |
| `num_clusters` | Number of synthetic Wi-Fi clusters generated in the map |
| `cluster_spread` | Spatial spread of Wi-Fi points around a cluster center |
| `min_center_dist` | Minimum allowed distance between cluster centers |
| `area_limit` | Size of the square navigation area |
| `neighbor_threshold` | Maximum allowed distance between two nodes when creating graph edges |
| `offline_threshold` | Maximum allowed offline flight time between reconnection events |
| `speed` | UAV speed, expressed in distance units per minute |
| `show_candidate_edges` | Flag for visualizing candidate graph transitions |

## How Flight Time Is Computed

For each graph segment, travel time is computed as:

```python
time_cost = dist / speed
```

where:
- `dist` is the Euclidean distance between two nodes,
- `speed` is the UAV speed.

Thus, the edge weight in the graph corresponds to the flight time required to move between two connected nodes.

## Output Interpretation

When a feasible route is found, the program prints:

1. **Path found** — ordered sequence of route nodes:
   - `A` — start point,
   - `B` — destination point,
   - `CLi` — boundary points of reconnection zones.

2. **Segments** — for each consecutive pair of route nodes:
   - `dist` — Euclidean distance,
   - `time` — travel time for the segment.

3. **Total path time** — the sum of travel times over all route segments.

Example:

```text
Path found:
01. A -> (5, 0)
02. CL7 -> (20, 17)
03. CL7 -> (21, 18)
04. CL2 -> (26, 36)
05. CL2 -> (26, 38)
06. CL6 -> (37, 42)
07. CL3 -> (60, 69)
08. CL3 -> (66, 74)
09. CL3 -> (75, 74)
10. CL3 -> (78, 73)
11. B -> (100, 100)

Segments:
01. A -> CL7 | dist = 22.80, time = 19.00 min
02. CL7 -> CL7 | dist = 1.16, time = 0.96 min
03. CL7 -> CL2 | dist = 18.76, time = 15.63 min
04. CL2 -> CL2 | dist = 1.88, time = 1.57 min
05. CL2 -> CL6 | dist = 11.76, time = 9.80 min
06. CL6 -> CL3 | dist = 35.43, time = 29.52 min
07. CL3 -> CL3 | dist = 7.62, time = 6.35 min
08. CL3 -> CL3 | dist = 9.06, time = 7.55 min
09. CL3 -> CL3 | dist = 2.97, time = 2.47 min
10. CL3 -> B | dist = 35.16, time = 29.30 min

Total path time: 122.16 min
```

## Visualization Assets

The following images are used to illustrate the prototype stages:

- `src/reconnection_zone_ConvexHull.png` — reconnection-zone boundary generation
- `src/coverage_map.png` — synthetic coverage map
- `src/graph_PP.png` — graph-based path-planning result
- `src/map.jpg` — optional background image used by the main script

## Jupyter Notebook

The notebook `UAV_Path_Planning_Demo.ipynb` demonstrates:

- parameter explanation,
- boundary generation example,
- coverage map example,
- graph/path-planning example,
- final output interpretation,
- inline visualization of the repository images.

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the main prototype:

```bash
python main.py
```

Run the notebook:

```bash
jupyter notebook
```