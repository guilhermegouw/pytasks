import enum

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.types import Enum

Base = declarative_base()


class ItemStatus(enum.Enum):
    CAPTURED = "captured"


class ItemType(enum.Enum):
    UNDEFINED = "undefined"


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime, nullable=True)
    status = Column(Enum(ItemStatus), default=ItemStatus.CAPTURED)
    type = Column(Enum(ItemType), default=ItemType.UNDEFINED)
    is_done = Column(Boolean, default=False)

    def __repr__(self):
        return (
            f"<Item(id={self.id}, "
            f"title={self.title}, "
            f"status={self.status}, "
            f"type={self.type}, "
            f"is_done={self.is_done})>"
        )
