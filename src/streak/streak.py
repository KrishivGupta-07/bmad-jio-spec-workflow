from datetime import date, timedelta


def compute_streak(completion_dates: set[date], today: date | None = None) -> int:
    """Return consecutive-day streak ending on the most recent completion."""
    if not completion_dates:
        return 0

    anchor = max(completion_dates)
    streak = 0
    current = anchor
    while current in completion_dates:
        streak += 1
        current -= timedelta(days=1)
    return streak
