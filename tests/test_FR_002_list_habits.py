from datetime import date, timedelta

from streak.models import Habit


def test_FR_002_list_habits_shows_streaks(service, store_path):
    today = service.today
    h1 = Habit(name="Run", completions={today})
    h2 = Habit(name="Read", completions={today - timedelta(days=1), today})
    service.store.save_habit(h1)
    service.store.save_habit(h2)

    listed = dict(service.list_habits())
    assert "Run" in listed
    assert "Read" in listed
    assert listed["Read"] == 2


def test_FR_002_list_habits_empty_store(service):
    assert service.list_habits() == []
