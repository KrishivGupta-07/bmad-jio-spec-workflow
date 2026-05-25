import pytest

from streak.errors import HabitError


def test_FR_001_create_habit_persists(service):
    service.create_habit("Morning run")
    habit = service.store.get("Morning run")
    assert habit is not None
    assert habit.name == "Morning run"


def test_FR_001_create_habit_rejects_duplicate(service):
    service.create_habit("Morning run")
    with pytest.raises(HabitError, match="already exists"):
        service.create_habit("Morning run")


def test_FR_001_create_habit_rejects_empty_name(service):
    with pytest.raises(HabitError, match="cannot be empty"):
        service.create_habit("   ")
