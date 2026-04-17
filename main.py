import matplotlib.pyplot as plt
import numpy as np
import random
from scipy.spatial import ConvexHull
import networkx as nx
from matplotlib.path import Path
import heapq

# ---------- Parameters ----------
random.seed(42)
np.random.seed(42)

A = (5, 0)
B = (100, 100)
num_clusters = 10
cluster_spread = 10.0
min_center_dist = 15
area_limit = 100
neighbor_threshold = 50.0
offline_threshold = 30.0  # max allowed offline time (minutes)
speed = 1.2  # distance units per minute
show_candidate_edges = False

# ---------- Generate cluster centers ----------
x_min, x_max = cluster_spread, area_limit - cluster_spread
y_min, y_max = cluster_spread, area_limit - cluster_spread

cluster_centers = []
while len(cluster_centers) < num_clusters:
    cand = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
    if all(np.linalg.norm(np.array(cand) - np.array(existing)) >= min_center_dist for existing in cluster_centers):
        cluster_centers.append(cand)

# ---------- Generate random points around each cluster center ----------
all_points = []
cluster_groups = []
hull_vertices_list = {}
cluster_hulls = {}

for i, (cx, cy) in enumerate(cluster_centers):
    pts = [
        (
            random.uniform(cx - cluster_spread, cx + cluster_spread),
            random.uniform(cy - cluster_spread, cy + cluster_spread),
        )
        for _ in range(random.randint(6, 30))
    ]
    pts_array = np.array(pts)
    all_points.extend(pts)
    cluster_groups.append(pts)

    hull = ConvexHull(pts_array)
    vertices = pts_array[hull.vertices]
    hull_vertices_list[i] = [tuple(v) for v in vertices]
    cluster_hulls[i] = Path(vertices)

points_array = np.array(all_points)

# ---------- Collect all nodes ----------
all_nodes = []
for i in range(num_clusters):
    for v in hull_vertices_list[i]:
        all_nodes.append((v[0], v[1], f"CL{i+1}"))
all_nodes.append((A[0], A[1], "A"))
all_nodes.append((B[0], B[1], "B"))

# ---------- Geometry helpers ----------
def segments_intersect(p1, p2, q1, q2):
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def on_segment(a, b, c):
        return min(a[0], b[0]) <= c[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= c[1] <= max(a[1], b[1])

    o1 = orient(p1, p2, q1)
    o2 = orient(p1, p2, q2)
    o3 = orient(q1, q2, p1)
    o4 = orient(q1, q2, p2)

    if o1 * o2 < 0 and o3 * o4 < 0:
        return True
    if o1 == 0 and on_segment(p1, p2, q1):
        return True
    if o2 == 0 and on_segment(p1, p2, q2):
        return True
    if o3 == 0 and on_segment(q1, q2, p1):
        return True
    if o4 == 0 and on_segment(q1, q2, p2):
        return True
    return False


def crosses_cluster_interior(p1, p2):
    """Return True if the segment crosses through the interior of any cluster hull.
    Touching a hull vertex is allowed; flying through the cluster is not.
    """
    mid = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    for i in range(num_clusters):
        verts = hull_vertices_list[i]
        n = len(verts)
        for j in range(n):
            q1 = verts[j]
            q2 = verts[(j + 1) % n]
            if p1 in (q1, q2) or p2 in (q1, q2):
                continue
            if segments_intersect(p1, p2, q1, q2):
                return True
        if cluster_hulls[i].contains_point(mid):
            return True
    return False


# ---------- Build graph ----------
G = nx.Graph()
for idx, (x, y, label) in enumerate(all_nodes):
    G.add_node(idx, coord=(x, y), label=label)

# Connect boundary edges so the drone can move along hull boundaries
for i in range(num_clusters):
    verts = hull_vertices_list[i]
    n = len(verts)
    for j in range(n):
        p1 = verts[j]
        p2 = verts[(j + 1) % n]
        u = all_nodes.index((p1[0], p1[1], f"CL{i+1}"))
        v = all_nodes.index((p2[0], p2[1], f"CL{i+1}"))
        dist = np.linalg.norm(np.array(p1) - np.array(p2))
        G.add_edge(u, v, weight=dist / speed)

# Connect visible/feasible transitions between nodes
for i in range(len(all_nodes)):
    p1 = (all_nodes[i][0], all_nodes[i][1])
    l1 = all_nodes[i][2]
    for j in range(i + 1, len(all_nodes)):
        p2 = (all_nodes[j][0], all_nodes[j][1])
        l2 = all_nodes[j][2]

        # Do not create duplicate shortcuts inside the same hull; boundary edges already cover them.
        if l1.startswith("CL") and l1 == l2:
            continue

        dist = np.linalg.norm(np.array(p1) - np.array(p2))
        time_cost = dist / speed
        if dist <= neighbor_threshold and time_cost <= offline_threshold and not crosses_cluster_interior(p1, p2):
            G.add_edge(i, j, weight=time_cost)


# ---------- Dijkstra with offline-time constraint ----------
def constrained_dijkstra(graph, source, target, boundary_nodes, threshold):
    """Shortest path where accumulated offline time cannot exceed threshold.

    Offline time resets to 0 whenever the drone reaches any boundary node.
    """
    pq = [(0.0, 0.0, source, None)]  # (total_cost, current_offline_time, node, parent_state)
    visited = {}
    parent = {}
    found_state = None

    while pq:
        dist, offline, node, parent_state = heapq.heappop(pq)
        key = (node, round(offline, 5))
        if key in visited and visited[key] <= dist:
            continue

        visited[key] = dist
        parent[(node, offline)] = parent_state

        if node == target:
            found_state = (node, offline)
            break

        for nbr in graph.neighbors(node):
            w = graph.edges[node, nbr]["weight"]
            new_offline = 0.0 if nbr in boundary_nodes else offline + w
            if new_offline > threshold:
                continue
            heapq.heappush(pq, (dist + w, new_offline, nbr, (node, offline)))

    if not found_state:
        return None, None, None

    path = []
    state = found_state
    while state:
        node, off = state
        path.append(node)
        state = parent.get(state)
    path.reverse()

    coords = [graph.nodes[n]["coord"] for n in path]
    total_cost = 0.0
    if len(path) > 1:
        for u, v in zip(path[:-1], path[1:]):
            total_cost += graph.edges[u, v]["weight"]

    return path, coords, total_cost


# ---------- Run algorithm ----------
boundary_nodes = {n for n, d in G.nodes(data=True) if d["label"].startswith("CL")}
idx_A = next(n for n, d in G.nodes(data=True) if d["label"] == "A")
idx_B = next(n for n, d in G.nodes(data=True) if d["label"] == "B")
path_nodes, path_coords, total_time = constrained_dijkstra(G, idx_A, idx_B, boundary_nodes, offline_threshold)


# ---------- Visualization ----------
def visualize(graph, path_nodes=None, total_time=None):
    plt.figure(figsize=(10, 10))

    # Wi-Fi points
    plt.scatter(points_array[:, 0], points_array[:, 1], color="blue", s=50, marker="x", label="Wi-Fi points")

    # Hulls + cluster labels
    for i, pts in enumerate(cluster_groups):
        pts_array = np.array(pts)
        hull = ConvexHull(pts_array)
        hull_points = pts_array[hull.vertices]
        hull_closed = np.vstack([hull_points, hull_points[0]])
        plt.plot(hull_closed[:, 0], hull_closed[:, 1], color="orange", linewidth=2)

        center = hull_points.mean(axis=0)
        plt.text(center[0], center[1], f"CL{i+1}", fontsize=10, ha="center", va="center")

    # Optional: show graph transitions
    if show_candidate_edges:
        for u, v in graph.edges():
            x1, y1 = graph.nodes[u]["coord"]
            x2, y2 = graph.nodes[v]["coord"]
            plt.plot([x1, x2], [y1, y2], color="lightgray", linewidth=0.6, alpha=0.45, zorder=0)

    # Start and finish
    plt.scatter(*A, color="green", s=180, marker="o", label="Start A", zorder=5)
    plt.text(A[0] + 1, A[1] + 1, "A", color="green", fontsize=12, weight="bold")

    plt.scatter(*B, color="red", s=180, marker="o", label="Goal B", zorder=5)
    plt.text(B[0] + 1, B[1] + 1, "B", color="red", fontsize=12, weight="bold")

    # Path
    if path_nodes and len(path_nodes) > 1:
        path_xy = np.array([graph.nodes[n]["coord"] for n in path_nodes])
        plt.plot(path_xy[:, 0], path_xy[:, 1], color="purple", linewidth=3, label="Dijkstra path", zorder=6)
        plt.scatter(path_xy[:, 0], path_xy[:, 1], color="purple", s=35, zorder=7)

        # Mark boundary connection points visited by the path
        boundary_path_xy = np.array([
            graph.nodes[n]["coord"] for n in path_nodes if graph.nodes[n]["label"].startswith("CL")
        ])
        if len(boundary_path_xy) > 0:
            plt.scatter(
                boundary_path_xy[:, 0],
                boundary_path_xy[:, 1],
                facecolors="none",
                edgecolors="black",
                s=120,
                linewidths=1.5,
                label="Connection points",
                zorder=8,
            )

        title = (
            f"Cluster boundaries and constrained Dijkstra path\n"
            f"Total path time = {total_time:.2f} min, offline threshold = {offline_threshold:.2f} min"
        )
    else:
        title = (
            f"No feasible path found\n"
            f"Offline threshold = {offline_threshold:.2f} min"
        )
    if path_nodes:
        for i in range(len(path_nodes) - 1):
            u = path_nodes[i]
            v = path_nodes[i + 1]

            x1, y1 = G.nodes[u]['coord']
            x2, y2 = G.nodes[v]['coord']

            plt.plot([x1, x2], [y1, y2], color='red', linewidth=2)

            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            weight = G.edges[u, v]['weight']

            plt.text(mx, my, f"   {weight:.1f} min", fontsize=10, color='red')
    plt.title(title)
    plt.xlabel("X")
    plt.ylabel("Y")
    img = plt.imread("src/map.jpg")
    plt.imshow(img, extent=[0, area_limit, 0, area_limit], alpha=0.4, zorder=0)
    plt.xlim(0, area_limit)
    plt.ylim(0, area_limit)
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.axis("equal")
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.show()


if path_nodes:
    print("Path found:")

    # --- input points ---
    for idx, node in enumerate(path_nodes):
        label = G.nodes[node]["label"]
        coord = G.nodes[node]["coord"]
        print(f"{idx+1:02d}. {label} -> ({round(coord[0])}, {round(coord[1])})")

    print("\nSegments:")

    # --- output distances between points ---
    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i + 1]

        x1, y1 = G.nodes[u]["coord"]
        x2, y2 = G.nodes[v]["coord"]

        label1 = G.nodes[u]["label"]
        label2 = G.nodes[v]["label"]

        # distance
        dist = np.hypot(x2 - x1, y2 - y1)

        # время (уже есть в графе)
        time = G.edges[u, v]["weight"]

        print(f"{i+1:02d}. {label1} -> {label2} | "
              f"dist = {dist:.2f}, time = {time:.2f} min")

    print(f"\nTotal path time: {total_time:.2f} min")

else:
    print("No feasible path found under the current offline-time constraint.")

visualize(G, path_nodes, total_time)
