"""Keep all application data in Python lists for one server process."""

from itertools import count

from todo_api.todos._detail.schemas import Todo
from todo_api.users._detail.schemas import User

users: list[User] = []
todos: list[Todo] = []
user_ids = count(1)
todo_ids = count(1)
