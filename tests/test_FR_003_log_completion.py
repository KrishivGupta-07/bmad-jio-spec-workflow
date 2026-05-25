import pytest

from streak.errors import HabitError


def test_FR_003_log_completion_records_today(service):
    service.create_habit("Morning run")
    service.log_completion("Morning run")
    habit = service.store.get("Morning run")
    assert service.today in habit.completions


def test_FR_003_log_completion_unknown_habit(service):
    with pytest.raises(HabitError, match="not found"):
        service.log_completion("Unknown")


def test_FR_003_log_completion_idempotent(service):
    service.create_habit("Morning run")
    service.log_completion("Morning run")
    service.log_completion("Morning run")
    habit = service.store.get("Morning run")
    assert len(habit.completions) == 1
