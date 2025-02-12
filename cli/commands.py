import typer
from rich.console import Console
from rich.table import Table

from .db.models import ItemType
from .helpers import interactively_collect, process_item
from .services import ItemService, ProjectService

app = typer.Typer()
item_service = ItemService()
project_service = ProjectService()
console = Console()


@app.command(name="collect")
def collect(
    title: str | None = typer.Argument(None, help="Title of the item"),
    description: str = typer.Option("", help="Description of the item"),
):
    """
    Collect a new item.
    If no title is provided, prompts the user interactively.
    """
    if title:
        item_service.capture_item(title, description)
        console.print(f'[✔] Collected: "{title}"', style="bold green")
    else:
        interactively_collect()


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
        "waiting": (ItemType.NEXT_ACTION, "Waiting For Others"),
        "reference": (ItemType.REFERENCE, "Reference materials"),
        "someday": (ItemType.SOMEDAY, "Someday/Maybe items"),
        "trash": (ItemType.TRASH, "Items to delete"),
        "projects": (None, "Active Projects"),
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

    if context.lower() == "projects":
        projects = project_service.get_active_projects()
        if not projects:
            typer.echo("No active projects found")
            return

        table = Table(title=description)
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Description", style="white")
        table.add_column("Next Actions", style="green")

        for project in projects:
            next_actions = [
                f"• {action['title']}" for action in project["next_actions"]
            ]
            table.add_row(
                str(project["id"]),
                project["title"],
                project["description"] or "",
                "\n".join(next_actions) if next_actions else "No actions",
            )

        console = Console()
        console.print(table)
        return
    only_delegated = context.lower() == "waiting"
    items = item_service.get_items_by_type(
        item_type, only_delegated=only_delegated
    )

    if not items:
        typer.echo(f"No items found in {description.lower()}")
        return

    table = Table(title=description)
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Description", style="white")
    if context.lower() == "waiting":
        table.add_column("Delegated To", style="white")
        table.add_column("Follow up date", style="white")
    if context.lower() in ["next", "waiting"]:
        table.add_column("Project", style="yellow")

    for item in items:
        row = [
            str(item["id"]),
            str(item["title"]),
            str(item["description"]) or "",
        ]
        if context.lower() == "waiting":
            row.append(str(item["delegated_to"]) or "")
            row.append(str(item["follow_up_date"]) or "")
        if context.lower() in ["next", "waiting"]:
            project_info = (
                f"#{item['project']['id']} {item['project']['title']}"
                if item["project"]
                else ""
            )
            row.append(project_info)
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
