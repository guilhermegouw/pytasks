import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .db.models import ItemType
from .services import ItemService, ProjectService

console = Console()
item_service = ItemService()
project_service = ProjectService()


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
    is_quick = questionary.confirm(
        "Will it take less than 2 minutes?", default=False
    ).ask()
    if is_quick:
        item_service.update_item_type(item["id"], ItemType.QUICK_TASK)
        return

    will_delegate = questionary.confirm(
        "Do you want to delegate it?", default=False
    ).ask()
    if will_delegate:
        delegated_to = questionary.text("Who should do this?").ask()
        follow_up_date = (
            questionary.text(
                "When should you follow up? (YYYY-MM-DD or press enter to skip)"
            ).ask()
            if delegated_to
            else None
        )

        item_service.update_item_type(item["id"], ItemType.NEXT_ACTION)
        item_service.update_item_delegation(
            item["id"], delegated_to, follow_up_date
        )
        return
    needs_multiple_actions = questionary.confirm(
        "Will this require multiple actions?", default=False
    ).ask()
    if needs_multiple_actions:
        project_id = project_service.create_project(
            item["title"], item["description"]
        )
        want_to_add_action = questionary.confirm(
            "Would you like to add a next action now?", default=False
        ).ask()
        if want_to_add_action:
            next_action_title = questionary.text(
                "What's the first next action for this project?"
            ).ask()
            next_action_description = questionary.text(
                "Any etails for this action? (optional)"
            ).ask()

            project_service.add_next_action(
                project_id,
                next_action_title,
                next_action_description if next_action_description else None,
            )
        item_service.update_item_type(item["id"], ItemType.TRASH)
        return
    item_service.update_item_type(item["id"], ItemType.NEXT_ACTION)
