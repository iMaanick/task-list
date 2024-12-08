from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import StaleDataError

from app.adapters.sqlalchemy_db import models
from app.application.exceptions import TaskNotFoundError, MissingTasksError, DataConflictError
from app.application.models import TaskCreate, Task, TaskTitleUpdate, TaskUpdate, ReorderRequest
from app.application.protocols.database import DatabaseGateway, UserDataBaseGateway


class SqlaGateway(DatabaseGateway):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_task(self, task: TaskCreate) -> Task:
        new_task = models.Task(
            title=task.title,
            completed=task.completed,
            createdAt=datetime.utcnow()
        )
        self.session.add(new_task)
        await self.session.commit()
        await self.session.refresh(new_task)
        return Task.model_validate(new_task)

    async def get_tasks(self, skip: int, limit: int) -> list[Task]:
        query = select(models.Task).order_by(models.Task.position).offset(skip).limit(limit)
        result = await self.session.execute(query)
        tasks = [Task.model_validate(task) for task in result.scalars().all()]
        return tasks

    async def delete_task_by_id(self, task_id: int) -> Optional[int]:
        result = await self.session.execute(
            select(models.Task).where(models.Task.id == task_id))
        organization = result.scalars().first()
        if not organization:
            return None
        await self.session.delete(organization)
        await self.session.commit()
        return organization.id

    async def change_tasks_position(self) -> None:
        query = select(models.Task).order_by(models.Task.position)
        result = await self.session.execute(query)
        tasks = result.scalars().all()
        for index, task in enumerate(tasks):
            task.position = index
        await self.session.commit()

    async def update_task_title_by_id(self, task_id: int, task_update: TaskTitleUpdate) -> Optional[Task]:
        result = await self.session.execute(select(models.Task).where(models.Task.id == task_id))
        task = result.scalars().first()
        if not task:
            return None
        task.title = task_update.title
        await self.session.commit()
        return Task.model_validate(task)

    async def update_task_by_id(self, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
        result = await self.session.execute(select(models.Task).where(models.Task.id == task_id))
        task = result.scalars().first()
        if not task:
            return None
        task.completed = task_update.completed
        task.title = task_update.title
        await self.session.commit()
        return Task.model_validate(task)

    async def reorder_tasks(self, reorder_data: ReorderRequest) -> None:
        task_ids = [task.id for task in reorder_data.tasks]
        query = select(models.Task).where(models.Task.id.in_(task_ids))
        result = await self.session.execute(query)
        tasks = result.scalars().all()

        if len(tasks) != len(task_ids):
            found_task_ids = {task.id for task in tasks}
            missing_task_ids = set(task_ids) - found_task_ids
            raise MissingTasksError(missing_task_ids)

        for task_data in reorder_data.tasks:
            task = next((task for task in tasks if task.id == task_data.id), None)
            if not task:
                raise TaskNotFoundError(task_data.id)
            task.position = task_data.position
        try:
            await self.session.commit()
        except StaleDataError as e:
            await self.session.rollback()
            raise DataConflictError(f"Data conflict error: {str(e)}")


class UserSqlaGateway(UserDataBaseGateway):
    def __init__(self, session: AsyncSession):
        self.session = session
