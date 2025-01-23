from .db import SessionLocal
from .db.models import Item, ItemStatus, ItemType


class ItemService:
    def __init__(self):
        self.session = SessionLocal()

    def capture_item(self, title: str, description: str = ""):
        """
        Capture a new item in the database.
        """
        item = Item(
            title=title,
            description=description,
            status=ItemStatus.CAPTURED,
            type=ItemType.UNDEFINED,
        )
        self.session.add(item)
        self.session.commit()
