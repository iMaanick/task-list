from typing import Optional

from app.application.models import TaskCreate, Task, TaskTitleUpdate, TaskUpdate, ReorderRequest
from app.application.protocols.database import DatabaseGateway, UoW


async def add_task(
        user_id: int,
        task: TaskCreate,
        database: DatabaseGateway,
) -> Task:
    new_task = await database.add_task(user_id, task)
    return new_task


async def delete_task_from_list(
        user_id: int,
        task_id: int,
        database: DatabaseGateway,
) -> Optional[int]:
    deleted_task_id = await database.delete_task_by_id(user_id, task_id)
    if deleted_task_id is None:
        return None
    await database.change_tasks_position(user_id)
    return deleted_task_id


async def get_tasks(
        user_id: int,
        skip: int,
        limit: int,
        database: DatabaseGateway,
) -> list[Task]:
    tasks = await database.get_tasks(user_id, skip, limit)
    return tasks


async def update_task_title_by_id(
        user_id: int,
        task_id: int,
        task_update: TaskTitleUpdate,
        database: DatabaseGateway,
        uow: UoW,
) -> Optional[Task]:
    updated_task = await database.update_task_title_by_id(user_id, task_id, task_update)
    if updated_task is None:
        return None
    await uow.commit()
    return updated_task


async def update_task_by_id(
        user_id: int,
        task_id: int,
        task_update: TaskUpdate,
        database: DatabaseGateway,
        uow: UoW,
) -> Optional[Task]:
    updated_task = await database.update_task_by_id(user_id, task_id, task_update)
    if updated_task is None:
        return None
    await uow.commit()
    return updated_task


async def tasks_reorder(
        user_id: int,
        reorder_data: ReorderRequest,
        database: DatabaseGateway,
) -> None:
    await database.reorder_tasks(user_id, reorder_data)
