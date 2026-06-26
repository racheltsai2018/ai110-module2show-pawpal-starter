"""PawPal+ demo: build an owner with pets and tasks, then print today's plan."""

from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def main():
    today = date.today()

    # An owner with two pets.
    biscuit = Pet("Biscuit", "Golden Retriever")
    snow = Pet("Snow", "Cat")

    owner = Owner("Sam", available_time={"start": "08:00", "end": "20:00"})
    owner.add_pet(biscuit)
    owner.add_pet(snow)

    # Three tasks at different times.
    walk = Task("Morning walk", 30, "high", today, preferred_time=time(8, 0))
    biscuit.add_task(walk)

    feed = Task("Feeding", 10, "high", today, preferred_time=time(9, 0), frequency=1)
    biscuit.add_task(feed)
    snow.add_task(feed)  # shared feeding for both pets

    meds = Task("Dog meds", 5, "medium", today, preferred_time=time(18, 0))
    biscuit.add_task(meds)

    # Build today's schedule.
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan(today)

    print(f"Today's Schedule for {owner.name} ({today:%A, %B %d, %Y})")
    for start, task in plan:
        pets = ", ".join(p.name for p in task.pets)
        print(f"  {start:%H:%M} {task.name}: {task.duration} min, task priority:{task.priority}, Pets: {pets}")

    conflicts = scheduler.detect_conflicts(today)
    if conflicts:
        print("\n⚠️  Scheduling conflicts:")
        for start, tasks in conflicts:
            names = ", ".join(t.name for t in tasks)
            print(f"  {start:%H:%M} — {names}")


if __name__ == "__main__":
    main()
