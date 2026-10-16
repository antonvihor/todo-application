"""Test user creation, validation, lookup, and deletion through HTTP."""

import pytest
from fastapi.testclient import TestClient

from todo_api._detail import storage


def test_create_user_trims_whitespace(client: TestClient) -> None:
    """Return a stored user with a generated identifier and trimmed name."""
    response = client.post("/users", json={"name": "  Olena  ", "email": "olena@example.com"})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Olena", "email": "olena@example.com"}
    assert client.get("/users/1").json() == response.json()


def test_list_users_preserves_creation_order(client: TestClient, user_id: int) -> None:
    """List all users in the order they were created."""
    second = client.post("/users", json={"name": "Taras", "email": "taras@example.com"})
    response = client.get("/users")
    assert response.status_code == 200
    assert [user["id"] for user in response.json()] == [user_id, second.json()["id"]]


@pytest.mark.parametrize("email", ["olena@example.com", "OLENA@EXAMPLE.COM"])
def test_reject_duplicate_email(client: TestClient, user_id: int, email: str) -> None:
    """Reject duplicate emails without adding a second user."""
    response = client.post("/users", json={"name": "Another user", "email": email})
    assert response.status_code == 409
    assert response.json() == {"detail": "Email is already registered."}
    assert [user["id"] for user in client.get("/users").json()] == [user_id]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": "Olena"},
        {"email": "olena@example.com"},
        {"name": "", "email": "olena@example.com"},
        {"name": "   ", "email": "olena@example.com"},
        {"name": "x" * 81, "email": "olena@example.com"},
        {"name": "Olena", "email": "invalid"},
        {"name": "Olena", "email": None},
        {"name": 123, "email": "olena@example.com"},
        {"name": "Olena", "email": "olena@example.com", "id": 10},
    ],
)
def test_reject_invalid_user(client: TestClient, payload: dict[str, object]) -> None:
    """Reject invalid fields without changing storage."""
    assert client.post("/users", json=payload).status_code == 422
    assert client.get("/users").json() == []


def test_delete_user_cascades_only_owned_todos(client: TestClient, user_id: int, todo_id: int) -> None:
    """Remove the user's todos while preserving other users and tasks."""
    other_user = client.post("/users", json={"name": "Taras", "email": "taras@example.com"}).json()
    other_todo = client.post("/todos", json={"user_id": other_user["id"], "title": "Keep this"}).json()
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/users/{user_id}").status_code == 404
    assert client.get(f"/todos/{todo_id}").status_code == 404
    assert client.get("/users").json() == [other_user]
    assert client.get("/todos").json() == [other_todo]
    assert [todo.id for todo in storage.todos] == [other_todo["id"]]


def test_reuse_email_after_deletion(client: TestClient, user_id: int) -> None:
    """Allow a deleted user's email while assigning a fresh identifier."""
    client.delete(f"/users/{user_id}")
    response = client.post("/users", json={"name": "Olena", "email": "olena@example.com"})
    assert response.status_code == 201
    assert response.json()["id"] > user_id


@pytest.mark.parametrize("method", ["get", "delete"])
def test_missing_user(client: TestClient, method: str) -> None:
    """Report a missing user consistently for reads and deletions."""
    response = client.request(method, "/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}
