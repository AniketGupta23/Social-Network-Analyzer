from flask import Blueprint, jsonify
from database.datasets import get_all_datasets, get_dataset

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