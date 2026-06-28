"""PawPal+ demo: build an owner with pets and tasks, then print today's plan.

Output is dressed up for the terminal: color-coded priorities/status (via
colorama), task-type emojis, and aligned tables (via tabulate).
"""

import sys
from datetime import date, time

from colorama import Fore, Style, init as colorama_init
from tabulate import tabulate

from pawpal_system import Owner, Pet, Scheduler, Task


DATA_FILE = "data.json"

# Windows terminals often default to a legacy code page (cp1252) that can't
# encode emojis; force UTF-8 so the icons render instead of crashing.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Initialize colorama so ANSI colors work on Windows terminals too.
# autoreset=True means every print resets styling afterward automatically.
colorama_init(autoreset=True)


# --- Presentation helpers --------------------------------------------------

PRIORITY_COLORS = {
    "high": Fore.RED,
    "medium": Fore.YELLOW,
    "low": Fore.GREEN,
}


def color_priority(priority: str) -> str:
    """Return the priority label wrapped in its color (HIGH=red, etc.)."""
    color = PRIORITY_COLORS.get(priority.lower(), Fore.WHITE)
    return f"{color}{priority.upper()}{Style.RESET_ALL}"


def status_icon(completed: bool) -> str:
    """Green check for done, dim hourglass for pending."""
    if completed:
        return f"{Fore.GREEN}✓ done{Style.RESET_ALL}"
    return f"{Fore.CYAN}⏳ pending{Style.RESET_ALL}"


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


def when_str(task: Task) -> str:
    """Preferred time as HH:MM, or a 'flexible' marker."""
    return f"{task.preferred_time:%H:%M}" if task.preferred_time else "flexible"


def header(text: str) -> None:
    """Print a bold, bright section header."""
    print(f"\n{Style.BRIGHT}{Fore.MAGENTA}{text}{Style.RESET_ALL}")


def build_demo_owner(today: date) -> Owner:
    """Build the sample owner with pets and tasks used for the demo."""
    # An owner with two pets.
    biscuit = Pet("Biscuit", "Golden Retriever")
    snow = Pet("Snow", "Cat")

    owner = Owner("Sam", available_time={"start": "08:00", "end": "20:00"})
    owner.add_pet(biscuit)
    owner.add_pet(snow)

    meds = Task("Dog meds", 5, "medium", today, preferred_time=time(18, 0))
    biscuit.add_task(meds)

    feed = Task("Feeding", 10, "high", today, preferred_time=time(9, 0), frequency=1)
    biscuit.add_task(feed)
    snow.add_task(feed)  # shared feeding for both pets

    walk = Task("Morning walk", 30, "high", today, preferred_time=time(8, 0))
    biscuit.add_task(walk)

    # Low priority but an early preferred time: by *time* it sorts near the top,
    # but priority-first sorting keeps it near the bottom — a clear contrast.
    play = Task("Play with Snow", 15, "low", today, preferred_time=time(8, 30))
    snow.add_task(play)

    brush = Task("Brush Snow", 10, "low", today, preferred_time=time(7, 0))
    snow.add_task(brush)
    brush.mark_complete()  # already done today

    snow_meds = Task("Cat meds", 5, "high", today, preferred_time=time(18, 0))
    snow.add_task(snow_meds)  # collides with Biscuit's "Dog meds" at 18:00

    return owner


def main():
    today = date.today()

    # Reuse saved data if it exists, otherwise build (and save) the demo.
    owner = Owner.load_from_json(DATA_FILE)
    if owner is None:
        owner = build_demo_owner(today)
        owner.save_to_json(DATA_FILE)
        print(f"{Fore.YELLOW}(No saved data found — created {DATA_FILE} with demo pets/tasks.){Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}(Loaded saved data from {DATA_FILE}.){Style.RESET_ALL}")

    scheduler = Scheduler(owner)

    print(f"\n{Style.BRIGHT}🐾 PawPal+ — Daily plan for {Fore.CYAN}{owner.name}{Style.RESET_ALL}"
          f"{Style.BRIGHT} ({today:%A, %B %d, %Y}){Style.RESET_ALL}")

    # --- Sorting: order by time of day, despite being added out of order ---
    header("⏰ Tasks sorted by time of day")
    print(tabulate(
        [
            [when_str(t), f"{task_emoji(t.name)} {t.name}", color_priority(t.priority)]
            for t in scheduler.sort_by_time(today)
        ],
        headers=["Time", "Task", "Priority"],
        tablefmt="rounded_outline",
    ))

    # --- Sorting: priority first (High -> Medium -> Low), then by time ---
    header("📋 Tasks sorted by priority, then time")
    print(tabulate(
        [
            [
                color_priority(t.priority),
                when_str(t),
                f"{task_emoji(t.name)} {t.name}",
                f"{t.duration} min",
            ]
            for t in scheduler.sort_tasks(today)
        ],
        headers=["Priority", "Time", "Task", "Duration"],
        tablefmt="rounded_outline",
    ))

    # --- Filtering: by completion status and by pet name ---
    header("🔎 Tasks by status & pet")
    rows = []
    for t in owner.find_tasks():
        pets = ", ".join(p.name for p in t.pets)
        rows.append([status_icon(t.completed), f"{task_emoji(t.name)} {t.name}", pets])
    print(tabulate(
        rows,
        headers=["Status", "Task", "Pets"],
        tablefmt="rounded_outline",
    ))

    snow_tasks = ", ".join(t.name for t in owner.find_tasks(pet_name="Snow"))
    print(f"  {Fore.CYAN}🐱 Tasks involving Snow:{Style.RESET_ALL} {snow_tasks}")

    # --- Full generated plan + conflicts ---
    header("🗓️  Today's Schedule")
    plan = scheduler.generate_plan(today)
    if plan:
        print(tabulate(
            [
                [
                    f"{start:%H:%M}",
                    f"{task_emoji(task.name)} {task.name}",
                    f"{task.duration} min",
                    color_priority(task.priority),
                    ", ".join(p.name for p in task.pets),
                ]
                for start, task in plan
            ],
            headers=["Time", "Task", "Duration", "Priority", "Pets"],
            tablefmt="rounded_outline",
        ))
    else:
        print(f"  {Fore.YELLOW}No tasks fit the available time window.{Style.RESET_ALL}")

    # --- Next available slot: where could a new 20-min task fit today? ---
    slot = scheduler.find_next_available_slot(20, today)
    if slot is not None:
        print(f"\n{Fore.GREEN}🕳️  Next free 20-min slot today: {slot:%H:%M}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}🕳️  No free 20-min slot left today.{Style.RESET_ALL}")

    # --- Lightweight conflict warnings (returns strings, never crashes) ---
    warnings = scheduler.conflict_warnings(today)
    if warnings:
        print(f"\n{Style.BRIGHT}{Fore.RED}⚠️  Scheduling conflicts:{Style.RESET_ALL}")
        for warning in warnings:
            print(f"  {Fore.RED}{warning}{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.GREEN}✅ No scheduling conflicts. All clear!{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
