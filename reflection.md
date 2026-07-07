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

My scheduler considers three main constraints:

1. **Available time** (`available_minutes`) — the hard budget for the day. 
   `build_schedule()` greedily fills this budget best-first, dropping 
   tasks that would overflow it.
2. **Priority** (`priority`, 1 = highest to 3 = lowest) — this is the 
   primary ordering factor. When time runs out, the lowest-priority 
   (and longest) tasks are the ones excluded.
3. **Preferred time** (`preferred_time`) — used as a secondary sort key 
   within the same priority group, so tasks are still read in a 
   sensible chronological order, and also used for conflict detection 
   (two tasks sharing the same time slot).

I decided priority should outrank time when ordering tasks, because the 
scenario is about a busy owner who needs the *most important* care tasks 
done first if time is short — a high-priority task at a less convenient 
time should still come before a low-priority task at a "nicer" time. Time 
of day matters for readability and conflict-checking, but shouldn't 
override what actually needs to happen.

`Owner.preferences` (a dict) is modeled in the data but not yet used by 
the scheduling logic — it's a placeholder for future constraints like 
"prefers morning walks," which I didn't have time to wire into the 
sorting/selection logic in this phase.

**b. Tradeoffs**

One tradeoff is in conflict detection: `find_conflicts()` only flags tasks 
that share the exact same `preferred_time` string (e.g., two tasks both at 
"08:00"). It does not detect overlapping durations — for example, a 30-minute 
task starting at 08:00 and a task starting at 08:15 would genuinely overlap 
in real time, but aren't flagged because their preferred_time values differ. 
This is a reasonable simplification for this assignment: exact-match 
detection is simple, fast, and catches the most obvious scheduling mistakes 
(double-booking the same slot), even though a full interval-overlap check 
would be more accurate.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI (Claude Code, in VS Code) throughout the project in several distinct roles:

- **Design brainstorming**: generated the initial Mermaid.js UML class 
  diagram from a plain-language description of my four classes and their 
  attributes/methods.
- **Scaffolding**: translated the UML into dataclass-based Python stubs, 
  then later implemented the full logic for each class (sorting, 
  filtering, recurring tasks, conflict detection).
- **Design review**: I asked it to review my class skeleton against the 
  UML before implementing logic, which surfaced two real gaps — a missing 
  Scheduler-Owner link and a priority type mismatch (int vs. str) that 
  would have broken sorting.
- **Test generation**: drafted pytest tests for core behaviors 
  (task completion, task addition) based on a plain description of what 
  to verify.
- **Code evaluation**: reviewed one of my own implemented methods 
  (`sort_tasks()`) and judged whether it could be simplified.

The most helpful prompts were ones that asked for a *review against a 
concrete artifact* rather than open-ended help — for example, "review 
pawpal_system.py against uml.mmd, are there missing relationships or 
logic bottlenecks?" produced much more useful, specific feedback than a 
vague "does this look okay?" would have. Prompts that stated my own 
design decisions explicitly (e.g., "priority is primary, time is a 
tiebreaker") before asking it to implement also reduced back-and-forth, 
since the AI didn't have to guess at ambiguous requirements.

**b. Judgment and verification**

I asked my AI assistant whether `Scheduler.sort_tasks()` could be simplified 
for readability or performance. It concluded the current version (a single 
`sorted()` call with a tuple key) was already close to optimal, and 
explained that Python's `sorted()` calls the key function once per element 
rather than repeatedly, so there was no performance issue to fix. It offered 
one minor readability alternative (naming the key function instead of using 
an inline lambda) but recommended keeping the original.

I verified this reasoning made sense — the compact lambda version is what 
I kept. More usefully, the AI also flagged an edge case unrelated to my 
original question: `_time_key()` would raise a ValueError on a malformed 
preferred_time string (e.g., "8am" instead of "08:00"). I decided not to 
fix this now since it's out of scope for the current phase, but I noted it 
as a known limitation to revisit later rather than ignoring it silently.

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
