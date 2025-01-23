import typer
from services import ItemService

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
