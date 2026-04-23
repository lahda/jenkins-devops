from flask import Blueprint, jsonify, request
from ..services.task_service import get_tasks, add_task, delete_task

api = Blueprint("api", __name__)

@api.route("/tasks", methods=["GET"])
def tasks():
    return jsonify({"tasks": get_tasks(), "total": len(get_tasks())})

@api.route("/tasks", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Title required"}), 400
    return jsonify(add_task(data)), 201

@api.route("/tasks/<int:task_id>", methods=["DELETE"])
def remove(task_id):
    delete_task(task_id)
    return jsonify({"message": "deleted"})