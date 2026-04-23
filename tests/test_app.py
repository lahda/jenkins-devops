import pytest
from webapp.app import app

# ─────────────────────────────
# FIXTURE CLIENT FLASK
# ─────────────────────────────
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# ─────────────────────────────
# TEST HEALTHCHECK
# ─────────────────────────────
def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200

    data = res.get_json()
    assert data["status"] == "healthy"

# ─────────────────────────────
# TEST GET TASKS
# ─────────────────────────────
def test_get_tasks(client):
    res = client.get("/api/tasks")
    assert res.status_code == 200

    data = res.get_json()
    assert "tasks" in data
    assert isinstance(data["tasks"], list)

# ─────────────────────────────
# TEST CREATE TASK
# ─────────────────────────────
def test_create_task(client):
    res = client.post("/api/tasks", json={
        "title": "Test task",
        "priority": "high"
    })

    assert res.status_code == 201

    data = res.get_json()
    assert data["title"] == "Test task"

# ─────────────────────────────
# TEST BAD REQUEST
# ─────────────────────────────
def test_create_task_missing_title(client):
    res = client.post("/api/tasks", json={})
    assert res.status_code == 400

# ─────────────────────────────
# TEST DELETE TASK
# ─────────────────────────────
def test_delete_task(client):
    create = client.post("/api/tasks", json={"title": "Temp"})
    task_id = create.get_json()["id"]

    res = client.delete(f"/api/tasks/{task_id}")
    assert res.status_code == 200

# ─────────────────────────────
# TEST INDEX PAGE
# ─────────────────────────────
def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200