import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")
owner_name = st.text_input("Owner name", value="Jordan")

# Persist a single Owner across reruns; keep its name in sync with the input.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
owner = st.session_state.owner
owner.name = owner_name

# UI priority labels map to Task's int priority (1 = highest, 3 = lowest).
PRIORITY_TO_INT = {"high": 1, "medium": 2, "low": 3}
INT_TO_PRIORITY = {v: k for k, v in PRIORITY_TO_INT.items()}

st.markdown("### Pets")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    existing = [p.name for p in owner.pets]
    if not pet_name:
        st.warning("Enter a pet name first.")
    elif pet_name in existing:
        st.info(f"{pet_name} is already added.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species))
        st.success(f"Added {pet_name} ({species}).")

if owner.pets:
    st.caption("Pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above before creating tasks.")

st.markdown("### Tasks")
st.caption("Add a few tasks. These feed directly into your scheduler.")

pet_names = [p.name for p in owner.pets]

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

assign_to = st.selectbox("Assign to pet", pet_names) if pet_names else None

if st.button("Add task"):
    if not pet_names:
        st.warning("Add a pet first, then assign tasks to it.")
    else:
        pet = next(p for p in owner.pets if p.name == assign_to)
        pet.add_task(
            Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=PRIORITY_TO_INT[priority],
            )
        )
        st.success(f"Added '{task_title}' to {pet.name}.")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": t.pet.name if t.pet else "-",
                "title": t.title,
                "duration_minutes": t.duration_minutes,
                "priority": INT_TO_PRIORITY.get(t.priority, t.priority),
                "completed": t.completed,
            }
            for t in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Calls your scheduling logic and explains the resulting plan.")

available_minutes = st.number_input(
    "Available minutes for the day", min_value=1, max_value=1440, value=120
)

if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner, int(available_minutes))
        st.code(scheduler.explain_schedule())
