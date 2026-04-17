import matplotlib.pyplot as plt
import numpy as np
import random

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
for (cx, cy) in cluster_centers:
    pts = [(random.uniform(cx - cluster_spread, cx + cluster_spread),
            random.uniform(cy - cluster_spread, cy + cluster_spread))
           for _ in range(random.randint(6, 30))]
    all_points.extend(pts)

points_array = np.array(all_points)

# ---------- Visualization (optimized for IEEE format) ----------
plt.figure(figsize=(8, 8))

# Wi-Fi points as blue crosses with increased size
plt.scatter(points_array[:,0], points_array[:,1], color='blue', s=60, marker='x', label='Wi-Fi points')
plt.scatter(*A, color='green', s=100, marker='.', label='Start Point A')
plt.scatter(*B, color='red', s=100, marker='.', label='End Point B')
# Start (A) and End (B) points with enlarged stars and labels
plt.scatter(A[0], A[1], c='green', s=200, marker='.')
plt.text(A[0]+1, A[1], "A", color='green', fontsize=14)

plt.scatter(B[0], B[1], c='red', s=200, marker='.')
plt.text(B[0]+1, B[1], "B", color='red', fontsize=14)

plt.title("2D Wi-Fi Coverage Map Open Wi-Fi Routers", fontsize=14)
plt.xlabel("X")
plt.ylabel("Y")
plt.xlim(0, area_limit)
plt.ylim(0, area_limit)
plt.grid(True, linestyle='--', linewidth=0.5)
plt.axis('equal')
plt.legend(fontsize=10)
plt.tight_layout()
plt.show()
