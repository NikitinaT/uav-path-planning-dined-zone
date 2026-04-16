from src.map import generate_map
from src.graph import build_graph
from src.dijkstra import dijkstra_modified
from src.visualize import plot


def main() -> None:
    # Generate synthetic environment
    env = generate_map("config.yaml")

    # Build graph representation
    graph = build_graph(env)

    # Define start and goal nodes
    start = (0, 0)
    goal = (env["width"] - 1, env["height"] - 1)

    # Compute path using modified Dijkstra
    path = dijkstra_modified(graph, start, goal)

    # Visualize the result
    plot(env, path, start, goal)


if __name__ == "__main__":
    main()
