"""Expose HTTP endpoints for todo management."""

from fastapi import APIRouter, Response, status

from todo_api._detail import storage
from todo_api.todos._detail import service
from todo_api.todos._detail.schemas import Todo, TodoCreate, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_todo(payload: TodoCreate) -> Todo:
    """Create an incomplete todo.

    Parameters
    ----------
    payload : TodoCreate
        The owner's identifier, title, and optional description.

    Returns
    -------
    Todo
        The newly created todo.
    """
    return service.create_todo(payload)


@router.get("")
async def list_todos() -> list[Todo]:
    """List todos in creation order.

    Returns
    -------
    list of Todo
        All currently stored todos.
    """
    return storage.todos.copy()


@router.get("/{todo_id}")
async def get_todo(todo_id: int) -> Todo:
    """Retrieve a todo.

    Parameters
    ----------
    todo_id : int
        Identifier of the requested todo.

    Returns
    -------
    Todo
        The requested todo.
    """
    return service.get_todo(todo_id)


@router.patch("/{todo_id}")
async def update_todo(todo_id: int, payload: TodoUpdate) -> Todo:
    """Update the supplied fields of a todo.

    Parameters
    ----------
    todo_id : int
        Identifier of the todo to update.
    payload : TodoUpdate
        Nonempty set of changes.

    Returns
    -------
    Todo
        The updated todo.
    """
    return service.update_todo(todo_id, payload)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int) -> Response:
    """Delete a todo.

    Parameters
    ----------
    todo_id : int
        Identifier of the todo to delete.

    Returns
    -------
    Response
        An empty successful response.
    """
    service.delete_todo(todo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
