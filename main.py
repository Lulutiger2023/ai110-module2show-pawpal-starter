from pawpal_system import Owner, Pet, Task, Scheduler

# Set up an owner with two pets
jordan = Owner(name="Jordan", preferences={"prefers_morning_walks": True})

biscuit = Pet(name="Biscuit", species="dog")
mochi = Pet(name="Mochi", species="cat")

jordan.add_pet(biscuit)
jordan.add_pet(mochi)


def show_tasks(tasks):
    """Print a compact one-line summary for each task."""
    for t in tasks:
        who = t.pet.name if t.pet else "unassigned"
        time = t.preferred_time or "--:--"
        print(f"  - [{time}] {t.title} ({who}, priority {t.priority}, {t.duration_minutes} min)")


# --- Sorting demo ---
# Add tasks out of order: priorities and times deliberately mixed up.
print("--- Sorting demo ---")
mochi.add_task(Task(title="Play session", duration_minutes=20, priority=3, preferred_time="17:00"))
biscuit.add_task(Task(title="Feeding", duration_minutes=10, priority=1, preferred_time="08:30"))
mochi.add_task(Task(title="Litter box cleaning", duration_minutes=5, priority=2, preferred_time="09:00"))
biscuit.add_task(Task(title="Morning walk", duration_minutes=30, priority=1, preferred_time="08:00"))
biscuit.add_task(Task(title="Vitamins", duration_minutes=2, priority=1))  # no preferred_time -> sorts last in its group

scheduler = Scheduler(owner=jordan, available_minutes=120)
print("Sorted (priority first, then preferred_time, no-time last):")
show_tasks(scheduler.sort_tasks())


# --- Recurring task demo ---
# Add a daily recurring task, complete it, and watch the next occurrence appear.
print("\n--- Recurring task demo ---")
brush = Task(title="Daily brushing", duration_minutes=5, priority=2, is_recurring=True, recurrence="daily", preferred_time="19:00")
biscuit.add_task(brush)
print(f"Biscuit's tasks before completing '{brush.title}': {len(biscuit.tasks)}")
brush.mark_complete()
print(f"Biscuit's tasks after completing '{brush.title}': {len(biscuit.tasks)}")
print("Biscuit's task list (note the auto-created next occurrence):")
for t in biscuit.tasks:
    marker = "done" if t.completed else "open"
    print(f"  - {t.title} on {t.date} [{marker}]")


# --- Conflict demo ---
# Two tasks (different pets) scheduled for the same time -> conflict warning.
print("\n--- Conflict demo ---")
biscuit.add_task(Task(title="Bath time", duration_minutes=15, priority=2, preferred_time="10:00"))
mochi.add_task(Task(title="Vet call", duration_minutes=15, priority=2, preferred_time="10:00"))
scheduler = Scheduler(owner=jordan, available_minutes=120)
print(scheduler.explain_schedule())


# --- Filter demo ---
# Filter for a single pet's incomplete tasks.
print("\n--- Filter demo ---")
print("Biscuit's incomplete tasks:")
show_tasks(jordan.filter_tasks(pet_name="Biscuit", completed=False))
