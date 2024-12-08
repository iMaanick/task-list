from typing import Optional

from app.application.models import TaskCreate, Task, TaskTitleUpdate, TaskUpdate, ReorderRequest
from app.application.protocols.database import DatabaseGateway


async def add_task(
        task: TaskCreate,
        database: DatabaseGateway,
) -> Task:
    new_task = await database.add_task(task)
    return new_task


async def delete_task_from_list(
        task_id: int,
        database: DatabaseGateway,
) -> Optional[int]:
    deleted_task_id = await database.delete_task_by_id(task_id)
    if deleted_task_id is None:
        return None
    await database.change_tasks_position()
    return deleted_task_id


async def get_tasks(
        skip: int,
        limit: int,
        database: DatabaseGateway,
) -> list[Task]:
    tasks = await database.get_tasks(skip, limit)
    return tasks


async def update_task_title_by_id(
        task_id: int,
        task_update: TaskTitleUpdate,
        database: DatabaseGateway,
) -> Optional[Task]:
    updated_task = await database.update_task_title_by_id(task_id, task_update)
    if updated_task is None:
        return None
    return updated_task


async def update_task_by_id(
        task_id: int,
        task_update: TaskUpdate,
        database: DatabaseGateway,
) -> Optional[Task]:
    updated_task = await database.update_task_by_id(task_id, task_update)
    if updated_task is None:
        return None
    return updated_task


async def tasks_reorder(
        reorder_data: ReorderRequest,
        database: DatabaseGateway,
) -> None:
    await database.reorder_tasks(reorder_data)
