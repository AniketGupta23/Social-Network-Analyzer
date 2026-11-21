from flask import Flask, jsonify
from api.datasets import datasets_bp

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

app.register_blueprint(datasets_bp)


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "success",
        "message": "Social Network Analyzer API is running"
    }), 200


if __name__ == "__main__":
    app.run(debug=True)