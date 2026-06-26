"""Tests for core PawPal+ behaviors."""

import sys
from datetime import date
from pathlib import Path

# Put the project root on sys.path so this test can import pawpal_system.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Pet, Task


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
