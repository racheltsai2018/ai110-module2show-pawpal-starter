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

    meds = Task("Dog meds", 5, "medium", today, preferred_time=time(18, 0))
    biscuit.add_task(meds)

    feed = Task("Feeding", 10, "high", today, preferred_time=time(9, 0), frequency=1)
    biscuit.add_task(feed)
    snow.add_task(feed)  # shared feeding for both pets

    walk = Task("Morning walk", 30, "high", today, preferred_time=time(8, 0))
    biscuit.add_task(walk)

    play = Task("Play with Snow", 15, "low", today)  # no preferred time
    snow.add_task(play)

    brush = Task("Brush Snow", 10, "low", today, preferred_time=time(7, 0))
    snow.add_task(brush)
    brush.mark_complete()  # already done today


    snow_meds = Task("Cat meds", 5, "high", today, preferred_time=time(18, 0))
    snow.add_task(snow_meds)  # collides with Biscuit's "Dog meds" at 18:00

    scheduler = Scheduler(owner)

    # --- Sorting: order by time of day, despite being added out of order ---
    print(f"Tasks sorted by time for {owner.name} ({today:%A, %B %d, %Y}):")
    for task in scheduler.sort_by_time(today):
        when = f"{task.preferred_time:%H:%M}" if task.preferred_time else "flexible"
        print(f"  {when:>8}  {task.name} [{task.priority}]")

    # --- Filtering: by completion status and by pet name ---
    print("\nPending tasks (not yet done):")
    for task in owner.find_tasks(completed=False):
        print(f"  - {task.name}")

    print("\nCompleted tasks:")
    for task in owner.find_tasks(completed=True):
        print(f"  - {task.name}")

    print("\nTasks involving Snow:")
    for task in owner.find_tasks(pet_name="Snow"):
        print(f"  - {task.name}")

    # --- Full generated plan + conflicts ---
    print(f"\nToday's Schedule for {owner.name}:")
    for start, task in scheduler.generate_plan(today):
        pets = ", ".join(p.name for p in task.pets)
        print(f"  {start:%H:%M} {task.name}: {task.duration} min, priority:{task.priority}, Pets: {pets}")

    # --- Lightweight conflict warnings (returns strings, never crashes) ---
    warnings = scheduler.conflict_warnings(today)
    if warnings:
        print("\n[!] Scheduling conflicts:")
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("\nNo scheduling conflicts. All clear!")


if __name__ == "__main__":
    main()
