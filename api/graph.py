from flask import Blueprint, jsonify

from database.loader import load_graph


graph_bp = Blueprint(
    "graph",
    __name__,
    url_prefix="/api/datasets"
)


@graph_bp.route("/<int:dataset_id>/graph", methods=["GET"])
def retrieve_graph(dataset_id):
    try:
        graph = load_graph(dataset_id)

        nodes = [
            {"id": node}
            for node in graph.nodes()
        ]

        edges = [
            {
                "source": source,
                "target": target,
                "weight": data.get("weight", 1.0)
            }
            for source, target, data in graph.edges(data=True)
        ]

        return jsonify({
            "status": "success",
            "data": {
                "dataset_id": dataset_id,
                "is_directed": graph.is_directed(),
                "num_nodes": graph.number_of_nodes(),
                "num_edges": graph.number_of_edges(),
                "nodes": nodes,
                "edges": edges
            }
        }), 200

    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve graph."
        }), 500