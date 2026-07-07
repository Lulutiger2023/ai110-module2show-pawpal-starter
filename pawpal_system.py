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
    priority: int  # 1 = highest, 3 = lowest
    is_recurring: bool = False
    recurrence: Optional[str] = None  # "daily" | "weekly" | None
    preferred_time: Optional[str] = None  # e.g. "08:00"
    pet: Optional["Pet"] = None


@dataclass
class Pet:
    name: str
    species: str
    owner: Optional["Owner"] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        task.pet = self
        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        pet.owner = self
        self.pets.append(pet)


class Scheduler:
    def __init__(self, owner: Owner, available_minutes: int):
        self.owner = owner
        self.available_minutes = available_minutes
        self.tasks: List[Task] = [
            task for pet in owner.pets for task in pet.tasks
        ]

    def sort_tasks(self) -> List[Task]:
        """Sort tasks by priority and/or duration."""
        pass

    def build_schedule(self) -> List[Task]:
        """Select and order tasks into a daily plan, respecting available_minutes."""
        pass

    def explain_schedule(self) -> str:
        """Return a human-readable explanation of why the plan looks the way it does."""
        pass