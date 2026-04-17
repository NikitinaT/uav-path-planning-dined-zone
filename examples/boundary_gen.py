import matplotlib.pyplot as plt
import numpy as np
import random
from scipy.spatial import ConvexHull

# ---------- Parameters ----------
random.seed(42)
np.random.seed(42)

A = (5, 0)
B = (60, 60)
num_clusters = 6
cluster_spread = 5.0
min_center_dist = 15
area_limit = 80  # Limit for visualization

# ---------- Generate cluster centers ----------
x_min, x_max = cluster_spread, area_limit - cluster_spread
y_min, y_max = cluster_spread, area_limit - cluster_spread

cluster_centers = []
while len(cluster_centers) < num_clusters:
    cand = (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
    if all(np.linalg.norm(np.array(cand) - np.array(existing)) >= min_center_dist 
           for existing in cluster_centers):
        cluster_centers.append(cand)

# ---------- Generate random points around each cluster center ----------
all_points = []
cluster_groups = []
for (cx, cy) in cluster_centers:
    pts = [(random.uniform(cx - cluster_spread, cx + cluster_spread),
            random.uniform(cy - cluster_spread, cy + cluster_spread))
           for _ in range(random.randint(6, 30))]
    all_points.extend(pts)
    cluster_groups.append(pts)

points_array = np.array(all_points)

# ---------- Visualization with convex hulls ----------
plt.figure(figsize=(8, 8))

# Wi-Fi points as blue dots (instead of crosses)
plt.scatter(points_array[:,0], points_array[:,1], color='blue', s=60, marker='x', label='Wi-Fi points')

# Draw convex hulls around clusters
for pts in cluster_groups:
    if len(pts) >= 3:
        hull = ConvexHull(pts)
        hull_points = np.array(pts)[hull.vertices]
        hull_points = np.concatenate((hull_points, [hull_points[0]]))  # close the loop
        plt.plot(hull_points[:, 0], hull_points[:, 1], 'orange', linewidth=2)

# Start and End points
plt.scatter(*A, color='green', s=200, marker='o', label='Start Point A')
plt.text(A[0]+1, A[1], "A", color='green', fontsize=14)

plt.scatter(*B, color='red', s=200, marker='o', label='End Point B')
plt.text(B[0]+1, B[1], "B", color='red', fontsize=14)

# Final plot settings
#plt.title("2D Wi-Fi Coverage Map with Cluster Boundaries", fontsize=14)
plt.xlabel("X")
plt.ylabel("Y")
plt.xlim(0, area_limit)
plt.ylim(0, area_limit)
plt.grid(True, linestyle='--', linewidth=0.5)
plt.axis('equal')
plt.legend(fontsize=10)
plt.tight_layout()
plt.show()
