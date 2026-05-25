from datetime import date

from streak.errors import HabitError
from streak.models import Habit
from streak.streak import compute_streak
from streak.store import JsonHabitStore


class HabitService:
    def __init__(self, store: JsonHabitStore, today: date | None = None) -> None:
        self.store = store
        self._today = today or date.today()

    @property
    def today(self) -> date:
        return self._today

    def create_habit(self, name: str) -> Habit:
        name = name.strip()
        if not name:
            raise HabitError("Habit name cannot be empty.")
        if self.store.get(name) is not None:
            raise HabitError(f"Habit '{name}' already exists.")
        habit = Habit(name=name)
        self.store.save_habit(habit)
        return habit

    def log_completion(self, name: str) -> None:
        habit = self.store.get(name)
        if habit is None:
            raise HabitError(f"Habit '{name}' not found.")
        habit.completions.add(self.today)
        self.store.save_habit(habit)

    def get_streak(self, name: str) -> int:
        habit = self.store.get(name)
        if habit is None:
            raise HabitError(f"Habit '{name}' not found.")
        return compute_streak(habit.completions, self.today)

    def list_habits(self) -> list[tuple[str, int]]:
        habits = self.store.all_habits()
        return [
            (name, compute_streak(h.completions, self.today))
            for name, h in sorted(habits.items())
        ]
