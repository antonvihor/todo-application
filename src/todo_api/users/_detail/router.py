"""Expose HTTP endpoints for user management."""

from fastapi import APIRouter, Response, status

from todo_api._detail import storage
from todo_api.users._detail import service
from todo_api.users._detail.schemas import User, UserCreate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate) -> User:
    """Create a user.

    Parameters
    ----------
    payload : UserCreate
        User name and email address.

    Returns
    -------
    User
        The newly created user.
    """
    return service.create_user(payload)


@router.get("")
async def list_users() -> list[User]:
    """List users in creation order.

    Returns
    -------
    list of User
        All currently stored users.
    """
    return storage.users.copy()


@router.get("/{user_id}")
async def get_user(user_id: int) -> User:
    """Retrieve a user.

    Parameters
    ----------
    user_id : int
        Identifier of the requested user.

    Returns
    -------
    User
        The requested user.
    """
    return service.get_user(user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int) -> Response:
    """Delete a user and their todos.

    Parameters
    ----------
    user_id : int
        Identifier of the user to delete.

    Returns
    -------
    Response
        An empty successful response.
    """
    service.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
