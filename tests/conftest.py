"""Provide isolated lists and reusable API fixtures."""

from collections.abc import Iterator
from itertools import count

import pytest
from fastapi.testclient import TestClient

from todo_api._detail import storage
from todo_api.main import app


@pytest.fixture(autouse=True)
def reset_storage(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace shared lists and counters before every test.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Fixture that restores module attributes after the test.
    """
    monkeypatch.setattr(storage, "users", [])
    monkeypatch.setattr(storage, "todos", [])
    monkeypatch.setattr(storage, "user_ids", count(1))
    monkeypatch.setattr(storage, "todo_ids", count(1))


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Open an HTTP client for the application.

    Yields
    ------
    TestClient
        A client closed automatically after the test.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def user_id(client: TestClient) -> int:
    """Create a user for tests that need an existing owner.

    Parameters
    ----------
    client : TestClient
        Client connected to the application.

    Returns
    -------
    int
        The created user's identifier.
    """
    response = client.post("/users", json={"name": "Olena", "email": "olena@example.com"})
    assert response.status_code == 201
    return int(response.json()["id"])


@pytest.fixture
def todo_id(client: TestClient, user_id: int) -> int:
    """Create a todo for tests that need an existing task.

    Parameters
    ----------
    client : TestClient
        Client connected to the application.
    user_id : int
        Existing owner's identifier.

    Returns
    -------
    int
        The created todo's identifier.
    """
    response = client.post("/todos", json={"user_id": user_id, "title": "Learn CI", "description": "Run pytest"})
    assert response.status_code == 201
    return int(response.json()["id"])
