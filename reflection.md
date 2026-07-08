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

- **a. What you tested**

  I tested the four core algorithmic behaviors added in Phase 4, organized 
  around 5 groups of tests (22 total):

  1. **Sorting order** — priority as the primary key, preferred_time and 
     duration as tiebreakers, including the case where a task has no 
     preferred_time.
  2. **Budget-constrained scheduling** — tasks that fit exactly at the time 
     boundary, tasks that overflow the budget (verifying a smaller later task 
     still gets picked up rather than the scheduler stopping early), and 
     completed tasks correctly freeing up budget instead of competing for it.
  3. **Recurring task completion** — marking a daily/weekly task complete 
     correctly appends a new occurrence dated +1 or +7 days out, while a 
     non-recurring or unrecognized-recurrence task appends nothing.
  4. **Conflict detection** — two tasks at the same time across different 
     pets are flagged, three tasks at the same time produce all 3 pairs, and 
     completed or untimed tasks are correctly excluded from conflicts.
  5. **Empty/boundary cases** — an owner with no pets, or a pet with no tasks, 
     produces empty results everywhere without crashing.

  These were important because they're exactly the places where a small 
  mistake (like an off-by-one on a boundary, or including a completed task in 
  the budget) would silently produce a subtly wrong schedule rather than an 
  obvious crash — the kind of bug that's easy to miss just from eyeballing 
  `main.py` output once.

  **b. Confidence**

  I'd rate my confidence at 4/5. All 22 tests pass, and they specifically 
  target the boundary conditions most likely to hide bugs, not just the 
  happy path. The main gaps are things I know about rather than things I'm 
  unsure of: `preferred_time` has no format validation (a malformed string 
  would raise an error instead of failing gracefully), and `Owner.preferences` 
  is modeled but not yet used by any scheduling logic.

  If I had more time, I'd test: what happens with an invalid `preferred_time` 
  string (e.g., "8am" or "25:99"); a task with `duration_minutes` of 0; 
  multiple recurring tasks completed in the same run to confirm they don't 
  interfere with each other's next-occurrence dates; and `explain_schedule()`'s 
  full text output directly, to lock down its formatting as a contract rather 
  than only testing the data it's built from.

---

## 5. Reflection

- **a. What went well**

  I'm most satisfied with the recurring-task and conflict-detection logic — 
  they were the parts I was least sure how to approach at the start (especially 
  figuring out that daily/weekly recurrence needed an actual `date` field, not 
  just a label), and the final implementation handles the edge cases (unknown 
  recurrence values, tasks with no pet) cleanly rather than just working for 
  the obvious case.

  **b. What you would improve**

  If I did another iteration, I'd want to actually wire `Owner.preferences` 
  into the scheduling logic — right now it's modeled in the data but has no 
  effect on sorting or selection, which is a gap between what the system 
  looks like it can do and what it actually does. I'd also add input 
  validation for `preferred_time` so a malformed time string fails gracefully 
  instead of raising an error, and extend conflict detection to catch 
  overlapping time ranges, not just exact-match start times.

  **c. Key takeaway**

  The biggest thing I learned is that AI is very good at *implementing* a 
  decision once I've made it, but not at *making* the decision for me — and 
  trying to skip that step (by asking vague questions instead of stating my 
  own design choices) produced worse results than being explicit up front. 
  Being the "lead architect" meant the real work was deciding things like 
  "priority beats time" or "conflicts are global, not per-pet" — the AI could 
  build any of those correctly, but it couldn't tell me which one was right 
  for this scenario.
