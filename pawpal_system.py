"""PawPal+ system class skeletons.

Generated from diagrams/uml.mmd. Method bodies are stubs (no logic yet).
"""

from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    species: str
    age: int


@dataclass
class Owner:
    name: str
    pet: Pet
    available_minutes: int
    preferences: dict = field(default_factory=dict)


@dataclass
class Task:
    name: str
    duration: int
    priority: str
    preferred_time: str
    recurrence: str

    def is_due_today(self) -> bool:
        ...

    def __str__(self) -> str:
        ...


class Scheduler:
    def __init__(self, tasks: list[Task], owner: Owner) -> None:
        self.tasks = tasks
        self.owner = owner

    def sort_tasks(self) -> list[Task]:
        ...

    def filter_tasks(self) -> list[Task]:
        ...

    def assign_times(self) -> list:
        ...

    def generate_plan(self) -> list:
        ...
