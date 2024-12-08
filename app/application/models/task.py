from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    title: str
    completed: bool = False
    description: str = ""


class TaskUpdate(BaseModel):
    title: str
    completed: bool


class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool
    createdAt: datetime
    description: str

    model_config = ConfigDict(from_attributes=True)


class TaskTitleUpdate(BaseModel):
    title: str


class Task(BaseModel):
    id: int
    title: str
    completed: bool = False
    createdAt: datetime
    position: Optional[int] = None
    description: str

    model_config = ConfigDict(from_attributes=True)
