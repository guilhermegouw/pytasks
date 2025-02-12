from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from .db import SessionLocal
from .db.models import Item, ItemType, Project


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
        only_delegated: bool = False,
    ) -> list[dict]:
        """Get items of a specific type with optional filtering"""
        with self.get_session() as session:
            query = session.query(Item).filter(Item.item_type == item_type)

            if only_delegated:
                query = query.filter(
                    Item.delegated_to.isnot(None),
                )
            if item_type == ItemType.NEXT_ACTION and not only_delegated:
                query = query.filter(
                    Item.delegated_to.is_(None),
                )
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
                    "follow_up_date": item.follow_up_date,
                    "project": (
                        {
                            "id": item.project.id,
                            "title": item.project.title,
                        }
                        if item.project
                        else None
                    ),
                }
                for item in items
            ]

    def update_item_type(self, item_id: int, new_type: ItemType) -> None:
        """Updates the type of an item"""
        with self.get_session() as session:
            item = session.query(Item).filter(Item.id == item_id).first()
            if item:
                item.item_type = new_type

    def update_item_delegation(
        self,
        item_id: int,
        delegated_to: str,
        follow_up_date: str | None = None,
    ) -> None:
        """Updates who an item is delegated to"""
        with self.get_session() as session:
            item = session.query(Item).filter(Item.id == item_id).first()
            if item:
                item.delegated_to = delegated_to
                if follow_up_date:
                    item.follow_up_date = datetime.strptime(
                        follow_up_date, "%Y-%m-%d"
                    )


class ProjectService:
    def __init__(self):
        self.session = SessionLocal()

    @contextmanager
    def get_session(self):
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_project(
        self, title: str, description: Optional[str] = None
    ) -> int:
        with self.get_session() as session:
            project = Project(
                title=title, description=description, is_active=True
            )
            session.add(project)
            session.commit()
            return project.id

    def add_next_action(
        self, project_id: int, title: str, description: Optional[str] = None
    ) -> None:
        with self.get_session() as session:
            item = Item(
                title=title,
                description=description,
                item_type=ItemType.NEXT_ACTION,
                project_id=project_id,
            )
            session.add(item)

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        with self.get_session() as session:
            return (
                session.query(Project).filter(Project.id == project_id).first()
            )

    def get_active_projects(self) -> list[dict]:
        with self.get_session() as session:
            projects = (
                session.query(Project).filter(Project.is_active == True).all()
            )
            projects_data = [
                {
                    "id": project.id,
                    "title": project.title,
                    "description": project.description,
                    "next_actions": [
                        {"id": action.id, "title": action.title}
                        for action in project.next_actions
                    ],
                }
                for project in projects
            ]
        return projects_data
