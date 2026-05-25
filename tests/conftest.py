from datetime import date
from pathlib import Path

import pytest

from streak.service import HabitService
from streak.store import JsonHabitStore


@pytest.fixture
def store_path(tmp_path: Path) -> Path:
    return tmp_path / "habits.json"


@pytest.fixture
def service(store_path: Path) -> HabitService:
    return HabitService(JsonHabitStore(store_path), today=date(2026, 5, 25))


@pytest.fixture
def frozen_today() -> date:
    return date(2026, 5, 25)
