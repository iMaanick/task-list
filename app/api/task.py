from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.adapters.sqlalchemy_db.models import User
from app.api.depends_stub import Stub
from app.application.exceptions import MissingTasksError, DataConflictError, TaskNotFoundError
from app.application.fastapi_users import fastapi_users
from app.application.models import TaskCreate, TaskResponse, TaskTitleUpdate, TaskUpdate, ReorderRequest
from app.application.protocols.database import DatabaseGateway, UserDataBaseGateway
from app.application.task import add_task, delete_task_from_list, get_tasks, update_task_title_by_id, update_task_by_id, \
    tasks_reorder

task_router = APIRouter()


@task_router.post("/", response_model=TaskResponse)
async def create_task(
        database: Annotated[DatabaseGateway, Depends()],
        task: TaskCreate,
        user: User = Depends(fastapi_users.current_user(optional=True)),
) -> TaskResponse:
    print(task)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    new_task = await add_task(user.id, task, database)
    return new_task


@task_router.delete("/{task_id}")
async def delete_task(
        database: Annotated[DatabaseGateway, Depends()],
        task_id: int,
        user: User = Depends(fastapi_users.current_user(optional=True)),

) -> dict:
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    deleted_task_id = await delete_task_from_list(user.id, task_id, database)
    if deleted_task_id is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}


@task_router.get("/", response_model=list[TaskResponse])
async def read_tasks(
        database: Annotated[DatabaseGateway, Depends()],
        user: User = Depends(fastapi_users.current_user(optional=True)),
        skip: int = 0,
        limit: int = 10,
) -> list[TaskResponse]:
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    tasks = await get_tasks(user.id, skip, limit, database)
    return tasks


@task_router.patch("/{task_id}/title", response_model=TaskResponse)
async def update_task_title(
        task_id: int,
        task_update: TaskTitleUpdate,
        database: Annotated[DatabaseGateway, Depends()],
        user: User = Depends(fastapi_users.current_user(optional=True)),
) -> TaskResponse:
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    updated_task = await update_task_title_by_id(user.id, task_id, task_update, database)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@task_router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
        task_id: int,
        task_update: TaskUpdate,
        database: Annotated[DatabaseGateway, Depends()],
        user: User = Depends(fastapi_users.current_user(optional=True)),
) -> TaskResponse:
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    updated_task = await update_task_by_id(user.id, task_id, task_update, database)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@task_router.post("/reorder")
async def reorder_tasks(
        reorder_data: ReorderRequest,
        database: Annotated[DatabaseGateway, Depends()],
        user: User = Depends(fastapi_users.current_user(optional=True)),
) -> dict:
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        await tasks_reorder(user.id, reorder_data, database)
    except MissingTasksError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DataConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"message": "Tasks reordered successfully"}
