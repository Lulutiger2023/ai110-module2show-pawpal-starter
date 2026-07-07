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
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature           | Method(s)                                           | Notes                                                        |
| ----------------- | --------------------------------------------------- | ------------------------------------------------------------ |
| Task sorting      | `Scheduler.sort_tasks()`                            | Sorts by priority (ascending, 1=highest) first, then by `preferred_time` ("HH:MM") as a tiebreaker, then by duration. Tasks with no preferred_time sort last within their priority group. |
| Filtering         | `Owner.filter_tasks(pet_name=None, completed=None)` | Filters tasks by pet name and/or completion status; either filter is optional. |
| Conflict handling | `Scheduler.find_conflicts()`                        | Detects tasks (across all pets, globally) that share the exact same `preferred_time`. Does not detect overlapping durations at different start times. |
| Recurring tasks   | `Task.next_occurrence()`, `Task.mark_complete()`    | When a recurring task ("daily"/"weekly") is marked complete, a new uncompleted Task is automatically created with its `date` advanced by 1 or 7 days. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
