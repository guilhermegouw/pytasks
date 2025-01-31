import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import (DeclarativeMeta, Mapped, declarative_base,
                            mapped_column)
from sqlalchemy.sql import func

Base: DeclarativeMeta = declarative_base()


class ItemType(enum.Enum):
    NEXT_ACTION = "next_action"
    QUICK_TASK = "quick_task"
    REFERENCE = "reference"
    SOMEDAY = "someday"
    TRASH = "trash"
    UNDEFINED = "undefined"


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    item_type: Mapped[ItemType] = mapped_column(default=ItemType.UNDEFINED)
    is_done: Mapped[bool] = mapped_column(default=False)
    delegated_to: Mapped[Optional[str]] = mapped_column(nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("items.id"), nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<Item(id={self.id}, "
            f"title={self.title}, "
            f"item_type={self.item_type}, "
            f"is_done={self.is_done})>"
        )
