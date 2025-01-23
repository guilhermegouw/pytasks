import typer
from rich.console import Console
from rich.table import Table

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
    if context is None:
        typer.echo("Available contexts:")
        typer.echo("  - inbox: Show unclarified items")
        return

    if context.lower() != "inbox":
        typer.echo(f"Context '{context}' not implemented yet")
        raise typer.Exit(1)

    items = item_service.get_inbox_items()

    table = Table(title="Inbox Items")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Description", style="white")

    for item in items:
        table.add_row(
            str(item["id"]),
            str(item["title"]),
            str(item["description"]) or "",
        )

    console = Console()
    console.print(table)
