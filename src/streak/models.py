from dataclasses import dataclass, field
from datetime import date


@dataclass
class Habit:
    name: str
    completions: set[date] = field(default_factory=set)
