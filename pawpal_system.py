"""
PawPal+ system logic layer.

Core classes: Owner, Pet, Task, Scheduler.
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
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


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

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner, available_minutes: int):
        self.owner = owner
        self.available_minutes = available_minutes
        self.tasks: List[Task] = owner.get_all_tasks()

    def sort_tasks(self) -> List[Task]:
        """Sort tasks by priority ascending, then duration_minutes ascending."""
        return sorted(self.tasks, key=lambda t: (t.priority, t.duration_minutes))

    def build_schedule(self) -> List[Task]:
        """Select and order tasks into a daily plan, respecting available_minutes.

        Tasks are considered best-first (highest priority, then shortest). Each
        task is included while it fits in the remaining time; tasks that would
        overflow the budget are dropped. Because of the ordering, the tasks left
        out are the lowest-priority / longest ones.
        """
        remaining = self.available_minutes
        schedule: List[Task] = []
        for task in self.sort_tasks():
            if task.duration_minutes <= remaining:
                schedule.append(task)
                remaining -= task.duration_minutes
        return schedule

    def explain_schedule(self) -> str:
        """Return a human-readable explanation of why the plan looks the way it does."""
        scheduled = self.build_schedule()
        scheduled_set = {id(t) for t in scheduled}
        used = sum(t.duration_minutes for t in scheduled)

        def label(task: Task) -> str:
            who = task.pet.name if task.pet else "unassigned"
            return f"{task.title} ({who}, priority {task.priority}, {task.duration_minutes} min)"

        lines = [
            f"Daily plan for {self.owner.name} "
            f"({used}/{self.available_minutes} min used):",
        ]

        if scheduled:
            lines.append("Included:")
            for task in scheduled:
                lines.append(f"  - {label(task)}")
        else:
            lines.append("Included: none — no task fit in the available time.")

        excluded = [t for t in self.sort_tasks() if id(t) not in scheduled_set]
        if excluded:
            lines.append("Excluded (ran out of time — lowest priority / longest first):")
            for task in excluded:
                lines.append(f"  - {label(task)}")

        return "\n".join(lines)
