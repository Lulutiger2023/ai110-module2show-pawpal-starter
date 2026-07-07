"""
PawPal+ system logic layer.

Core classes: Owner, Pet, Task, Scheduler.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional, Tuple


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: int  # 1 = highest, 3 = lowest
    is_recurring: bool = False
    recurrence: Optional[str] = None  # "daily" | "weekly" | None
    preferred_time: Optional[str] = None  # e.g. "08:00"
    date: Optional[date] = None  # day this occurrence is scheduled for
    pet: Optional["Pet"] = None
    completed: bool = False

    def __post_init__(self) -> None:
        """Default the scheduled date to today when not supplied."""
        if self.date is None:
            self.date = date.today()

    def next_occurrence(self) -> Optional["Task"]:
        """Build the next occurrence of a recurring task.

        Returns a fresh, uncompleted Task whose date is advanced by the
        recurrence interval (daily = +1 day, weekly = +7 days). Returns None
        for non-recurring tasks or unrecognized recurrence values. All other
        attributes (title, duration, priority, preferred_time, pet) carry over.
        """
        if not self.is_recurring:
            return None
        deltas = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}
        step = deltas.get(self.recurrence)
        if step is None:
            return None
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            is_recurring=self.is_recurring,
            recurrence=self.recurrence,
            preferred_time=self.preferred_time,
            date=self.date + step,
            pet=self.pet,
        )

    def mark_complete(self) -> None:
        """Mark this task as completed.

        For a recurring task, also create the next occurrence and append it to
        the same pet's task list so the care routine continues automatically.
        """
        self.completed = True
        following = self.next_occurrence()
        if following is not None and self.pet is not None:
            self.pet.tasks.append(following)


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

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Task]:
        """Return tasks matching the given filters.

        Each filter is optional; ``None`` means "don't filter on this".
        ``pet_name`` matches a task's owning pet by name; ``completed``
        matches the task's completion status.
        """
        tasks = self.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet is not None and t.pet.name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks


class Scheduler:
    def __init__(self, owner: Owner, available_minutes: int):
        """Build a scheduler for an owner's tasks within a daily time budget."""
        self.owner = owner
        self.available_minutes = available_minutes
        self.tasks: List[Task] = owner.get_all_tasks()

    @staticmethod
    def _time_key(task: Task) -> int:
        """Parse a task's preferred_time ("HH:MM") into minutes since midnight.

        Tasks with no preferred_time sort last within their priority group.
        """
        if not task.preferred_time:
            return 24 * 60  # sentinel: sorts after any real time-of-day
        hours, minutes = task.preferred_time.split(":")
        return int(hours) * 60 + int(minutes)

    def sort_tasks(self) -> List[Task]:
        """Sort by priority ascending, then preferred_time as a tiebreaker.

        Priority is primary (1 = highest). Within a priority group, tasks are
        ordered by preferred_time (earliest first); tasks without a
        preferred_time sort last. duration_minutes breaks any remaining ties.
        """
        return sorted(
            self.tasks,
            key=lambda t: (t.priority, self._time_key(t), t.duration_minutes),
        )

    def build_schedule(self) -> List[Task]:
        """Select and order tasks into a daily plan, respecting available_minutes.

        Completed tasks are skipped entirely — they don't compete for the day's
        time budget. Remaining tasks are considered best-first (highest priority,
        then shortest). Each task is included while it fits in the remaining time;
        tasks that would overflow the budget are dropped. Because of the ordering,
        the tasks left out are the lowest-priority / longest ones.
        """
        remaining = self.available_minutes
        schedule: List[Task] = []
        for task in self.sort_tasks():
            if task.completed:
                continue
            if task.duration_minutes <= remaining:
                schedule.append(task)
                remaining -= task.duration_minutes
        return schedule

    def find_conflicts(self) -> List[Tuple[Task, Task]]:
        """Return pairs of non-completed tasks that share a preferred_time.

        Conflicts are global: any two active tasks scheduled for the same
        clock time collide, regardless of which pet they belong to. Tasks with
        no preferred_time can't conflict and are ignored.
        """
        by_time: dict = {}
        for task in self.tasks:
            if task.completed or not task.preferred_time:
                continue
            by_time.setdefault(task.preferred_time, []).append(task)

        conflicts: List[Tuple[Task, Task]] = []
        for tasks in by_time.values():
            for i in range(len(tasks)):
                for j in range(i + 1, len(tasks)):
                    conflicts.append((tasks[i], tasks[j]))
        return conflicts

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

        excluded = [
            t
            for t in self.sort_tasks()
            if id(t) not in scheduled_set and not t.completed
        ]
        if excluded:
            lines.append("Excluded (ran out of time — lowest priority / longest first):")
            for task in excluded:
                lines.append(f"  - {label(task)}")

        completed = [t for t in self.sort_tasks() if t.completed]
        if completed:
            lines.append("Already completed:")
            for task in completed:
                lines.append(f"  - {label(task)}")

        conflicts = self.find_conflicts()
        if conflicts:
            lines.append("⚠️ Conflicts (tasks sharing the same time):")
            for a, b in conflicts:
                lines.append(f"  - {a.preferred_time}: {label(a)} vs {label(b)}")

        return "\n".join(lines)
