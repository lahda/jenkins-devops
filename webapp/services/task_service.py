tasks = [
    {"id": 1, "title": "Setup Jenkins Pipeline", "status": "done", "priority": "high"},
    {"id": 2, "title": "Dockerize the application", "status": "done", "priority": "high"},
    {"id": 3, "title": "Push image to DockerHub", "status": "pending", "priority": "medium"},
    {"id": 4, "title": "Deploy to production", "status": "pending", "priority": "low"},
]

def get_tasks():
    return tasks

def add_task(data):
    new_task = {
        "id": max([t["id"] for t in tasks]) + 1 if tasks else 1,
        "title": data["title"],
        "status": data.get("status", "pending"),
        "priority": data.get("priority", "medium")
    }
    tasks.append(new_task)
    return new_task

def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]