from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import mapped_column

from app.adapters.sqlalchemy_db.models import Base


class Task(Base):
    __tablename__ = 'tasks'

    id = mapped_column(Integer, primary_key=True, index=True)
    title = mapped_column(String, index=True)
    completed = mapped_column(Boolean, default=False)
    createdAt = mapped_column(DateTime, default=datetime.utcnow)
    position = mapped_column(Integer)
