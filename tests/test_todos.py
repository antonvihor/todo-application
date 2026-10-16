"""Test todo creation, partial updates, validation, and deletion."""

import pytest
from fastapi.testclient import TestClient


def test_create_todo_with_defaults(client: TestClient, user_id: int) -> None:
    """Create an incomplete todo with an empty description by default."""
    response = client.post("/todos", json={"user_id": user_id, "title": "  Learn CI  "})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "user_id": user_id, "title": "Learn CI", "description": "", "completed": False}
    assert client.get("/todos/1").json() == response.json()


def test_list_todos_preserves_creation_order(client: TestClient, user_id: int, todo_id: int) -> None:
    """List todos in creation order."""
    second = client.post("/todos", json={"user_id": user_id, "title": "Read the workflow"})
    response = client.get("/todos")
    assert response.status_code == 200
    assert [todo["id"] for todo in response.json()] == [todo_id, second.json()["id"]]


def test_reject_todo_for_missing_user(client: TestClient) -> None:
    """Require an existing owner before storing a todo."""
    response = client.post("/todos", json={"user_id": 999, "title": "Learn CI"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}
    assert client.get("/todos").json() == []


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": "Learn CI"},
        {"user_id": 1},
        {"user_id": 0, "title": "Learn CI"},
        {"user_id": -1, "title": "Learn CI"},
        {"user_id": 1, "title": ""},
        {"user_id": 1, "title": "   "},
        {"user_id": 1, "title": "x" * 121},
        {"user_id": 1, "title": "Learn CI", "description": "x" * 1001},
        {"user_id": 1, "title": "Learn CI", "completed": True},
        {"user_id": 1, "title": "Learn CI", "id": 5},
    ],
)
def test_reject_invalid_todo(client: TestClient, user_id: int, payload: dict[str, object]) -> None:
    """Reject invalid todo payloads without adding a record."""
    assert user_id == 1
    assert client.post("/todos", json=payload).status_code == 422
    assert client.get("/todos").json() == []


@pytest.mark.parametrize(
    "changes",
    [
        {"title": "Write tests"},
        {"description": "Check GitHub Actions"},
        {"description": ""},
        {"completed": True},
        {"title": "Write tests", "description": "", "completed": True},
    ],
)
def test_update_only_supplied_fields(client: TestClient, todo_id: int, changes: dict[str, object]) -> None:
    """Persist supplied fields while retaining every omitted field."""
    original = client.get(f"/todos/{todo_id}").json()
    response = client.patch(f"/todos/{todo_id}", json=changes)
    assert response.status_code == 200
    assert response.json() == original | changes
    assert client.get(f"/todos/{todo_id}").json() == original | changes


def test_mark_completed_todo_incomplete(client: TestClient, todo_id: int) -> None:
    """Apply an explicit false value instead of treating it as missing."""
    client.patch(f"/todos/{todo_id}", json={"completed": True})
    response = client.patch(f"/todos/{todo_id}", json={"completed": False})
    assert response.status_code == 200
    assert response.json()["completed"] is False


@pytest.mark.parametrize(
    "changes",
    [
        {},
        {"title": None},
        {"description": None},
        {"completed": None},
        {"title": ""},
        {"title": "   "},
        {"title": "x" * 121},
        {"description": "x" * 1001},
        {"completed": "yes"},
        {"completed": 1},
        {"user_id": 2},
        {"id": 2},
    ],
)
def test_reject_invalid_update(client: TestClient, todo_id: int, changes: dict[str, object]) -> None:
    """Reject invalid updates without altering the stored todo."""
    original = client.get(f"/todos/{todo_id}").json()
    assert client.patch(f"/todos/{todo_id}", json=changes).status_code == 422
    assert client.get(f"/todos/{todo_id}").json() == original


def test_delete_todo(client: TestClient, user_id: int, todo_id: int) -> None:
    """Delete only the requested todo and retain its owner."""
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/todos/{todo_id}").status_code == 404
    assert client.get("/todos").json() == []
    assert client.get(f"/users/{user_id}").status_code == 200


def test_do_not_reuse_deleted_todo_id(client: TestClient, user_id: int, todo_id: int) -> None:
    """Assign a fresh identifier after deleting the previous todo."""
    client.delete(f"/todos/{todo_id}")
    response = client.post("/todos", json={"user_id": user_id, "title": "Next task"})
    assert response.status_code == 201
    assert response.json()["id"] > todo_id


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_missing_todo(client: TestClient, method: str) -> None:
    """Report a missing todo consistently for all item operations."""
    response = client.request(method, "/todos/999", json={"completed": True} if method == "patch" else None)
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found."}
