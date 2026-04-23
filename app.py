from flask import Flask, jsonify, render_template, request
import os
import socket
import datetime

app = Flask(__name__)

# In-memory task store
tasks = [
    {"id": 1, "title": "Setup Jenkins Pipeline", "status": "done", "priority": "high"},
    {"id": 2, "title": "Dockerize the application", "status": "done", "priority": "high"},
    {"id": 3, "title": "Push image to DockerHub", "status": "pending", "priority": "medium"},
    {"id": 4, "title": "Deploy to production", "status": "pending", "priority": "low"},
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "hostname": socket.gethostname(),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "version": os.getenv("APP_VERSION", "1.0.0")
    }), 200

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify({"tasks": tasks, "total": len(tasks)}), 200

@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400
    new_task = {
        "id": max(t["id"] for t in tasks) + 1 if tasks else 1,
        "title": data["title"],
        "status": data.get("status", "pending"),
        "priority": data.get("priority", "medium")
    }
    tasks.append(new_task)
    return jsonify(new_task), 201

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    tasks = [t for t in tasks if t["id"] != task_id]
    return jsonify({"message": "Task deleted"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
