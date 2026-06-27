from datetime import date

import streamlit as st
from pawpal_system import Pet, Task, Owner, Scheduler

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

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.tasks.append(
        Task(
            name=task_title,
            duration=int(duration),
            priority=priority,
            due_date=date.today(),
        )
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": t.name,
                "duration_minutes": t.duration,
                "priority": t.priority,
            }
            for t in st.session_state.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.info("Add at least one task before generating a schedule.")
    else:
        # Build the backend objects from the UI inputs.
        pet = Pet(name=pet_name, species=species)
        for task in st.session_state.tasks:
            pet.add_task(task)

        owner = Owner(name=owner_name)
        owner.add_pet(pet)

        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan(date.today())

        if not plan:
            st.warning("No tasks fit the available time window today.")
        else:
            st.success(f"Planned {len(plan)} task occurrence(s) for {pet.name}.")
            st.table(
                [
                    {
                        "time": slot.strftime("%H:%M"),
                        "task": task.name,
                        "duration_minutes": task.duration,
                        "priority": task.priority,
                    }
                    for slot, task in plan
                ]
            )

        conflicts = scheduler.detect_conflicts(date.today())
        if conflicts:
            st.warning("Scheduling conflicts detected:")
            for slot, tasks in conflicts:
                names = ", ".join(t.name for t in tasks)
                st.write(f"- {slot.strftime('%H:%M')}: {names}")
