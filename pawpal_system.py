"""PawPal+ system class skeletons.

Generated from diagrams/uml.mmd. Method bodies are stubs (no logic yet).
"""

import json
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta


@dataclass
class Pet:
    """A pet's identifying info plus the care tasks attached to it.

    A task can be shared with other pets (e.g. a group walk). Sharing works by
    adding the *same* Task object to each pet, so the Owner can de-duplicate it
    when gathering tasks across all pets.
    """

    name: str
    species: str
    tasks: list["Task"] = field(default_factory=list)

    def add_task(self, task: "Task") -> None:
        """Attach a task to this pet, keeping the Task.pets back-link in sync."""
        if task not in self.tasks:
            self.tasks.append(task)
        if self not in task.pets:
            task.pets.append(self)

    def remove_task(self, task: "Task") -> None:
        """Detach a task from this pet (no-op if it isn't attached)."""
        if task in self.tasks:
            self.tasks.remove(task)
        if self in task.pets:
            task.pets.remove(self)

    def list_tasks(self) -> list["Task"]:
        """Return a copy of this pet's tasks."""
        return list(self.tasks)

    def __str__(self) -> str:
        """Readable summary: name, species, and task count."""
        return f"{self.name} ({self.species}) — {len(self.tasks)} task(s)"


@dataclass
class Owner:
    """A pet owner: identifying info, a list of pets, and access to all tasks.

    Tasks live on each Pet, not here. The owner aggregates them across pets and
    de-duplicates, so one activity shared by several pets counts only once.
    """

    name: str
    pets: list[Pet] = field(default_factory=list)
    available_time: dict = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Unregister a pet (no-op if it isn't registered)."""
        if pet in self.pets:
            self.pets.remove(pet)

    def all_tasks(self) -> list["Task"]:
        """Return every task across all pets in order, de-duplicating shared tasks by identity."""
        by_id = {id(task): task for pet in self.pets for task in pet.tasks}
        return list(by_id.values())

    def tasks_for(self, pet: Pet) -> list["Task"]:
        """All tasks that involve the given pet."""
        return pet.list_tasks()

    def find_tasks(
        self,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list["Task"]:
        """Tasks across all pets, optionally filtered by status and/or pet.

        Pass `completed=True`/`False` to keep only done/pending tasks, and
        `pet_name` to keep only tasks involving that pet (case-insensitive).
        Both filters are optional; omitting both returns every task.
        """
        result = self.all_tasks()
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            target = pet_name.lower()
            result = [
                t for t in result if any(p.name.lower() == target for p in t.pets)
            ]
        return result

    def tasks_due_today(self, today: date) -> list["Task"]:
        """All still-pending tasks due on `today`, across every pet."""
        return [task for task in self.all_tasks() if task.is_due_today(today)]

    def to_dict(self) -> dict:
        """Serialize the owner, its pets, and all tasks into plain dicts.

        Pets are listed by index; each task records the indexes of the pets it
        belongs to, so a shared task (the same Task on several pets) is stored
        once and re-linked to every pet on load.
        """
        pet_index = {id(pet): i for i, pet in enumerate(self.pets)}
        tasks = []
        for task in self.all_tasks():
            tasks.append(
                {
                    "name": task.name,
                    "duration": task.duration,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat(),
                    "pet_indexes": [
                        pet_index[id(p)] for p in task.pets if id(p) in pet_index
                    ],
                    "frequency": task.frequency,
                    "preferred_time": (
                        task.preferred_time.isoformat()
                        if task.preferred_time is not None
                        else None
                    ),
                    "completed": task.completed,
                    "recurrence": task.recurrence,
                }
            )
        return {
            "name": self.name,
            "available_time": self.available_time,
            "pets": [{"name": p.name, "species": p.species} for p in self.pets],
            "tasks": tasks,
        }

    def save_to_json(self, path: str = "data.json") -> None:
        """Write this owner (pets + tasks) to a JSON file for persistence."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Rebuild an Owner (with pets and tasks) from a serialized dict."""
        owner = cls(
            name=data.get("name", ""),
            available_time=data.get("available_time", {}) or {},
        )
        pets = [Pet(name=p["name"], species=p["species"]) for p in data.get("pets", [])]
        for pet in pets:
            owner.add_pet(pet)
        for t in data.get("tasks", []):
            preferred = t.get("preferred_time")
            task = Task(
                name=t["name"],
                duration=t["duration"],
                priority=t["priority"],
                due_date=date.fromisoformat(t["due_date"]),
                frequency=t.get("frequency", 1),
                preferred_time=time.fromisoformat(preferred) if preferred else None,
                completed=t.get("completed", False),
                recurrence=t.get("recurrence"),
            )
            # Re-link the (possibly shared) task to each of its pets by index.
            for idx in t.get("pet_indexes", []):
                if 0 <= idx < len(pets):
                    pets[idx].add_task(task)
        return owner

    @classmethod
    def load_from_json(cls, path: str = "data.json") -> "Owner | None":
        """Load an Owner from a JSON file, or None if the file doesn't exist."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return None
        return cls.from_dict(data)

    def __str__(self) -> str:
        """Readable summary: name, pet count, and total task count."""
        return f"{self.name} — {len(self.pets)} pet(s), {len(self.all_tasks())} task(s)"


@dataclass
class Task:
    """A single pet-care activity (e.g. a walk, feeding, or meds)."""

    name: str
    duration: int            # minutes the task takes (per occurrence)
    priority: str            # "high", "medium", or "low"
    due_date: date           # the day this task should happen
    pets: list[Pet] = field(default_factory=list)  # pets this activity is for
    frequency: int = 1       # how many times per day it must be done
    preferred_time: time | None = None  # time the owner wants it (for conflicts)
    completed: bool = False  # whether the owner has finished it
    recurrence: str | None = None  # "daily", "weekly", or None for one-off

    # Lower number = more important, used as a sort key.
    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    # How far to advance the due date for each recurrence type.
    RECURRENCE_STEPS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}

    def is_due_today(self, today: date) -> bool:
        """True if this task is scheduled for `today` and isn't done yet."""
        return self.due_date == today and not self.completed

    def priority_rank(self) -> int:
        """Numeric rank for sorting; unknown priorities sort last."""
        return self.PRIORITY_ORDER.get(self.priority.lower(), len(self.PRIORITY_ORDER))

    def next_occurrence(self) -> "Task | None":
        """Build the next instance of a recurring task, or None if one-off.

        The new task's due_date is advanced from *this* task's due_date using a
        timedelta, so the cadence stays anchored to the schedule even if the
        task was completed late. It is attached to the same pets and starts
        pending (completed=False).
        """
        step = self.RECURRENCE_STEPS.get((self.recurrence or "").lower())
        if step is None:
            return None
        nxt = Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            due_date=self.due_date + step,
            frequency=self.frequency,
            preferred_time=self.preferred_time,
            completed=False,
            recurrence=self.recurrence,
        )
        # Attach to the same pets, keeping the Pet<->Task back-links in sync.
        for pet in list(self.pets):
            pet.add_task(nxt)
        return nxt

    def mark_complete(self) -> "Task | None":
        """Mark the task done; if recurring, create and return the next instance."""
        self.completed = True
        return self.next_occurrence()

    def total_daily_minutes(self) -> int:
        """Total time this task consumes in a day across all occurrences."""
        return self.duration * self.frequency

    def __str__(self) -> str:
        """Readable one-line view: status, name, duration, pets, and priority."""
        status = "✓" if self.completed else " "
        times = f" x{self.frequency}/day" if self.frequency > 1 else ""
        who = f" for {', '.join(p.name for p in self.pets)}" if self.pets else ""
        return (
            f"[{status}] {self.name} ({self.duration} min{times})"
            f"{who} [priority: {self.priority}]"
        )


# Default care window used when the owner hasn't specified one.
DEFAULT_WINDOW = {"start": "08:00", "end": "20:00"}


class Scheduler:
    """The brain: retrieves, organizes, and schedules tasks across all pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that plans tasks for the given owner."""
        self.owner = owner

    @property
    def tasks(self) -> list[Task]:
        """All tasks across the owner's pets (deduped), so no copy can drift."""
        return self.owner.all_tasks()

    def _window(self) -> tuple[time, time]:
        """Return (start, end) times for the owner's available care window."""
        window = self.owner.available_time or DEFAULT_WINDOW
        start = time.fromisoformat(window.get("start", DEFAULT_WINDOW["start"]))
        end = time.fromisoformat(window.get("end", DEFAULT_WINDOW["end"]))
        return start, end

    def _window_minutes(self, today: date | None = None) -> int:
        """How many minutes of care time are available in the window."""
        start, end = self._window()
        today = today or date.today()
        delta = datetime.combine(today, end) - datetime.combine(today, start)
        return max(0, int(delta.total_seconds() // 60))

    def sort_tasks(self, today: date | None = None) -> list[Task]:
        """Pending tasks for `today`, ordered by priority first, then by time.

        High-priority tasks come first; within the same priority, tasks are
        ordered by their preferred time of day (flexible tasks without a
        preferred_time sort last), and shortest-first breaks any remaining ties.
        """
        today = today or date.today()
        due = self.owner.tasks_due_today(today)
        end_of_day = time(23, 59, 59)
        return sorted(
            due,
            key=lambda t: (
                t.priority_rank(),
                t.preferred_time or end_of_day,
                t.duration,
            ),
        )

    def sort_by_time(self, today: date | None = None) -> list[Task]:
        """Pending tasks for `today`, ordered by their preferred time of day.

        Tasks without a preferred_time sort last (they're flexible), and ties
        fall back to priority then shortest-first for a stable order.
        """
        today = today or date.today()
        due = self.owner.tasks_due_today(today)
        end_of_day = time(23, 59, 59)
        return sorted(
            due,
            key=lambda t: (
                t.preferred_time or end_of_day,
                t.priority_rank(),
                t.duration,
            ),
        )

    def filter_tasks(self, today: date | None = None) -> list[Task]:
        """Keep the highest-priority tasks that fit the available time budget."""
        budget = self._window_minutes(today)
        kept: list[Task] = []
        used = 0
        for task in self.sort_tasks(today):
            cost = task.total_daily_minutes()
            if used + cost <= budget:
                kept.append(task)
                used += cost
        return kept

    def assign_times(self, today: date | None = None) -> list[tuple[time, Task]]:
        """Place kept tasks at preferred times (or packed) as (time, task) pairs.

        Occurrences that would start at or after the window end are dropped so
        the plan never spills past the owner's available care time.
        """
        today = today or date.today()
        start, end = self._window()
        window_end = datetime.combine(today, end)
        cursor = datetime.combine(today, start)
        plan: list[tuple[time, Task]] = []
        for task in self.filter_tasks(today):
            if task.preferred_time is not None:
                occ = datetime.combine(today, task.preferred_time)
            else:
                occ = cursor
            for _ in range(max(1, task.frequency)):
                if occ >= window_end:
                    break
                plan.append((occ.time(), task))
                occ += timedelta(minutes=task.duration)
            if task.preferred_time is None:
                cursor = occ
        return sorted(plan, key=lambda pair: pair[0])

    def detect_conflicts(
        self, today: date | None = None
    ) -> list[tuple[time, list[Task]]]:
        """Find time slots where two or more different tasks overlap in time.

        Two occurrences conflict when one starts before the other ends, even if
        their start times differ (e.g. 08:00+30min vs 08:15+10min).
        """
        today = today or date.today()

        def to_dt(t: time) -> datetime:
            """Anchor a time to today so comparisons can't wrap across midnight."""
            return datetime.combine(today, t)

        # Build (start, end, task) intervals as datetimes, then sweep in start order.
        intervals = sorted(
            (
                (to_dt(start), to_dt(start) + timedelta(minutes=task.duration), task)
                for start, task in self.assign_times(today)
            ),
            key=lambda iv: (iv[0], iv[1]),  # sort by (start, end) only, never the Task
        )

        conflicts: list[tuple[time, list[Task]]] = []
        group: list[Task] = []
        group_start: datetime | None = None
        group_end: datetime | None = None

        def flush() -> None:
            # Single source of truth for emitting a finished cluster.
            if len(group) > 1:
                conflicts.append((group_start.time(), list(group)))

        for start, occ_end, task in intervals:
            if group_end is not None and start < group_end:
                # Overlaps the current cluster; extend it.
                if task not in group:
                    group.append(task)
                group_end = max(group_end, occ_end)
            else:
                flush()
                group = [task]
                group_start = start
                group_end = occ_end
        flush()
        return conflicts

    def conflict_warnings(self, today: date | None = None) -> list[str]:
        """Return human-readable warnings for overlapping tasks (never raises).

        A "lightweight" check: it reuses detect_conflicts and turns each clash
        into a plain warning string instead of throwing an exception, so the
        caller can print warnings and keep running. Notes whether the clash is
        for the same pet (one pet double-booked) or across different pets.
        """
        warnings: list[str] = []
        for start, tasks in self.detect_conflicts(today):
            names = ", ".join(t.name for t in tasks)
            # Collect every pet involved across the clashing tasks.
            pets = {p.name for task in tasks for p in task.pets}
            if len(pets) <= 1:
                who = next(iter(pets), "a pet")
                scope = f"{who} is double-booked"
            else:
                scope = f"{len(pets)} pets need attention at once ({', '.join(sorted(pets))})"
            warnings.append(
                f"WARNING: {start:%H:%M} - {scope}: {names} overlap."
            )
        return warnings

    def free_slots(
        self, today: date | None = None, min_minutes: int = 1
    ) -> list[tuple[time, time]]:
        """Return the open (start, end) gaps in the care window after planning.

        Builds the day's plan, merges every scheduled occurrence into busy
        intervals, then sweeps the care window start-to-end and emits the gaps
        between them. Only gaps at least `min_minutes` long are returned, so the
        result is the set of windows where new work could actually fit.
        """
        today = today or date.today()
        win_start, win_end = self._window()
        cursor = datetime.combine(today, win_start)
        day_end = datetime.combine(today, win_end)

        # Busy intervals from the generated plan, merged so overlaps don't
        # produce phantom zero-length gaps. Sort by start, then sweep.
        busy = sorted(
            (
                datetime.combine(today, slot),
                datetime.combine(today, slot) + timedelta(minutes=task.duration),
            )
            for slot, task in self.generate_plan(today)
        )

        slots: list[tuple[time, time]] = []

        def emit(gap_start: datetime, gap_end: datetime) -> None:
            if (gap_end - gap_start) >= timedelta(minutes=min_minutes):
                slots.append((gap_start.time(), gap_end.time()))

        for start, end in busy:
            if start > cursor:
                emit(cursor, min(start, day_end))
            cursor = max(cursor, end)
            if cursor >= day_end:
                break
        if cursor < day_end:
            emit(cursor, day_end)
        return slots

    def find_next_available_slot(
        self, duration: int, today: date | None = None, after: time | None = None
    ) -> time | None:
        """Earliest start time that fits a `duration`-minute task, or None.

        Scans the free gaps (see `free_slots`) for the first one long enough to
        hold the task. Pass `after` to only consider slots at or past a given
        time of day (e.g. "when's my next free moment from now?").
        """
        today = today or date.today()
        for gap_start, gap_end in self.free_slots(today, min_minutes=duration):
            start = gap_start
            if after is not None and start < after:
                # Try sliding the start forward into this gap.
                start = after
            slot_start = datetime.combine(today, start)
            slot_end = datetime.combine(today, gap_end)
            if (slot_end - slot_start) >= timedelta(minutes=duration):
                return start
        return None

    def generate_plan(self, today: date | None = None) -> list[tuple[time, Task]]:
        """Produce the final ordered daily plan (sort -> filter -> assign)."""
        return self.assign_times(today)
