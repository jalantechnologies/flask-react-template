# src/apps/backend/modules/todo/models.py

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class TodoBase(BaseModel):
    title: str
    description: str
    type: Literal["Official", "Personal", "Hobby"]
    due_date: datetime


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[Literal["Personal", "Official", "Hobby"]] = None
    due_date: Optional[str] = None
    status: Optional[Literal["To Do", "Done"]] = None


class TodoResponse(TodoBase):
    id: str
    user_id: str
    status: Literal["To Do", "Done"]
    created_at: datetime

    class Config:
        orm_mode = True
