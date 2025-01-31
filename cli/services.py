from contextlib import contextmanager

from .db import SessionLocal
from .db.models import Item, ItemType


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
                item_type=ItemType.UNDEFINED,
            )
            session.add(item)

    def get_inbox_items(self):
        """
        Retrieves all unclarified items.
        Returns a list of Item objects with their attributes loaded.
        """
        return self.get_items_by_type(ItemType.UNDEFINED)

    def get_items_to_clarify(
        self, ids: list[int] | None = None, all: bool = False
    ) -> list[dict]:
        """
        Retrieves items to clarify based on criteria:
        - If ids provided: only those specific items
        - If all=True: all captured items
        - Otherwise: first available captured item

        Returns:
            List of dictionaries with id, title, description, and delegated_to
        """
        limit = None if (ids or all) else 1
        return self.get_items_by_type(ItemType.UNDEFINED, ids=ids, limit=limit)

    def get_items_by_type(
        self,
        item_type: ItemType,
        ids: list[int] | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Get items of a specific type with optional filtering"""
        with self.get_session() as session:
            query = session.query(Item).filter(Item.item_type == item_type)

            if ids:
                query = query.filter(Item.id.in_(ids))
            if limit:
                query = query.limit(limit)

            items = query.all()
            return [
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "delegated_to": item.delegated_to,
                }
                for item in items
            ]

    def update_item_type(self, item_id: int, new_type: ItemType) -> None:
        """Updates the type of an item"""
        with self.get_session() as session:
            item = session.query(Item).filter(Item.id == item_id).first()
            if item:
                item.item_type = new_type

    def update_item_delegation(self, item_id: int, delegated_to: str) -> None:
        """Updates who an item is delegated to"""
        with self.get_session() as session:
            item = session.query(Item).filter(Item.id == item_id).first()
            if item:
                item.delegated_to = delegated_to
