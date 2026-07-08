"""Tests for PawPal+ core behaviors."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


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


# ---------------------------------------------------------------------------
# Behavior #1: Task sorting order (Scheduler.sort_tasks)
# Sort key is (priority, preferred_time, duration_minutes).
# ---------------------------------------------------------------------------

def test_sort_priority_is_primary():
    """Priority 1 tasks come before priority 3, regardless of time."""
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    low = Task(title="low", duration_minutes=10, priority=3, preferred_time="06:00")
    high = Task(title="high", duration_minutes=10, priority=1, preferred_time="23:00")
    pet.add_task(low)
    pet.add_task(high)

    order = [t.title for t in Scheduler(owner, 100).sort_tasks()]

    assert order == ["high", "low"]


def test_sort_time_breaks_priority_tie():
    """Within a priority group, the earlier preferred_time comes first."""
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    late = Task(title="late", duration_minutes=10, priority=1, preferred_time="18:00")
    early = Task(title="early", duration_minutes=10, priority=1, preferred_time="08:00")
    pet.add_task(late)
    pet.add_task(early)

    order = [t.title for t in Scheduler(owner, 100).sort_tasks()]

    assert order == ["early", "late"]


def test_sort_missing_time_sorts_last_in_priority_group():
    """A task with no preferred_time sorts after timed tasks of equal priority."""
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    no_time = Task(title="anytime", duration_minutes=10, priority=1)
    timed = Task(title="timed", duration_minutes=10, priority=1, preferred_time="12:00")
    pet.add_task(no_time)
    pet.add_task(timed)

    order = [t.title for t in Scheduler(owner, 100).sort_tasks()]

    assert order == ["timed", "anytime"]


def test_sort_duration_is_final_tiebreaker():
    """Same priority and same time: the shorter task wins."""
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    longer = Task(title="longer", duration_minutes=30, priority=1, preferred_time="09:00")
    shorter = Task(title="shorter", duration_minutes=10, priority=1, preferred_time="09:00")
    pet.add_task(longer)
    pet.add_task(shorter)

    order = [t.title for t in Scheduler(owner, 100).sort_tasks()]

    assert order == ["shorter", "longer"]


# ---------------------------------------------------------------------------
# Behavior #2: Budget-constrained scheduling (Scheduler.build_schedule)
# NOTE: the Scheduler snapshots owner.get_all_tasks() at construction, so
# every test here builds the Scheduler only AFTER all task setup is done.
# ---------------------------------------------------------------------------

def test_build_schedule_all_fit():
    """When everything fits, all tasks are included in sorted order."""
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(title="a", duration_minutes=20, priority=1, preferred_time="08:00"))
    pet.add_task(Task(title="b", duration_minutes=15, priority=2, preferred_time="09:00"))

    scheduler = Scheduler(owner, 100)
    titles = [t.title for t in scheduler.build_schedule()]

    assert titles == ["a", "b"]


def test_build_schedule_exact_fit_boundary():
    """A task whose duration exactly equals the remaining budget is included (<=)."""
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(title="exact", duration_minutes=30, priority=1))

    scheduler = Scheduler(owner, 30)
    titles = [t.title for t in scheduler.build_schedule()]

    assert titles == ["exact"]


def test_build_schedule_skips_overflow_but_keeps_later_smaller_task():
    """A too-big task is dropped, but a later smaller task still gets picked up."""
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    # Same priority/time so ordering is by duration: big (60) sorts before small (10).
    pet.add_task(Task(title="big", duration_minutes=60, priority=1, preferred_time="08:00"))
    pet.add_task(Task(title="small", duration_minutes=10, priority=1, preferred_time="08:00"))

    scheduler = Scheduler(owner, 30)
    titles = [t.title for t in scheduler.build_schedule()]

    assert titles == ["small"]


def test_build_schedule_completed_task_frees_budget():
    """Completed tasks are skipped and do not consume the time budget."""
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    done = Task(title="done", duration_minutes=25, priority=1, preferred_time="08:00")
    active = Task(title="active", duration_minutes=20, priority=2, preferred_time="09:00")
    pet.add_task(done)
    pet.add_task(active)
    done.mark_complete()  # mutate before constructing the Scheduler

    scheduler = Scheduler(owner, 30)
    titles = [t.title for t in scheduler.build_schedule()]

    # If 'done' had competed for budget, only 25 min would remain and 'active'
    # (20 min) would still fit — but this asserts 'done' is absent entirely.
    assert titles == ["active"]


def test_build_schedule_empty_and_zero_budget():
    """No tasks, or a zero budget, yields an empty schedule without error."""
    empty_owner = Owner(name="Sam")
    empty_owner.add_pet(Pet(name="Rex", species="dog"))
    assert Scheduler(empty_owner, 100).build_schedule() == []

    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(title="a", duration_minutes=10, priority=1))
    assert Scheduler(owner, 0).build_schedule() == []


# ---------------------------------------------------------------------------
# Behavior #3: Recurring vs. non-recurring completion
# (Task.mark_complete + Task.next_occurrence)
# ---------------------------------------------------------------------------

def test_recurring_completion_appends_advanced_occurrence():
    """Completing a daily recurring task appends a fresh occurrence at date+1."""
    pet = Pet(name="Rex", species="dog")
    today = date(2026, 7, 7)
    task = Task(
        title="Walk Rex",
        duration_minutes=30,
        priority=1,
        is_recurring=True,
        recurrence="daily",
        preferred_time="08:00",
        date=today,
    )
    pet.add_task(task)

    task.mark_complete()

    assert task.completed is True
    assert len(pet.tasks) == 2
    nxt = pet.tasks[-1]
    assert nxt.completed is False
    assert nxt.date == today + timedelta(days=1)
    assert nxt.title == "Walk Rex"
    assert nxt.preferred_time == "08:00"
    assert nxt.pet is pet


def test_weekly_recurrence_advances_seven_days():
    """A weekly recurring task's next occurrence lands +7 days out."""
    today = date(2026, 7, 7)
    task = Task(
        title="Vet nails",
        duration_minutes=45,
        priority=2,
        is_recurring=True,
        recurrence="weekly",
        date=today,
    )

    nxt = task.next_occurrence()

    assert nxt is not None
    assert nxt.date == today + timedelta(weeks=1)


def test_non_recurring_completion_appends_nothing():
    """A non-recurring task, when completed, adds no follow-up occurrence."""
    pet = Pet(name="Rex", species="dog")
    task = Task(title="One-off bath", duration_minutes=40, priority=2)
    pet.add_task(task)

    task.mark_complete()

    assert task.completed is True
    assert len(pet.tasks) == 1


def test_unrecognized_recurrence_yields_no_occurrence():
    """is_recurring with an unknown recurrence value produces no next occurrence."""
    pet = Pet(name="Rex", species="dog")
    task = Task(
        title="Monthly groom",
        duration_minutes=60,
        priority=3,
        is_recurring=True,
        recurrence="monthly",  # not "daily" / "weekly"
    )
    pet.add_task(task)

    assert task.next_occurrence() is None

    task.mark_complete()
    assert task.completed is True
    assert len(pet.tasks) == 1


def test_recurring_without_pet_does_not_crash():
    """Completing a recurring task with no pet marks it done and orphans nothing."""
    task = Task(
        title="Ownerless walk",
        duration_minutes=30,
        priority=1,
        is_recurring=True,
        recurrence="daily",
    )

    task.mark_complete()  # self.pet is None -> guarded, no append target

    assert task.completed is True


# ---------------------------------------------------------------------------
# Behavior #4: Time conflict detection (Scheduler.find_conflicts)
# ---------------------------------------------------------------------------

def test_conflict_across_pets_same_time():
    """Two active tasks at the exact same time conflict, even across pets."""
    owner = Owner(name="Sam")
    dog = Pet(name="Rex", species="dog")
    cat = Pet(name="Milo", species="cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task(title="Walk Rex", duration_minutes=30, priority=1, preferred_time="08:00"))
    cat.add_task(Task(title="Feed Milo", duration_minutes=10, priority=1, preferred_time="08:00"))

    conflicts = Scheduler(owner, 100).find_conflicts()

    assert len(conflicts) == 1
    titles = {conflicts[0][0].title, conflicts[0][1].title}
    assert titles == {"Walk Rex", "Feed Milo"}


def test_three_tasks_same_time_yield_three_pairs():
    """Three tasks at the same time produce C(3,2) = 3 conflict pairs."""
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    for i in range(3):
        pet.add_task(Task(title=f"t{i}", duration_minutes=10, priority=1, preferred_time="08:00"))

    conflicts = Scheduler(owner, 100).find_conflicts()

    assert len(conflicts) == 3


def test_missing_time_never_conflicts():
    """Tasks without a preferred_time are ignored by conflict detection."""
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(title="a", duration_minutes=10, priority=1))
    pet.add_task(Task(title="b", duration_minutes=10, priority=1))

    assert Scheduler(owner, 100).find_conflicts() == []


def test_completed_task_does_not_conflict():
    """A completed task sharing a time with an active one is not a conflict."""
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    done = Task(title="done", duration_minutes=10, priority=1, preferred_time="08:00")
    active = Task(title="active", duration_minutes=10, priority=1, preferred_time="08:00")
    pet.add_task(done)
    pet.add_task(active)
    done.mark_complete()

    assert Scheduler(owner, 100).find_conflicts() == []


# ---------------------------------------------------------------------------
# Behavior #5: Empty / boundary collections (Owner + Scheduler on no data)
# ---------------------------------------------------------------------------

def test_pet_with_no_tasks_and_owner_with_no_pets():
    """Empty structures produce empty results everywhere, without error."""
    no_pets = Owner(name="Sam")
    assert no_pets.get_all_tasks() == []
    assert no_pets.filter_tasks() == []
    scheduler = Scheduler(no_pets, 100)
    assert scheduler.build_schedule() == []
    assert scheduler.find_conflicts() == []
    # explain_schedule should render the "none" branch without raising.
    assert "none" in scheduler.explain_schedule()

    pet_no_tasks = Owner(name="Ann")
    pet_no_tasks.add_pet(Pet(name="Rex", species="dog"))
    assert pet_no_tasks.get_all_tasks() == []
    assert pet_no_tasks.filter_tasks() == []


def test_filter_tasks_none_filters_returns_everything():
    """filter_tasks() with both filters None returns all tasks."""
    owner = Owner(name="Sam")
    pet = Pet(name="Rex", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(title="a", duration_minutes=10, priority=1))
    pet.add_task(Task(title="b", duration_minutes=10, priority=2))

    assert len(owner.filter_tasks()) == 2
