import networkx as nx


def find_shortest_path(
    G: nx.Graph,
    source: str,
    target: str
) -> tuple[list[str], int] | None:

    try:
        path = nx.shortest_path(G, source=source, target=target)
        distance = len(path) - 1

        return path, distance

    except (nx.NodeNotFound, nx.NetworkXNoPath):
        return None

def find_weighted_shortest_path(
    G: nx.Graph,
    source: str,
    target: str
) -> tuple[list[str], float] | None:

    try:
        path = nx.dijkstra_path(
            G, source=source, target=target, weight="weight"
        )

        distance = nx.path_weight(G, path, weight="weight")

        return path, float(distance)

    except (nx.NodeNotFound, nx.NetworkXNoPath):
        return None