# PawPal+ Project Reflection

## 1. System Design

**Step 1 part 5:
-Three core actions:
    - Add owner and pet information
    - add/ complete/ delete tasks
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
AI tools is used to help design brainstorming during the project. While brainstorming the classes and functions needed, AI helped point out the missing parts or holes in the system. Aside from pointing out the problems, AI also made suggestions on ways to improve it.
- What kinds of prompts or questions were most helpful?
The prompt asking AI to generate a Mermaid.js class diagram is most helpful. The reason for this is because I was not aware that AI can generate Mermaid.js class diagrams. The Mermaid.js class diagrams are really helpful with visualizing the class and class relationships.
- How did using separate chat sessions for different phases help you stay organized?
Using separate chat sessions for different phases or different topics allow me to organize the chats depending on the section/ topics. When I need to refer back to a certain topic or look for some information, different chats also make this easier.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
When creating the task list for owner and pets. AI suggested keeping a separate list for each pet and listing all the task. However if an owner has two dogs, morning walk will have 2 task, when it can be considered as one task.
- How did you evaluate or verify what the AI suggested?
The reason I did not accept what AI suggested is because I thought about the logic, and that is not realistic since tasks like walks, and feeding the pets can be considered as one task instead of several task. An example would be a household with 2 dogs and 1 cat can be fed together at lunch time instead of 3 separate times. Similarly with walks, the 2 dogs can go out on a walk together instead of 2 separate walks. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
The test tested most core behaviors of this system. It includes testing if tasks can be marked complete and adding a task for a pet will increase the task count. For sorting, the test includes sorting task by priority, and preferred time of the day. For recurrence tasks, completing daily task will create a new task due the next day, creating a weekly task will create a new task due a week later, and ensuring the task will be assigned to the same pet. For conflicts, task with identical time and animals are detected, partial overlap of the time for two task also gives warning, and conflicting tasks does give warning messages.

- Why were these tests important?
These tests are important because it ensures that the core behaviors of the system are working properly. Without these tests, the developer are unable to test the application in a fast way.

**b. Confidence**

- How confident are you that your scheduler works correctly?
I am confident in the core behaviors that were tested, since all the test in test_pawpal.py passed. However, I am less confident in the possible bugs that were not discovered while I was testing the application.

- What edge cases would you test next if you had more time?
If I had more time I would test the recurrence task, and refine the recurrence methods. Currently, the generated schedule depends the the current non-completed task. If I select to generate the schedule for a day a week later, it would not show the weekly task unless I completed the current weekly task.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satified with the functionality where users are able to add several pets to the same task. An example would be an owner with 3 dogs, only have to do the morning walk once.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
If I had another iteration, I would improve the recurrence method and the due date methods. Currently, the due date for recurrent method depends on when the user finishes the previous recurrent task. If I had another iteration, I would make it so that if the weekly task is created on Wednesday and is due next Wednesday, the next weekly task will due two weeks later on Wednesday.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
I learned AI is able to give suggestions on different ways to improve the system. However, the developer still has to review and process what AI produces since AI is nto always correct. The developer will have to correct AI when it makes a mistake.
