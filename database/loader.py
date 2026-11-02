
import networkx as nx

from database.connection import get_db_connection


def load_graph(dataset_id):
    connection = get_db_connection()

    if connection is None:
        raise ConnectionError("Could not connect to MySQL.")

    cursor = None

    try:
        cursor = connection.cursor()

        # Retrieve dataset metadata
        cursor.execute(
            """
            SELECT is_directed
            FROM datasets
            WHERE dataset_id = %s
            """,
            (dataset_id,)
        )

        result = cursor.fetchone()

        if result is None:
            raise ValueError(
                f"Dataset with ID {dataset_id} does not exist."
            )

        is_directed = bool(result[0])

        # Create the appropriate NetworkX graph
        graph = nx.DiGraph() if is_directed else nx.Graph()

        # Retrieve nodes
        cursor.execute(
            """
            SELECT node_label
            FROM nodes
            WHERE dataset_id = %s
            """,
            (dataset_id,)
        )

        for (node_label,) in cursor.fetchall():
            graph.add_node(node_label)

        # Retrieve edges with their weights
        cursor.execute(
            """
            SELECT
                source.node_label,
                target.node_label,
                edges.weight
            FROM edges
            JOIN nodes AS source
                ON edges.source_node_id = source.node_id
            JOIN nodes AS target
                ON edges.target_node_id = target.node_id
            WHERE edges.dataset_id = %s
            """,
            (dataset_id,)
        )

        for source, target, weight in cursor.fetchall():
            graph.add_edge(source, target, weight=weight)

        return graph

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()
