# PawPal+ Project Reflection

## 1. System Design

**Step 1 part 5:
-Three core actions:
    - Add owner and pet information
    - add/ edit/ delete tasks
    - put the task in a schedule and display schedule

**a. Initial design**

- Briefly describe your initial UML design.
The UML design would include 4 classes. The Owner class would include data like the name of owner, the pets the owner own, the available_times of the owner. The Pet class include the name of the pet and the species of the pet. The task include the name of task, the duration, the priority, and recurrence of the task. The scheduler class include the list of tasks, and the owner that will perform this task. The relationships between these classes are the scheduler can read constraints depending on the owner, and the scheduler schedules the tasks. The owner owns the tasks and has pets. 
- What classes did you include, and what responsibilities did you assign to each?
The classes include Owner, Pet, Task, and Scheduler. The responsibility of owner will contain the data of the owner, the data of the pets this owner owns, and the time window the owner can do the tasks. The responsibility of pet will include data of the pet including the name and species. The task class will be responsible for keeping track of the what task name, the duration, and priority. The scheduler class is in charge of organizing all the tasks for one owner for a suitable schedule including a list of task for the current owner. 

**b. Design changes**

- Did your design change during implementation?
Yes, I changed the design during implementation.
- If yes, describe at least one change and why you made it.
I made several changes to the design. By following the instructions I gave the class Pet its own list of task. A function was added to support shared task. An example would be if the owner had 3 dogs and they all have a walking task, the owner can take all 3 of them out on a walk together instead of doing 3 seperate walks.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
Constraints my scheduler considers includes the available time, which indicates the time the owner is available to do the tasks. Other constraints include priority level of the tasks, the duration and frequency of the task. Lastly, is that if the owner wants to perform a certain task at a specific time it is included in the task. 

- How did you decide which constraints mattered most?
The priority constraint matters the most since it indicates the importance of the tasks. The tasks with high priorities will be scheduled first. If there is not enough time to fit all the task in the available time, the lower priority ones will be disregarded first. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
One tradeoff my scheduler makes is disregarding the lower priority tasks if the tasks do not fit in the available windows for the day. The con of this tradeoff is that this means that some tasks will be completely disregarded for that day.
- Why is that tradeoff reasonable for this scenario?
This tradeoff is reasonable because other high priority tasks are a lot more important than the low priority one. An example would be feeding the dog medicine (high) and playing with the dog (low). In this case, not playing with the dog for 1-2 days is not impactful, but skipping medicine could have a negative impact on the dog's health. 

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
