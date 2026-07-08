# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

Algorithms implemented in `pawpal_system.py`:

- **Priority-based sorting with time and duration tiebreakers** — `Scheduler.sort_tasks()` (priority ascending, then `preferred_time`, then `duration_minutes`)
- **Greedy time-budgeted scheduling** — `Scheduler.build_schedule()` (fills `available_minutes` best-first, skipping completed tasks)
- **Time-based filtering by pet and completion status** — `Owner.filter_tasks()`
- **Daily/weekly recurring task auto-recreation** — `Task.next_occurrence()` and `Task.mark_complete()`
- **Global scheduling conflict detection** — `Scheduler.find_conflicts()` (tasks sharing a `preferred_time`, across all pets)
- **Human-readable plan explanation** — `Scheduler.explain_schedule()`

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Daily plan for Jordan (45/60 min used):
Included:
  - Feeding (Biscuit, priority 1, 10 min)
  - Morning walk (Biscuit, priority 1, 30 min)
  - Litter box cleaning (Mochi, priority 2, 5 min)
Excluded (ran out of time — lowest priority / longest first):
  - Play session (Mochi, priority 3, 20 min)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
$ python -m pytest
============================= test session starts ==============================
platform darwin -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/lulutiger/Desktop/codepath/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 22 items                                                             

tests/test_pawpal.py ......................                              [100%]

============================== 22 passed in 0.05s ==============================

```

**Confidence Level: ⭐⭐⭐⭐ (4/5)** — Core scheduling logic is well-covered by automated tests, including tricky edge cases (exact-fit boundaries, completed tasks freeing budget, recurring task state mutation). One star withheld because `preferred_time` parsing has no input validation (a malformed string like "8am" would raise an error rather than fail gracefully), and `Owner.preferences` isn't yet used by the scheduling logic.


## 📐 Smarter Scheduling

| Feature           | Method(s)                                           | Notes                                                        |
| ----------------- | --------------------------------------------------- | ------------------------------------------------------------ |
| Task sorting      | `Scheduler.sort_tasks()`                            | Sorts by priority (ascending, 1=highest) first, then by `preferred_time` ("HH:MM") as a tiebreaker, then by duration. Tasks with no preferred_time sort last within their priority group. |
| Filtering         | `Owner.filter_tasks(pet_name=None, completed=None)` | Filters tasks by pet name and/or completion status; either filter is optional. |
| Conflict handling | `Scheduler.find_conflicts()`                        | Detects tasks (across all pets, globally) that share the exact same `preferred_time`. Does not detect overlapping durations at different start times. |
| Recurring tasks   | `Task.next_occurrence()`, `Task.mark_complete()`    | When a recurring task ("daily"/"weekly") is marked complete, a new uncompleted Task is automatically created with its `date` advanced by 1 or 7 days. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:


1. Enter your name as the owner, then add one or more pets by name and species.
2. For each pet, add care tasks with a title, duration, priority (low/medium/high), 
   and optionally a preferred time (e.g., 08:00).
3. Added tasks appear in a live table showing which pet they belong to, their 
   duration, priority, and completion status.
4. Set the available minutes for the day and click "Generate schedule."
5. The scheduler sorts tasks by priority (then time, then duration), selects 
   as many as fit within the time budget, and flags any tasks that share the 
   exact same time slot as a scheduling conflict — shown as a warning above 
   the plan.
6. Tasks that didn't fit, or that are already marked complete, are tucked 
   into collapsible sections so the main focus stays on today's actual plan.

Key Scheduler behaviors shown: priority-first sorting with time/duration 
tiebreakers, budget-constrained task selection, and cross-pet conflict 
detection.

Sample output :

```
=== Today's Schedule ===
Daily plan for Jordan (45/60 min used):
Included:
  - Feeding (Biscuit, priority 1, 10 min)
  - Morning walk (Biscuit, priority 1, 30 min)
  - Litter box cleaning (Mochi, priority 2, 5 min)
Excluded (ran out of time — lowest priority / longest first):
  - Play session (Mochi, priority 3, 20 min)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

