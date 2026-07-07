"""Tests for PawPal+ core behaviors."""

from pawpal_system import Pet, Task


def test_task_completion():
    """mark_complete() sets completed to True."""
    task = Task(title="Walk Rex", duration_minutes=30, priority=1)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_addition():
    """add_task() increases the pet's task count by 1."""
    pet = Pet(name="Rex", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Feed Rex", duration_minutes=10, priority=1))
    assert len(pet.tasks) == 1
