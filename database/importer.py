import csv
import math
from pathlib import Path
from database.connection import get_db_connection

def validate_edges_csv(csv_path, directed=False):
    edges = []
    nodes = set()
    seen_edges = set()

    with open(csv_path, mode="r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file is empty.")

        required_columns = {"source", "target"}

        if not required_columns.issubset(reader.fieldnames):
            raise ValueError(
                "CSV must contain 'source' and 'target' columns."
            )

        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("CSV contains duplicate column names.")

        for row_number, row in enumerate(reader, start=2):

            if not any(value and value.strip() for value in row.values() if isinstance(value, str)):
                raise ValueError(
                    f"Row {row_number}: Empty row detected."
                )

            if None in row:
                raise ValueError(
                    f"Row {row_number}: Too many columns."
                )

            if any(value is None for value in row.values()):
                raise ValueError(
                    f"Row {row_number}: Missing column values."
                )

            source = (row["source"] or "").strip()
            target = (row["target"] or "").strip()

            if not source or not target:
                raise ValueError(
                    f"Row {row_number}: Empty source or target."
                )

            if len(source) > 255 or len(target) > 255:
                raise ValueError(
                    f"Row {row_number}: Node label exceeds 255 characters."
                )

            weight_value = row.get("weight")

            if weight_value is None or not weight_value.strip():
                weight = 1.0
            else:
                try:
                    weight = float(weight_value)
                except ValueError:
                    raise ValueError(
                        f"Row {row_number}: Invalid edge weight."
                    )

                if not math.isfinite(weight):
                    raise ValueError(
                        f"Row {row_number}: Weight must be finite."
                    )

            edge_key = (
                (source, target)
                if directed
                else tuple(sorted((source, target)))
            )

            if edge_key in seen_edges:
                raise ValueError(
                    f"Row {row_number}: Duplicate edge detected."
                )

            seen_edges.add(edge_key)
            nodes.update((source, target))
            edges.append((source, target, weight))

    return nodes, edges


def validate_nodes_csv(csv_path):
    nodes = set()

    with open(csv_path, mode="r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("Nodes CSV file is empty.")

        if reader.fieldnames != ["node"]:
            raise ValueError(
                "Nodes CSV must contain exactly one column: 'node'."
            )

        for row_number, row in enumerate(reader, start=2):
            node = (row["node"] or "").strip()

            if not node:
                raise ValueError(
                    f"Row {row_number}: Empty node identifier."
                )

            if len(node) > 255:
                raise ValueError(
                    f"Row {row_number}: Node label exceeds 255 characters."
                )

            if node in nodes:
                raise ValueError(
                    f"Row {row_number}: Duplicate node detected."
                )

            nodes.add(node)

    return nodes



def import_dataset(csv_path, directed=False, nodes_csv_path=None):
    # Validate CSV files before connecting to MySQL
    edge_nodes, edges = validate_edges_csv(csv_path, directed)

    if nodes_csv_path is not None:
        extra_nodes = validate_nodes_csv(nodes_csv_path)
        all_nodes = edge_nodes | extra_nodes
    else:
        all_nodes = edge_nodes

    connection = get_db_connection()

    if connection is None:
        raise ConnectionError("Could not connect to MySQL.")

    cursor = None

    try:
        cursor = connection.cursor()
        connection.start_transaction()

        # Insert dataset information
        cursor.execute(
            """
            INSERT INTO datasets (filename, is_directed)
            VALUES (%s, %s)
            """,
            (Path(csv_path).name, directed)
        )

        dataset_id = cursor.lastrowid

        # Insert unique nodes
        node_ids = {}

        for node in sorted(all_nodes):
            cursor.execute(
                """
                INSERT INTO nodes (dataset_id, node_label)
                VALUES (%s, %s)
                """,
                (dataset_id, node)
            )

            node_ids[node] = cursor.lastrowid

        # Insert edges using their corresponding node IDs
        for source, target, weight in edges:
            source_id = node_ids[source]
            target_id = node_ids[target]

            # Normalize undirected edges
            if not directed and source_id > target_id:
                source_id, target_id = target_id, source_id

            cursor.execute(
                """
                INSERT INTO edges (
                    dataset_id,
                    source_node_id,
                    target_node_id,
                    weight
                )
                VALUES (%s, %s, %s, %s)
                """,
                (dataset_id, source_id, target_id, weight)
            )

        connection.commit()

        return dataset_id

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()
