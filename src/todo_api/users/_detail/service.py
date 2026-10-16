"""Create, find, and delete users in the shared list."""

from fastapi import HTTPException, status

from todo_api._detail import storage
from todo_api.users._detail.schemas import User, UserCreate


def create_user(payload: UserCreate) -> User:
    """Add a user with a case-insensitively unique email.

    Parameters
    ----------
    payload : UserCreate
        Validated user name and email address.

    Returns
    -------
    User
        The newly stored user.

    Raises
    ------
    HTTPException
        If another user already has the requested email.
    """
    if any(user.email.casefold() == payload.email.casefold() for user in storage.users):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email is already registered.")
    user = User(id=next(storage.user_ids), name=payload.name, email=payload.email)
    storage.users.append(user)
    return user


def get_user(user_id: int) -> User:
    """Find a user by identifier.

    Parameters
    ----------
    user_id : int
        Identifier of the requested user.

    Returns
    -------
    User
        The matching user.

    Raises
    ------
    HTTPException
        If the user does not exist.
    """
    for user in storage.users:
        if user.id == user_id:
            return user
    raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")


def delete_user(user_id: int) -> None:
    """Delete a user and their todos.

    Parameters
    ----------
    user_id : int
        Identifier of the user to delete.
    """
    user = get_user(user_id)
    storage.users.remove(user)
    storage.todos[:] = [todo for todo in storage.todos if todo.user_id != user_id]
