from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    title: str
    completed: bool = False


class TaskUpdate(BaseModel):
    title: str
    completed: bool


class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskTitleUpdate(BaseModel):
    title: str


class Task(BaseModel):
    id: int
    title: str
    completed: bool = False
    createdAt: datetime
    position: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

