from fastapi import APIRouter

from .index import index_router
from .task import task_router

root_router = APIRouter()

root_router.include_router(
    task_router,
    prefix="/tasks",
    tags=["tasks"]
)

root_router.include_router(
    index_router,
)
