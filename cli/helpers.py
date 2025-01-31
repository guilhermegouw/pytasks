import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .db.models import ItemType
from .services import ItemService

console = Console()
item_service = ItemService()


def display_item(item: dict):
    """Display the current item being processed."""
    table = Table(show_header=False, box=None)
    table.add_row("Title:", item["title"])
    if item["description"]:
        table.add_row("Description:", item["description"])

    console.print(Panel(table, title="Current Item"))


def get_non_actionable_choice() -> str:
    """Present options for non-actionable items using arrow key selection."""
    choices = ["Delete it", "Save for reference", "Move to Someday/Maybe"]

    choice = questionary.select(
        "What would you like to do with this item?", choices=choices
    ).ask()

    return choice


def process_item(item: dict):
    """Interactive item processing following GTD workflow"""
    display_item(item)

    is_actionable = questionary.confirm(
        "Is it actionable?", default=False
    ).ask()

    if not is_actionable:
        handle_non_actionable(item)
        return

    handle_actionable(item)


def handle_non_actionable(item: dict):
    """Handle non-actionable items with questionary selection."""
    choices = ["Trash", "Save for reference", "Move to Someday/Maybe"]

    choice = questionary.select(
        "What would you like to do with this item?", choices=choices
    ).ask()

    type_mapping = {
        "Trash": ItemType.TRASH,
        "Save for reference": ItemType.REFERENCE,
        "Move to Someday/Maybe": ItemType.SOMEDAY,
    }

    item_service.update_item_type(item["id"], type_mapping[choice])
    console.print(f"\nItem marked as {type_mapping[choice].value}")


def handle_actionable(item: dict):
    """Handle actionable items with questionary selection."""
    choices = ["Quick Task (2 min)", "Delegate it", "Defer it"]

    choice = questionary.select(
        "What would you like to do with this item?", choices=choices
    ).ask()

    if choice == "Quick Task (2 min)":
        item_service.update_item_type(item["id"], ItemType.QUICK_TASK)
    elif choice == "Delegate it":
        delegated_to = questionary.text("Who to delegate to?").ask()
        item_service.update_item_type(item["id"], ItemType.NEXT_ACTION)
        item_service.update_item_delegation(item["id"], delegated_to)
    else:  # Defer it
        item_service.update_item_type(item["id"], ItemType.NEXT_ACTION)
