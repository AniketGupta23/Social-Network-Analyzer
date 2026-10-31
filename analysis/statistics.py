import networkx as nx


def calculate_basic_statistics(G: nx.Graph) -> dict[str, int | float]:

    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()

    average_degree = (
        sum(dict(G.degree()).values()) / num_nodes
        if num_nodes > 0 else 0.0
    )

    density = nx.density(G)

    return {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "average_degree": average_degree,
        "density": density
    }

def calculate_average_clustering(G: nx.Graph) -> float:

    if G.number_of_nodes() == 0:
        return 0.0

    return nx.average_clustering(G)


def calculate_connected_components(
    G: nx.Graph
) -> dict[str, int | list[set[str]]]:

    components = list(nx.connected_components(G))

    return {
        "num_components": len(components),
        "components": [set(component) for component in components]
    }


def calculate_average_shortest_path(
    G: nx.Graph
) -> float | None:

    if G.number_of_nodes() == 0:
        return None

    if G.number_of_nodes() == 1:
        return 0.0

    if not nx.is_connected(G):
        return None

    return nx.average_shortest_path_length(G)