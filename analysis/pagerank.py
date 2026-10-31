import networkx as nx


def calculate_pagerank(
    G: nx.Graph | nx.DiGraph,
    damping_factor: float = 0.85
) -> dict[str, float]:

    return nx.pagerank(G, alpha=damping_factor)