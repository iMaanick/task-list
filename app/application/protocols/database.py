from abc import ABC, abstractmethod
from typing import Optional

from app.application.models import TaskCreate, Task, TaskTitleUpdate, TaskUpdate, ReorderRequest


class UoW(ABC):
    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def flush(self) -> None:
        raise NotImplementedError


class DatabaseGateway(ABC):
    @abstractmethod
    async def add_task(self, user_id: int, task: TaskCreate) -> Task:
        raise NotImplementedError

    @abstractmethod
    async def delete_task_by_id(self, user_id: int, task_id: int) -> Optional[int]:
        raise NotImplementedError

    @abstractmethod
    async def change_tasks_position(self,  user_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_tasks(self, user_id: int, skip: int, limit: int) -> list[Task]:
        raise NotImplementedError

    @abstractmethod
    async def update_task_title_by_id(self, user_id: int, task_id: int, task_update: TaskTitleUpdate) -> Optional[Task]:
        raise NotImplementedError

    @abstractmethod
    async def update_task_by_id(self, user_id: int, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
        raise NotImplementedError

    @abstractmethod
    async def reorder_tasks(self, user_id: int, reorder_data: ReorderRequest) -> None:
        raise NotImplementedError


class UserDataBaseGateway(ABC):
    pass
