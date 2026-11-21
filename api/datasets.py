from pathlib import Path
from tempfile import TemporaryDirectory

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from database.datasets import get_all_datasets, get_dataset, delete_dataset
from database.importer import import_dataset

from werkzeug.exceptions import RequestEntityTooLarge

datasets_bp = Blueprint(
    "datasets",
    __name__,
    url_prefix="/api/datasets"
)


@datasets_bp.route("", methods=["GET"])
def list_datasets():
    try:
        datasets = get_all_datasets()

        return jsonify({
            "status": "success",
            "count": len(datasets),
            "data": datasets
        }), 200

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve datasets."
        }), 500


@datasets_bp.route("/<int:dataset_id>", methods=["GET"])
def retrieve_dataset(dataset_id):
    try:
        dataset = get_dataset(dataset_id)

        if dataset is None:
            return jsonify({
                "status": "error",
                "message": f"Dataset with ID {dataset_id} does not exist."
            }), 404

        return jsonify({
            "status": "success",
            "data": dataset
        }), 200

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve dataset."
        }), 500


@datasets_bp.route("", methods=["POST"])
def upload_dataset():
    try:
        edges_file = request.files.get("edges_file")
        nodes_file = request.files.get("nodes_file")

        directed_value = request.form.get(
            "is_directed", "false"
        ).strip().lower()

        # Validate directed parameter
        if directed_value not in ("true", "false"):
            raise ValueError(
                "is_directed must be true or false."
            )

        directed = directed_value == "true"

        # Validate required edges file
        if edges_file is None or not edges_file.filename:
            raise ValueError("Edges CSV file is required.")

        edges_filename = secure_filename(edges_file.filename)

        if not edges_filename.lower().endswith(".csv"):
            raise ValueError("Edges file must be a CSV file.")

        if len(edges_filename) > 255:
            raise ValueError("Edges filename exceeds 255 characters.")

        # Validate optional nodes file
        if nodes_file is not None:
            if not nodes_file.filename:
                raise ValueError("Nodes filename is missing.")

            nodes_filename = secure_filename(nodes_file.filename)

            if not nodes_filename.lower().endswith(".csv"):
                raise ValueError("Nodes file must be a CSV file.")

        # Create temporary directory
        with TemporaryDirectory() as temp_dir:
            edges_path = Path(temp_dir) / "edges.csv"
            edges_file.save(edges_path)

            nodes_path = None

            if nodes_file is not None:
                nodes_path = Path(temp_dir) / "nodes.csv"
                nodes_file.save(nodes_path)

            # Import dataset into MySQL
            dataset_id = import_dataset(
                csv_path=edges_path,
                directed=directed,
                nodes_csv_path=nodes_path,
                filename=edges_filename
            )

        return jsonify({
            "status": "success",
            "message": "Dataset uploaded successfully.",
            "dataset_id": dataset_id
        }), 201

    except RequestEntityTooLarge:
        return jsonify({
            "status": "error",
            "message": "Upload exceeds the 10 MiB limit."
        }), 413

    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Failed to upload dataset."
        }), 500


@datasets_bp.route("/<int:dataset_id>", methods=["DELETE"])
def remove_dataset(dataset_id):
    try:
        deleted = delete_dataset(dataset_id)

        if not deleted:
            return jsonify({
                "status": "error",
                "message": f"Dataset with ID {dataset_id} does not exist."
            }), 404

        return jsonify({
            "status": "success",
            "message": "Dataset deleted successfully.",
            "dataset_id": dataset_id
        }), 200

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Failed to delete dataset."
        }), 500