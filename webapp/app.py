from flask import Flask, jsonify, render_template, request
import os
import socket
import datetime

app = Flask(__name__)

tasks = [
    {"id": 1, "title": "Setup Jenkins Pipeline", "status": "done", "priority": "high"},
    {"id": 2, "title": "Dockerize the application", "status": "done", "priority": "high"},
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
    })

@app.route("/api/tasks")
def get_tasks():
    return jsonify({"tasks": tasks})

# ⚠️ IMPORTANT : bloc main obligatoire
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)