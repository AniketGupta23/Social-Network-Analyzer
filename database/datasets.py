from database.connection import get_db_connection


def get_all_datasets():
    connection = get_db_connection()

    if connection is None:
        raise ConnectionError("Could not connect to MySQL.")

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT dataset_id, filename, is_directed, uploaded_at
            FROM datasets
            ORDER BY dataset_id
            """
        )

        datasets = cursor.fetchall()

        for dataset in datasets:
            dataset["is_directed"] = bool(dataset["is_directed"])
            dataset["uploaded_at"] = dataset["uploaded_at"].isoformat()

        return datasets

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


def get_dataset(dataset_id):
    connection = get_db_connection()

    if connection is None:
        raise ConnectionError("Could not connect to MySQL.")

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT dataset_id, filename, is_directed, uploaded_at
            FROM datasets
            WHERE dataset_id = %s
            """,
            (dataset_id,)
        )

        dataset = cursor.fetchone()

        if dataset is None:
            return None

        dataset["is_directed"] = bool(dataset["is_directed"])
        dataset["uploaded_at"] = dataset["uploaded_at"].isoformat()

        return dataset

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


def delete_dataset(dataset_id):
    connection = get_db_connection()

    if connection is None:
        raise ConnectionError("Could not connect to MySQL.")

    cursor = None

    try:
        cursor = connection.cursor()
        connection.start_transaction()

        # Delete edges belonging to the dataset
        cursor.execute(
            """
            DELETE FROM edges
            WHERE dataset_id = %s
            """,
            (dataset_id,)
        )

        # Delete the dataset and its associated nodes
        cursor.execute(
            """
            DELETE FROM datasets
            WHERE dataset_id = %s
            """,
            (dataset_id,)
        )

        deleted = cursor.rowcount > 0

        connection.commit()

        return deleted

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()