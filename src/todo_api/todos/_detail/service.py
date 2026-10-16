"""Create, find, update, and delete todos in the shared list."""

from fastapi import HTTPException, status

from todo_api._detail import storage
from todo_api.todos._detail.schemas import Todo, TodoCreate, TodoUpdate
from todo_api.users._detail.service import get_user


def create_todo(payload: TodoCreate) -> Todo:
    """Add a todo for an existing user.

    Parameters
    ----------
    payload : TodoCreate
        The owner's identifier, title, and description.

    Returns
    -------
    Todo
        The newly stored todo.
    """
    get_user(payload.user_id)
    todo = Todo(id=next(storage.todo_ids), **payload.model_dump())
    storage.todos.append(todo)
    return todo


def get_todo(todo_id: int) -> Todo:
    """Find a todo by identifier.

    Parameters
    ----------
    todo_id : int
        Identifier of the requested todo.

    Returns
    -------
    Todo
        The matching todo.

    Raises
    ------
    HTTPException
        If the todo does not exist.
    """
    for todo in storage.todos:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Todo not found.")


def update_todo(todo_id: int, payload: TodoUpdate) -> Todo:
    """Apply only the fields explicitly supplied in an update.

    Parameters
    ----------
    todo_id : int
        Identifier of the todo to update.
    payload : TodoUpdate
        Validated changes; omitted fields retain their values.

    Returns
    -------
    Todo
        The updated todo.
    """
    current = get_todo(todo_id)
    updated = current.model_copy(update=payload.model_dump(exclude_unset=True))
    storage.todos[storage.todos.index(current)] = updated
    return updated


def delete_todo(todo_id: int) -> None:
    """Delete a todo.

    Parameters
    ----------
    todo_id : int
        Identifier of the todo to delete.
    """
    storage.todos.remove(get_todo(todo_id))
