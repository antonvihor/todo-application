"""Check the HTTP contract and documentation shared by both resources."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize("path", ["/users", "/todos"])
def test_start_with_empty_lists(client: TestClient, path: str) -> None:
    """Start each test with isolated empty storage."""
    response = client.get(path)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("path", ["/users/not-an-id", "/todos/not-an-id"])
def test_reject_invalid_path_identifier(client: TestClient, path: str) -> None:
    """Validate the identifier before calling a service function."""
    assert client.get(path).status_code == 422


def test_openapi_contains_both_resource_schemas(client: TestClient) -> None:
    """Publish separate user and todo endpoints with their request schemas."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    document = response.json()
    assert set(document["paths"]) == {"/users", "/users/{user_id}", "/todos", "/todos/{todo_id}"}
    assert {"UserCreate", "User", "TodoCreate", "TodoUpdate", "Todo"} <= set(document["components"]["schemas"])
    assert client.get("/docs").status_code == 200
