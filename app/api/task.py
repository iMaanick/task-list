from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.application.exceptions import MissingTasksError, DataConflictError, TaskNotFoundError
from app.application.models import TaskCreate, TaskResponse, TaskTitleUpdate, TaskUpdate, ReorderRequest
from app.application.protocols.database import DatabaseGateway
from app.application.task import add_task, delete_task_from_list, get_tasks, update_task_title_by_id, update_task_by_id, \
    tasks_reorder

task_router = APIRouter()


@task_router.post("/", response_model=TaskResponse)
async def create_task(
        database: Annotated[DatabaseGateway, Depends()],
        task: TaskCreate,
) -> TaskResponse:
    new_task = await add_task(task, database)
    return new_task


@task_router.delete("/{task_id}")
async def delete_task(
        database: Annotated[DatabaseGateway, Depends()],
        task_id: int,
) -> dict:
    deleted_task_id = await delete_task_from_list(task_id, database)
    if deleted_task_id is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}


@task_router.get("/", response_model=list[TaskResponse])
async def read_tasks(
        database: Annotated[DatabaseGateway, Depends()],
        skip: int = 0,
        limit: int = 10,
) -> list[TaskResponse]:
    tasks = await get_tasks(skip, limit, database)
    return tasks


@task_router.patch("/{task_id}/title", response_model=TaskResponse)
async def update_task_title(
        task_id: int,
        task_update: TaskTitleUpdate,
        database: Annotated[DatabaseGateway, Depends()],
) -> TaskResponse:
    updated_task = await update_task_title_by_id(task_id, task_update, database)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@task_router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
        task_id: int,
        task_update: TaskUpdate,
        database: Annotated[DatabaseGateway, Depends()],
) -> TaskResponse:
    updated_task = await update_task_by_id(task_id, task_update, database)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@task_router.post("/reorder")
async def reorder_tasks(
        reorder_data: ReorderRequest,
        database: Annotated[DatabaseGateway, Depends()],
) -> dict:
    try:
        await tasks_reorder(reorder_data, database)
    except MissingTasksError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DataConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"message": "Tasks reordered successfully"}
