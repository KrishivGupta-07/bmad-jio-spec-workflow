from datetime import timedelta

import pytest

from streak.errors import HabitError
from streak.models import Habit


def test_FR_004_view_streak_three_consecutive_days(service):
    today = service.today
    habit = Habit(
        name="Run",
        completions={
            today - timedelta(days=2),
            today - timedelta(days=1),
            today,
        },
    )
    service.store.save_habit(habit)
    assert service.get_streak("Run") == 3


def test_FR_004_view_streak_resets_after_gap(service):
    today = service.today
    habit = Habit(
        name="Run",
        completions={
            today - timedelta(days=5),
            today - timedelta(days=4),
            today - timedelta(days=1),
            today,
        },
    )
    service.store.save_habit(habit)
    # Only the most recent consecutive run: yesterday + today = 2
    assert service.get_streak("Run") == 2


def test_FR_004_view_streak_unknown_habit(service):
    with pytest.raises(HabitError, match="not found"):
        service.get_streak("Unknown")
