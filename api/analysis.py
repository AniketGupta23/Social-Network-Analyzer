from flask import Blueprint, jsonify, request
from database.loader import load_graph
from analysis.statistics import calculate_basic_statistics
from analysis.centrality import (
    calculate_degree_centrality,
    calculate_betweenness_centrality,
    calculate_closeness_centrality,
    calculate_eigenvector_centrality)
import networkx as nx
from analysis.pagerank import calculate_pagerank
from analysis.paths import find_shortest_path, find_weighted_shortest_path
from analysis.communities import (
    detect_communities,
    detect_communities_girvan_newman,
    calculate_modularity)
from analysis.statistics import (
    calculate_basic_statistics,
    calculate_average_clustering,
    calculate_connected_components,
    calculate_average_shortest_path
)
from analysis.connectivity import find_bridges, find_articulation_points


analysis_bp = Blueprint(
    "analysis",
    __name__,
    url_prefix="/api/datasets"
)

@analysis_bp.route("/<int:dataset_id>/statistics", methods=["GET"])
def retrieve_statistics(dataset_id):
    try:
        graph = load_graph(dataset_id)
        statistics = calculate_basic_statistics(graph)

        return jsonify({
            "status": "success",
            "data": {
                "dataset_id": dataset_id,
                **statistics
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
            "message": "Failed to calculate network statistics."
        }), 500


@analysis_bp.route("/<int:dataset_id>/centrality", methods=["GET"])
def retrieve_centrality(dataset_id):

    measure = request.args.get("measure", "degree").lower()

    centrality_functions = {
        "degree": calculate_degree_centrality,
        "betweenness": calculate_betweenness_centrality,
        "closeness": calculate_closeness_centrality,
        "eigenvector": calculate_eigenvector_centrality
    }

    if measure not in centrality_functions:
        return jsonify({
            "status": "error",
            "message": "Invalid centrality measure."
        }), 400

    try:
        graph = load_graph(dataset_id)

        centrality = centrality_functions[measure](graph)

        if measure == "eigenvector" and graph.number_of_nodes() > 0 and not centrality:
            return jsonify({
                "status": "error",
                "message": "Eigenvector centrality failed to converge."
            }), 422

        return jsonify({
            "status": "success",
            "data": {
                "dataset_id": dataset_id,
                "measure": measure,
                "centrality": centrality
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
            "message": "Failed to calculate centrality."
        }), 500


@analysis_bp.route("/<int:dataset_id>/pagerank", methods=["GET"])
def retrieve_pagerank(dataset_id):

    try:
        damping_factor = float(
            request.args.get("damping_factor", "0.85")
        )

    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Damping factor must be a valid number."
        }), 400

    if not 0 < damping_factor < 1:
        return jsonify({
            "status": "error",
            "message": "Damping factor must be between 0 and 1 (exclusive)."
        }), 400

    try:
        graph = load_graph(dataset_id)

        pagerank = calculate_pagerank(graph, damping_factor)

        return jsonify({
            "status": "success",
            "data": {
                "dataset_id": dataset_id,
                "damping_factor": damping_factor,
                "pagerank": pagerank
            }
        }), 200

    except nx.PowerIterationFailedConvergence:
        return jsonify({
            "status": "error",
            "message": "PageRank failed to converge."
        }), 422

    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Failed to calculate PageRank."
        }), 500


@analysis_bp.route("/<int:dataset_id>/shortest-path", methods=["GET"])
def retrieve_shortest_path(dataset_id):

    source = request.args.get("source")
    target = request.args.get("target")
    weighted = request.args.get("weighted", "false").lower()

    if not source or not target:
        return jsonify({
            "status": "error",
            "message": "Source and target nodes are required."
        }), 400

    if weighted not in ("true", "false"):
        return jsonify({
            "status": "error",
            "message": "Weighted must be true or false."
        }), 400

    weighted = weighted == "true"

    try:
        graph = load_graph(dataset_id)

        if source not in graph:
            return jsonify({
                "status": "error",
                "message": "Source node does not exist."
            }), 404

        if target not in graph:
            return jsonify({
                "status": "error",
                "message": "Target node does not exist."
            }), 404

        if weighted:
            if any(
                data.get("weight", 1.0) < 0
                for _, _, data in graph.edges(data=True)
            ):
                return jsonify({
                    "status": "error",
                    "message": "Weighted shortest path does not support negative edge weights."
                }), 422

            result = find_weighted_shortest_path(
                graph, source, target
            )

        else:
            result = find_shortest_path(
                graph, source, target
            )

        path, distance = result if result is not None else (None, None)

        return jsonify({
            "status": "success",
            "data": {
                "dataset_id": dataset_id,
                "source": source,
                "target": target,
                "weighted": weighted,
                "path_found": result is not None,
                "path": path,
                "distance": distance
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
            "message": "Failed to calculate shortest path."
        }), 500


@analysis_bp.route("/<int:dataset_id>/communities", methods=["GET"])
def retrieve_communities(dataset_id):

    algorithm = request.args.get("algorithm", "greedy").lower()

    if algorithm not in ("greedy", "girvan-newman"):
        return jsonify({
            "status": "error",
            "message": "Invalid community detection algorithm."
        }), 400

    num_communities = None

    if algorithm == "girvan-newman":
        try:
            num_communities = int(
                request.args.get("num_communities", "2")
            )

        except ValueError:
            return jsonify({
                "status": "error",
                "message": "Number of communities must be an integer."
            }), 400

        if num_communities < 2:
            return jsonify({
                "status": "error",
                "message": "Number of communities must be at least 2."
            }), 400

    try:
        graph = load_graph(dataset_id)

        if algorithm == "girvan-newman" and graph.is_directed():
            return jsonify({
                "status": "error",
                "message": "Girvan-Newman requires an undirected graph."
            }), 422

        if (
            num_communities is not None
            and num_communities > graph.number_of_nodes()
        ):
            return jsonify({
                "status": "error",
                "message": "Number of communities exceeds number of nodes."
            }), 400

        if any(
            data.get("weight", 1.0) < 0
            for _, _, data in graph.edges(data=True)
        ):
            return jsonify({
                "status": "error",
                "message": "Community analysis does not support negative edge weights."
            }), 422

        if graph.number_of_edges() == 0:
            communities = [{node} for node in graph.nodes()]
            modularity = None

        else:
            if algorithm == "greedy":
                communities = detect_communities(graph)

            else:
                communities = detect_communities_girvan_newman(
                    graph, num_communities
                )

            modularity = calculate_modularity(graph, communities)

        communities = [
            sorted(community)
            for community in communities
        ]

        return jsonify({
            "status": "success",
            "data": {
                "dataset_id": dataset_id,
                "algorithm": algorithm,
                "requested_num_communities": num_communities,
                "num_communities": len(communities),
                "communities": communities,
                "modularity": modularity
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
            "message": "Failed to detect communities."
        }), 500


@analysis_bp.route("/<int:dataset_id>/clustering", methods=["GET"])
def retrieve_clustering(dataset_id):

    try:
        graph = load_graph(dataset_id)

        average_clustering = calculate_average_clustering(graph)

        return jsonify({
            "status": "success",
            "data": {
                "dataset_id": dataset_id,
                "average_clustering": average_clustering
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
            "message": "Failed to calculate clustering coefficient."
        }), 500


@analysis_bp.route("/<int:dataset_id>/components", methods=["GET"])
def retrieve_components(dataset_id):

    try:
        graph = load_graph(dataset_id)

        if graph.is_directed():
            return jsonify({
                "status": "error",
                "message": "Connected components require an undirected graph."
            }), 422

        result = calculate_connected_components(graph)

        components = [
            sorted(component)
            for component in result["components"]
        ]

        return jsonify({
            "status": "success",
            "data": {
                "dataset_id": dataset_id,
                "num_components": result["num_components"],
                "components": components
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
            "message": "Failed to calculate connected components."
        }), 500


@analysis_bp.route("/<int:dataset_id>/bridges", methods=["GET"])
def retrieve_bridges(dataset_id):

    try:
        graph = load_graph(dataset_id)

        if graph.is_directed():
            return jsonify({
                "status": "error",
                "message": "Bridge detection requires an undirected graph."
            }), 422

        bridges = find_bridges(graph)

        return jsonify({
            "status": "success",
            "data": {
                "dataset_id": dataset_id,
                "num_bridges": len(bridges),
                "bridges": [
                    {"source": source, "target": target}
                    for source, target in bridges
                ]
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
            "message": "Failed to detect bridges."
        }), 500


@analysis_bp.route("/<int:dataset_id>/articulation-points", methods=["GET"])
def retrieve_articulation_points(dataset_id):

    try:
        graph = load_graph(dataset_id)

        if graph.is_directed():
            return jsonify({
                "status": "error",
                "message": "Articulation point detection requires an undirected graph."
            }), 422

        articulation_points = find_articulation_points(graph)

        return jsonify({
            "status": "success",
            "data": {
                "dataset_id": dataset_id,
                "num_articulation_points": len(articulation_points),
                "articulation_points": sorted(articulation_points)
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
            "message": "Failed to detect articulation points."
        }), 500


@analysis_bp.route("/<int:dataset_id>/average-shortest-path", methods=["GET"])
def retrieve_average_shortest_path(dataset_id):

    try:
        graph = load_graph(dataset_id)

        if graph.is_directed():
            return jsonify({
                "status": "error",
                "message": "Average shortest path calculation requires an undirected graph."
            }), 422

        average_shortest_path = calculate_average_shortest_path(graph)

        return jsonify({
            "status": "success",
            "data": {
                "dataset_id": dataset_id,
                "average_shortest_path": average_shortest_path
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
            "message": "Failed to calculate average shortest path length."
        }), 500