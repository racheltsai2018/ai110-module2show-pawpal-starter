from datetime import date, time, timedelta

import streamlit as st
from pawpal_system import Pet, Task, Owner, Scheduler, DEFAULT_WINDOW

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


# ---------------------------------------------------------------------------
# Presentation helpers: task-type emojis + color-coded priority badges.
# (Mirrors the CLI polish in main.py, adapted for Streamlit tables.)
# ---------------------------------------------------------------------------
def task_emoji(name: str) -> str:
    """Pick an emoji that hints at the kind of task from its name."""
    text = name.lower()
    if "walk" in text:
        return "🦮"
    if "feed" in text or "food" in text:
        return "🍽️"
    if "med" in text or "pill" in text:
        return "💊"
    if "play" in text:
        return "🎾"
    if "brush" in text or "groom" in text:
        return "🪮"
    if "vet" in text:
        return "🏥"
    return "🐾"


def priority_badge(priority: str) -> str:
    """Color-coded priority: 🔴 high, 🟡 medium, 🟢 low."""
    dot = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority.lower(), "⚪")
    return f"{dot} {priority.upper()}"


def status_badge(completed: bool) -> str:
    """Green check for done, hourglass for pending."""
    return "✅ done" if completed else "⏳ pending"


def task_label(t) -> str:
    """Task name prefixed with its type emoji."""
    return f"{task_emoji(t.name)} {t.name}"

st.title("🐾 PawPal+")

st.markdown(
    """
PawPal+ is a pet care planning assistant. Build an **owner** with **preferences**,
add one or more **pets**, attach **tasks**, then generate and explain a daily plan.
"""
)

# ---------------------------------------------------------------------------
# Session state: one Owner holds everything (pets, tasks, preferences).
# ---------------------------------------------------------------------------
DATA_FILE = "data.json"

if "owner" not in st.session_state:
    # Restore a saved owner if one exists, otherwise start with a default.
    owner = Owner.load_from_json(DATA_FILE)
    if owner is None:
        owner = Owner(name="Jordan")
        owner.add_pet(Pet(name="Mochi", species="dog"))
    st.session_state.owner = owner

owner: Owner = st.session_state.owner


def pet_options() -> list[str]:
    return [p.name for p in owner.pets]


def find_pet(name: str) -> Pet | None:
    return next((p for p in owner.pets if p.name == name), None)


st.divider()

# ---------------------------------------------------------------------------
# Owner: basic info + preferences (care window)
# ---------------------------------------------------------------------------
st.subheader("👤 Owner & preferences")

owner.name = st.text_input("Owner name", value=owner.name)

win = owner.available_time or DEFAULT_WINDOW
c1, c2 = st.columns(2)
with c1:
    win_start = st.time_input("Care window start", value=time.fromisoformat(win["start"]))
with c2:
    win_end = st.time_input("Care window end", value=time.fromisoformat(win["end"]))

owner.available_time = {
    "start": win_start.strftime("%H:%M"),
    "end": win_end.strftime("%H:%M"),
}
# Persist owner name + care-window edits as they're made.
owner.save_to_json(DATA_FILE)
st.caption(
    f"Available care time today: **{Scheduler(owner)._window_minutes(date.today())} min**."
)

st.divider()

# ---------------------------------------------------------------------------
# Pets: add multiple
# ---------------------------------------------------------------------------
st.subheader("🐶 Pets")

pc1, pc2, pc3 = st.columns([3, 2, 2])
with pc1:
    new_pet_name = st.text_input("New pet name", value="")
with pc2:
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
with pc3:
    st.write("")
    st.write("")
    if st.button("Add pet"):
        if not new_pet_name.strip():
            st.warning("Give the pet a name first.")
        elif find_pet(new_pet_name):
            st.warning(f"A pet named “{new_pet_name}” already exists.")
        else:
            owner.add_pet(Pet(name=new_pet_name.strip(), species=new_pet_species))
            owner.save_to_json(DATA_FILE)
            st.success(f"Added {new_pet_name}.")
            st.rerun()

if owner.pets:
    for pet in list(owner.pets):
        cols = st.columns([6, 1])
        cols[0].write(str(pet))
        if cols[1].button("Remove", key=f"rmpet_{id(pet)}"):
            owner.remove_pet(pet)
            owner.save_to_json(DATA_FILE)
            st.rerun()
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Tasks: add, optionally shared across pets, with recurrence + due date
# ---------------------------------------------------------------------------
st.subheader("📝 Tasks")

if not owner.pets:
    st.info("Add a pet before creating tasks.")
else:
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        task_title = st.text_input("Task title", value="Morning walk")
    with tc2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with tc3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    tc4, tc5, tc6 = st.columns(3)
    with tc4:
        frequency = st.number_input("Times per day", min_value=1, max_value=12, value=1)
    with tc5:
        use_preferred = st.checkbox("Set a preferred time")
    with tc6:
        preferred_time = st.time_input(
            "Preferred time", value=time(8, 0), disabled=not use_preferred
        )

    tc7, tc8, tc9 = st.columns(3)
    with tc7:
        recurrence = st.selectbox("Recurrence", ["one-off", "daily", "weekly"])
    with tc8:
        due_offset = st.number_input("Due in N days", min_value=0, max_value=30, value=0)
    with tc9:
        assigned_pets = st.multiselect(
            "For pets (shared = multiple)",
            options=pet_options(),
            default=pet_options()[:1],
        )

    if st.button("Add task"):
        if not assigned_pets:
            st.warning("Pick at least one pet.")
        else:
            task = Task(
                name=task_title,
                duration=int(duration),
                priority=priority,
                due_date=date.today() + timedelta(days=int(due_offset)),
                frequency=int(frequency),
                preferred_time=preferred_time if use_preferred else None,
                recurrence=None if recurrence == "one-off" else recurrence,
            )
            # Adding the SAME Task object to each pet makes it a shared task.
            for name in assigned_pets:
                find_pet(name).add_task(task)
            owner.save_to_json(DATA_FILE)
            st.success(f"Added “{task_title}” for {', '.join(assigned_pets)}.")
            st.rerun()

    # Current tasks with completion controls
    all_tasks = owner.all_tasks()
    if all_tasks:
        st.write("Current tasks:")
        for t in all_tasks:
            cols = st.columns([7, 2, 2])
            times = f" ×{t.frequency}/day" if t.frequency > 1 else ""
            who = ", ".join(p.name for p in t.pets)
            cols[0].write(
                f"{status_badge(t.completed)} {task_label(t)} "
                f"({t.duration} min{times}) — {priority_badge(t.priority)} · {who}"
            )
            cols[1].caption(t.due_date.strftime("%Y-%m-%d"))
            if not t.completed:
                if cols[2].button("Mark done", key=f"done_{id(t)}"):
                    nxt = t.mark_complete()
                    owner.save_to_json(DATA_FILE)
                    if nxt is not None:
                        st.toast(f"Recurring task rescheduled for {nxt.due_date}.")
                    st.rerun()
            else:
                cols[2].caption("✓ done")
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------
st.subheader("🗓️ Build schedule")

plan_for = st.date_input("Plan for date", value=date.today())

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    day = plan_for

    due = owner.tasks_due_today(day)
    if not due:
        st.info("No pending tasks are due on the selected date.")
    else:
        # --- Priority-sorted view ---
        st.markdown("#### 📋 Tasks by priority")
        ordered = scheduler.sort_tasks(day)
        st.table(
            [
                {
                    "rank": i,
                    "task": task_label(t),
                    "priority": priority_badge(t.priority),
                    "status": status_badge(t.completed),
                    "duration_minutes": t.duration,
                    "total_minutes": t.total_daily_minutes(),
                    "pets": ", ".join(p.name for p in t.pets),
                }
                for i, t in enumerate(ordered, start=1)
            ]
        )

        # --- Time-of-day ordering ---
        st.markdown("#### ⏰ Tasks by preferred time")
        st.table(
            [
                {
                    "task": task_label(t),
                    "preferred_time": t.preferred_time.strftime("%H:%M")
                    if t.preferred_time
                    else "flexible",
                    "priority": priority_badge(t.priority),
                }
                for t in scheduler.sort_by_time(day)
            ]
        )

        # --- Time-budget filtering ---
        kept = scheduler.filter_tasks(day)
        budget = scheduler._window_minutes(day)
        dropped = [t for t in ordered if t not in kept]
        st.caption(
            f"Time budget: **{budget} min**. Kept {len(kept)} of {len(ordered)} task(s)."
        )
        if dropped:
            st.warning(
                "Didn't fit the time budget: " + ", ".join(t.name for t in dropped)
            )

        # --- Final plan ---
        st.markdown("#### 🗓️ Daily plan")
        plan = scheduler.generate_plan(day)
        if not plan:
            st.warning("No tasks fit the available time window.")
        else:
            st.success(f"Planned {len(plan)} task occurrence(s).")
            st.table(
                [
                    {
                        "time": slot.strftime("%H:%M"),
                        "task": task_label(task),
                        "duration_minutes": task.duration,
                        "priority": priority_badge(task.priority),
                        "pets": ", ".join(p.name for p in task.pets),
                    }
                    for slot, task in plan
                ]
            )

        # --- Next available slot ---
        st.markdown("#### 🕳️ Open time")
        free = scheduler.free_slots(day, min_minutes=1)
        if free:
            st.caption(
                "Free gaps today: "
                + ", ".join(f"{s:%H:%M}–{e:%H:%M}" for s, e in free)
            )
        else:
            st.caption("No open gaps in the care window today.")
        fc1, fc2 = st.columns([2, 3])
        with fc1:
            fit_minutes = st.number_input(
                "Fit a new task of (min)", min_value=1, max_value=240, value=15
            )
        with fc2:
            st.write("")
            st.write("")
            slot = scheduler.find_next_available_slot(int(fit_minutes), day)
            if slot is not None:
                st.success(f"Next available slot: **{slot:%H:%M}**")
            else:
                st.warning("No open slot long enough today.")

        # --- Conflicts ---
        st.markdown("#### ⚠️ Conflicts")
        warnings = scheduler.conflict_warnings(day)
        if warnings:
            for message in warnings:
                st.warning(message)
        else:
            st.success("No scheduling conflicts detected.")
