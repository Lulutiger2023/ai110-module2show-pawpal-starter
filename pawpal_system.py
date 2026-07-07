"""
PawPal+ system logic layer.

Core classes: Owner, Pet, Task, Scheduler.
This file currently contains structural stubs only — no scheduling logic yet.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low" | "medium" | "high"
    is_recurring: bool = False
    recurrence: Optional[str] = None  # "daily" | "weekly" | None
    preferred_time: Optional[str] = None  # e.g. "08:00"


@dataclass
class Pet:
    name: str
    species: str
    owner: Optional["Owner"] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        pass


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        pass


class Scheduler:
    def __init__(self, tasks: List[Task], available_minutes: int):
        self.tasks = tasks
        self.available_minutes = available_minutes

    def sort_tasks(self) -> List[Task]:
        """Sort tasks by priority and/or duration."""
        pass

    def build_schedule(self) -> List[Task]:
        """Select and order tasks into a daily plan, respecting available_minutes."""
        pass

    def explain_schedule(self) -> str:
        """Return a human-readable explanation of why the plan looks the way it does."""
        pass