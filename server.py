from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static')
CORS(app)

tasks = []
task_id = 1

# Serve index.html
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

# Serve static files like CSS/JS
@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks), 200

@app.route("/api/tasks", methods=["POST"])
def add_task():
    global task_id
    data = request.json
    task = {
        "id": task_id,
        "title": data.get("title", ""),
        "completed": False
    }
    tasks.append(task)
    task_id += 1
    return jsonify(task), 201

@app.route("/api/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    data = request.json
    for task in tasks:
        if task["id"] == id:
            task["completed"] = data.get("completed", task["completed"])
            return jsonify(task), 200
    return jsonify({"error": "Task not found"}), 404

@app.route("/api/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    global tasks
    tasks = [t for t in tasks if t["id"] != id]
    return "", 204

# Main runner
if __name__ == "__main__":
    app.run(debug=True)

