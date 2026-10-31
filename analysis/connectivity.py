import networkx as nx


def find_bridges(G: nx.Graph) -> list[tuple[str, str]]:
    return list(nx.bridges(G))


def find_articulation_points(G: nx.Graph) -> list[str]:
    return list(nx.articulation_points(G))