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

    if num_communities < 2 or num_communities > G.number_of_nodes():
        raise ValueError("Invalid number of communities")

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