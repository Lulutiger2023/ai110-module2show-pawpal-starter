# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The three core actions a user should be able to perform are:

1. **Add/edit a pet care task** — such as a walk, feeding, medication, or grooming session, including its duration and priority.
2. **Generate a daily plan** — the system builds a schedule based on available time, task priority, and owner preferences, and explains why it chose that plan.
3. **View today's tasks** — the user can see the generated schedule clearly, in order, with reasoning for each choice.

To support these actions, I designed four classes:

- **Owner**: represents the pet owner, holds preferences and their pets.
- **Pet**: represents a pet, holds basic info and its list of tasks.
- **Task**: represents a single care task (title, duration, priority, recurrence).
- **Scheduler**: takes a list of tasks and available time, and builds/explains a daily schedule.

**b. Design changes**

Yes. After drafting the initial skeleton, I asked my AI assistant (Claude Code)
to review pawpal_system.py against the UML. It flagged that Scheduler had no
connection back to Owner or Pet, meaning Owner.preferences could never
influence scheduling, and explain_schedule() couldn't reference which pet a
task belonged to. It also caught a type mismatch: priority was typed as int
in the UML but str in the code, which would have caused incorrect sort order
(alphabetical instead of by importance) once sort_tasks() was implemented.

I made two changes as a result:
1. Changed Task.priority from str to int (1 = highest priority, 3 = lowest)
   so sorting works correctly.
2. Added a `pet` back-reference on Task (set automatically inside
   Pet.add_task), and changed Scheduler to take an `owner: Owner` instead of
   a flat task list, deriving its tasks internally from owner.pets. This
   gives the scheduler both pet context and access to owner preferences for
   future logic.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
