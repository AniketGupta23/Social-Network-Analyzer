import networkx as nx


def detect_communities(
    G: nx.Graph
) -> list[set[str]]:

    communities = nx.community.greedy_modularity_communities(G)

    return [set(community) for community in communities]

def detect_communities_girvan_newman(
    G: nx.Graph,
    num_communities: int = 2
) -> list[set[str]]:

    if num_communities < 2:
        raise ValueError("Number of communities must be at least 2")

    num_nodes = G.number_of_nodes()

    if num_nodes == 0:
        return []

    if num_nodes == 1:
        return [set(G.nodes())]

    if num_communities > num_nodes:
        raise ValueError("Number of communities exceeds number of nodes")

    components = list(nx.connected_components(G))

    if len(components) >= num_communities:
        return [set(component) for component in components]

    communities = nx.community.girvan_newman(G)

    for partition in communities:
        if len(partition) >= num_communities:
            return [set(community) for community in partition]

    return []

def calculate_modularity(
    G: nx.Graph,
    communities: list[set[str]]
) -> float:

    return nx.community.modularity(G, communities)