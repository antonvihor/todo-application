"""Create the FastAPI application and register the resource routers."""

from fastapi import FastAPI

from todo_api.todos._detail.router import router as todos_router
from todo_api.users._detail.router import router as users_router

app = FastAPI(title="Todo Application API Service", version="0.1.0")
app.include_router(users_router)
app.include_router(todos_router)
