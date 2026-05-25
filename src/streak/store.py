import json
from datetime import date
from pathlib import Path

from streak.errors import HabitError
from streak.models import Habit


class JsonHabitStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def _load(self) -> dict[str, Habit]:
        if not self.path.exists():
            return {}
        raw = json.loads(self.path.read_text())
        habits: dict[str, Habit] = {}
        for name, data in raw.get("habits", {}).items():
            dates = {date.fromisoformat(d) for d in data.get("completions", [])}
            habits[name] = Habit(name=name, completions=dates)
        return habits

    def _save(self, habits: dict[str, Habit]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "habits": {
                name: {"completions": sorted(d.isoformat() for d in h.completions)}
                for name, h in habits.items()
            }
        }
        self.path.write_text(json.dumps(payload, indent=2))

    def all_habits(self) -> dict[str, Habit]:
        return self._load()

    def get(self, name: str) -> Habit | None:
        return self._load().get(name)

    def save_habit(self, habit: Habit) -> None:
        habits = self._load()
        habits[habit.name] = habit
        self._save(habits)
