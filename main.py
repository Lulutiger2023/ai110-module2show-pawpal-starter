from pawpal_system import Owner, Pet, Task, Scheduler

# Set up an owner with two pets
jordan = Owner(name="Jordan", preferences={"prefers_morning_walks": True})

biscuit = Pet(name="Biscuit", species="dog")
mochi = Pet(name="Mochi", species="cat")

jordan.add_pet(biscuit)
jordan.add_pet(mochi)

# Add at least three tasks with different times/priorities
biscuit.add_task(Task(title="Morning walk", duration_minutes=30, priority=1, preferred_time="08:00"))
biscuit.add_task(Task(title="Feeding", duration_minutes=10, priority=1, preferred_time="08:30"))
mochi.add_task(Task(title="Litter box cleaning", duration_minutes=5, priority=2, preferred_time="09:00"))
mochi.add_task(Task(title="Play session", duration_minutes=20, priority=3, preferred_time="17:00"))

# Build and print today's schedule
scheduler = Scheduler(owner=jordan, available_minutes=60)

print("=== Today's Schedule ===")
print(scheduler.explain_schedule())