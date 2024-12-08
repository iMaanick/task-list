from fastapi import APIRouter

from .index import index_router
from .task import task_router
from ..application.auth_backend import auth_backend
from ..application.fastapi_users import fastapi_users
from ..application.models.user import UserRead, UserCreate

root_router = APIRouter()

root_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

root_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

root_router.include_router(
    task_router,
    prefix="/tasks",
    tags=["tasks"]
)

root_router.include_router(
    index_router,
)
