import sys
from pathlib import Path

import typer

from streak.errors import HabitError
from streak.service import HabitService
from streak.store import JsonHabitStore

app = typer.Typer(help="Track habits and daily streaks.")
DEFAULT_STORE = Path.home() / ".streak" / "habits.json"


def _service(store_path: Path | None = None) -> HabitService:
    path = store_path or DEFAULT_STORE
    return HabitService(JsonHabitStore(path))


@app.command("add")
def add_habit(
    name: str = typer.Argument(..., help="Habit name"),
    store: Path | None = typer.Option(None, "--store", help="Path to habits JSON"),
) -> None:
    try:
        _service(store).create_habit(name)
        typer.echo(f"Created habit: {name}")
    except HabitError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc


@app.command("done")
def done_habit(
    name: str = typer.Argument(..., help="Habit name"),
    store: Path | None = typer.Option(None, "--store", help="Path to habits JSON"),
) -> None:
    try:
        _service(store).log_completion(name)
        typer.echo(f"Logged completion for: {name}")
    except HabitError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc


@app.command("status")
def status_habit(
    name: str = typer.Argument(..., help="Habit name"),
    store: Path | None = typer.Option(None, "--store", help="Path to habits JSON"),
) -> None:
    try:
        streak = _service(store).get_streak(name)
        typer.echo(f"{name}: {streak}-day streak")
    except HabitError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc


@app.command("list")
def list_habits(
    store: Path | None = typer.Option(None, "--store", help="Path to habits JSON"),
) -> None:
    habits = _service(store).list_habits()
    if not habits:
        typer.echo("No habits yet. Use 'streak add NAME' to create one.")
        return
    for name, streak in habits:
        typer.echo(f"{name}: {streak}-day streak")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
