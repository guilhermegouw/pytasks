import typer
from rich.console import Console
from rich.table import Table

from .db.models import ItemType
from .helpers import process_item
from .services import ItemService

app = typer.Typer()
item_service = ItemService()


@app.command()
def capture(
    title: str | None = typer.Argument(None, help="Title of the item"),
    description: str | None = typer.Option(
        None, "--description", "-d", help="Description of the item"
    ),
):
    """
    Capture a new item.
    If no title is provided, prompts the user interactively.
    """
    if title is None:
        user_input = ""
        while not user_input.strip():
            user_input = typer.prompt("Enter the title (or 'q' to quit)")
            if user_input.lower() == "q":
                typer.echo("Capture cancelled.")
                raise typer.Exit()
            if not user_input.strip():
                typer.echo("Title is required. Press 'q' to quit")
        title = user_input
        description = typer.prompt(
            "Enter the description (optional)", default="", show_default=False
        )
    assert title is not None
    description = description or ""

    item_service.capture_item(title, description)
    typer.echo(f"Captured item: {title}")


@app.command()
def list(
    context: str | None = typer.Argument(
        None, help="Context to list items from (inbox, next, waiting-for, etc)"
    ),
):
    """List items from a specific context.
    If no context provided, shows available options."""
    contexts = {
        "inbox": (ItemType.UNDEFINED, "Unclarified items"),
        "quick": (ItemType.QUICK_TASK, "Quick tasks (2 minutes)"),
        "next": (ItemType.NEXT_ACTION, "Next actions"),
        "reference": (ItemType.REFERENCE, "Reference materials"),
        "someday": (ItemType.SOMEDAY, "Someday/Maybe items"),
        "trash": (ItemType.TRASH, "Items to delete"),
    }

    if context is None:
        typer.echo("Available contexts:")
        for key, (_, desc) in contexts.items():
            typer.echo(f"  - {key}: {desc}")
        return

    if context.lower() not in contexts:
        typer.echo(f"Invalid context: {context}")
        raise typer.Exit(1)

    item_type, description = contexts[context.lower()]
    items = item_service.get_items_by_type(item_type)

    if not items:
        typer.echo(f"No items found in {description.lower()}")
        return

    table = Table(title=description)
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Description", style="white")
    if item_type == ItemType.NEXT_ACTION:
        table.add_column("Delegated To", style="white")

    for item in items:
        row = [
            str(item["id"]),
            str(item["title"]),
            str(item["description"]) or "",
        ]
        if item_type == ItemType.NEXT_ACTION:
            row.append(str(item["delegated_to"]) or "")
        table.add_row(*row)

    console = Console()
    console.print(table)


@app.command()
def clarify(
    item_ids: str = typer.Argument(
        None, help="IDs of items to clarify (comma-separated)"
    ),
    all: bool = typer.Option(False, "--all", help="Process all inbox items"),
):
    """
    Process inbox items through GTD workflow.
    If no id provided, process the first available inbox item.
    """
    ids = None
    if item_ids:
        try:
            ids = [int(id.strip()) for id in item_ids.split(",")]
        except ValueError:
            typer.echo("Invalid ID format. Use comma-separated numbers")
            raise typer.Exit(1)

    items = item_service.get_items_to_clarify(ids, all)
    if not items:
        typer.echo("No items to clarify")
        return

    for item in items:
        process_item(item)
