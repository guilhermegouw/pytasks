from contextlib import contextmanager

from sqlalchemy.orm import joinedload

from .db import SessionLocal
from .db.models import Item, ItemStatus, ItemType


class ItemService:
    def __init__(self):
        self.session = SessionLocal()

    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.
        Handles commit/rollback and ensures proper session closure.
        """
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def capture_item(self, title: str, description: str = ""):
        """
        Capture a new item in the database (inbox).
        """

        with self.get_session() as session:
            item = Item(
                title=title,
                description=description,
                status=ItemStatus.CAPTURED,
                type=ItemType.UNDEFINED,
            )
            session.add(item)

    def get_inbox_items(self):
        """
        Retrieves all unclarified items (status=CAPTURED) from the database.
        Returns a list of Item objects with their attributes loaded.
        """
        with self.get_session() as session:
            items = (
                session.query(Item)
                .filter(Item.status == ItemStatus.CAPTURED)
                .all()
            )
            return [
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                }
                for item in items
            ]
