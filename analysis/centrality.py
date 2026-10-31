import networkx as nx


def calculate_degree_centrality(
    G: nx.Graph
) -> dict[str, float]:

    return nx.degree_centrality(G)


def calculate_betweenness_centrality(
    G: nx.Graph
) -> dict[str, float]:

    return nx.betweenness_centrality(G)


def calculate_closeness_centrality(
    G: nx.Graph
) -> dict[str, float]:

    return nx.closeness_centrality(G)


def calculate_eigenvector_centrality(G: nx.Graph) -> dict[str, float]:

    if G.number_of_nodes() == 0:
        return {}

    try:
        return nx.eigenvector_centrality(G, max_iter=1000)

    except nx.PowerIterationFailedConvergence:
        return {}