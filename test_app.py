import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'webapp'))
from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config.update({"TESTING": True})
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"

def test_get_tasks(client):
    res = client.get("/api/tasks")
    assert res.status_code == 200
    data = res.get_json()
    assert "tasks" in data
    assert isinstance(data["tasks"], list)

def test_create_task(client):
    res = client.post("/api/tasks", json={"title": "Test task", "priority": "high"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["title"] == "Test task"

def test_create_task_missing_title(client):
    res = client.post("/api/tasks", json={"priority": "low"})
    assert res.status_code == 400

def test_delete_task(client):
    # Create then delete
    create_res = client.post("/api/tasks", json={"title": "To delete"})
    task_id = create_res.get_json()["id"]
    del_res = client.delete(f"/api/tasks/{task_id}")
    assert del_res.status_code == 200

def test_delete_nonexistent_task(client):
    res = client.delete("/api/tasks/99999")
    assert res.status_code == 404

def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200
