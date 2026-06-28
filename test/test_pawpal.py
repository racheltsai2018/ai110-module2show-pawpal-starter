"""Tests for core PawPal+ behaviors."""

import sys
from datetime import date, time, timedelta
from pathlib import Path

# Put the project root on sys.path so this test can import pawpal_system.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task from incomplete to complete."""
    task = Task("Walk", 30, "high", date.today())
    assert task.completed is False  # starts incomplete

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count by one."""
    pet = Pet("Biscuit", "Golden Retriever")
    assert len(pet.tasks) == 0  # starts with no tasks

    task = Task("Feeding", 10, "high", date.today())
    pet.add_task(task)

    assert len(pet.tasks) == 1


# --- Helpers -------------------------------------------------------------

def _scheduler_with(tasks, *, window=None):
    """Build an Owner + Scheduler around one pet holding `tasks`."""
    pet = Pet("Biscuit", "Golden Retriever")
    for task in tasks:
        pet.add_task(task)
    owner = Owner("Sam", available_time=window or {})
    owner.add_pet(pet)
    return Scheduler(owner)


# --- Sorting correctness -------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """sort_by_time() returns tasks ordered by their preferred time of day."""
    today = date.today()
    noon = Task("Lunch", 10, "low", today, preferred_time=time(12, 0))
    morning = Task("Walk", 30, "low", today, preferred_time=time(8, 0))
    evening = Task("Dinner", 10, "low", today, preferred_time=time(18, 0))
    sched = _scheduler_with([noon, morning, evening])

    ordered = sched.sort_by_time(today)

    assert [t.name for t in ordered] == ["Walk", "Lunch", "Dinner"]


def test_sort_tasks_orders_by_priority_then_duration():
    """sort_tasks() puts higher priority first, shorter task first within a tie."""
    today = date.today()
    low = Task("Brush", 5, "low", today)
    high_long = Task("Walk", 30, "high", today)
    high_short = Task("Meds", 5, "high", today)
    sched = _scheduler_with([low, high_long, high_short])

    ordered = sched.sort_tasks(today)

    assert [t.name for t in ordered] == ["Meds", "Walk", "Brush"]


def test_sort_with_no_tasks_returns_empty_list():
    """Sorting an owner with no due tasks yields an empty list, not an error."""
    sched = _scheduler_with([])

    assert sched.sort_by_time(date.today()) == []
    assert sched.sort_tasks(date.today()) == []


# --- Recurrence logic ----------------------------------------------------

def test_marking_daily_task_complete_creates_next_day_task():
    """Completing a daily task returns a fresh instance due the following day."""
    today = date.today()
    task = Task("Walk", 30, "high", today, recurrence="daily")

    nxt = task.mark_complete()

    assert task.completed is True
    assert nxt is not None
    assert nxt.due_date == today + timedelta(days=1)
    assert nxt.completed is False
    assert nxt.name == "Walk"


def test_marking_weekly_task_complete_advances_seven_days():
    """Completing a weekly task advances the due date by one week."""
    today = date.today()
    task = Task("Bath", 45, "medium", today, recurrence="weekly")

    nxt = task.mark_complete()

    assert nxt is not None
    assert nxt.due_date == today + timedelta(weeks=1)


def test_one_off_task_has_no_next_occurrence():
    """A non-recurring task produces no follow-up when completed."""
    task = Task("Vet visit", 60, "high", date.today())

    assert task.mark_complete() is None


def test_recurrence_keeps_pet_backlinks():
    """The next occurrence stays attached to the same pet(s)."""
    today = date.today()
    pet = Pet("Biscuit", "Golden Retriever")
    task = Task("Walk", 30, "high", today, recurrence="daily")
    pet.add_task(task)

    nxt = task.mark_complete()

    assert nxt in pet.tasks
    assert pet in nxt.pets


# --- Conflict detection --------------------------------------------------

def test_detect_conflicts_flags_identical_times():
    """Two tasks at the exact same preferred time are flagged as a conflict."""
    today = date.today()
    walk = Task("Walk", 30, "high", today, preferred_time=time(8, 0))
    feed = Task("Feed", 15, "high", today, preferred_time=time(8, 0))
    sched = _scheduler_with([walk, feed])

    conflicts = sched.detect_conflicts(today)

    assert len(conflicts) == 1
    start, tasks = conflicts[0]
    assert start == time(8, 0)
    assert {t.name for t in tasks} == {"Walk", "Feed"}


def test_detect_conflicts_flags_partial_overlap():
    """A task starting before another ends is flagged even with different starts."""
    today = date.today()
    walk = Task("Walk", 30, "high", today, preferred_time=time(8, 0))
    meds = Task("Meds", 10, "high", today, preferred_time=time(8, 15))
    sched = _scheduler_with([walk, meds])

    conflicts = sched.detect_conflicts(today)

    assert len(conflicts) == 1
    assert {t.name for t in conflicts[0][1]} == {"Walk", "Meds"}


def test_adjacent_tasks_do_not_conflict():
    """Back-to-back tasks (one ends exactly as the next starts) don't conflict."""
    today = date.today()
    walk = Task("Walk", 30, "high", today, preferred_time=time(8, 0))
    feed = Task("Feed", 15, "high", today, preferred_time=time(8, 30))
    sched = _scheduler_with([walk, feed])

    assert sched.detect_conflicts(today) == []


# --- Next available slot ----------------------------------------------------

def test_free_slots_reports_gap_after_a_task():
    """An 8:00 30-min walk leaves the window free again from 8:30 onward."""
    today = date.today()
    walk = Task("Walk", 30, "high", today, preferred_time=time(8, 0))
    sched = _scheduler_with([walk], window={"start": "08:00", "end": "09:00"})

    slots = sched.free_slots(today)

    assert slots == [(time(8, 30), time(9, 0))]


def test_find_next_available_slot_skips_busy_time():
    """A 15-min task can't start at 8:00 (busy) but fits right after at 8:30."""
    today = date.today()
    walk = Task("Walk", 30, "high", today, preferred_time=time(8, 0))
    sched = _scheduler_with([walk], window={"start": "08:00", "end": "09:00"})

    assert sched.find_next_available_slot(15, today) == time(8, 30)


def test_find_next_available_slot_returns_none_when_no_room():
    """If no gap is long enough, the finder reports None instead of guessing."""
    today = date.today()
    walk = Task("Walk", 50, "high", today, preferred_time=time(8, 0))
    sched = _scheduler_with([walk], window={"start": "08:00", "end": "09:00"})

    assert sched.find_next_available_slot(30, today) is None


def test_find_next_available_slot_respects_after():
    """`after` pushes the slot past an earlier-but-free time of day."""
    today = date.today()
    sched = _scheduler_with([], window={"start": "08:00", "end": "12:00"})

    assert sched.find_next_available_slot(30, today, after=time(10, 0)) == time(10, 0)


def test_conflict_warnings_are_human_readable():
    """conflict_warnings() returns a warning string for an overlap."""
    today = date.today()
    walk = Task("Walk", 30, "high", today, preferred_time=time(8, 0))
    feed = Task("Feed", 15, "high", today, preferred_time=time(8, 0))
    sched = _scheduler_with([walk, feed])

    warnings = sched.conflict_warnings(today)

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "WARNING" in warnings[0]
