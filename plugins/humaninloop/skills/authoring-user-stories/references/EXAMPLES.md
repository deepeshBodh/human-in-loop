# User Story Examples

Complete examples demonstrating proper user story format.

## Example 1: P1 User Story (Core)

```markdown
### User Story 1 - Create Recurring Task (Priority: P1)

A user wants to create a task that automatically repeats on a schedule. They select
a task, choose a recurrence pattern (daily, weekly, or monthly), and save. The system
generates future task instances based on this pattern.

**Why this priority**: This is the core value proposition of the recurring tasks
feature. Without the ability to create recurring tasks, the entire feature is
non-functional. All other stories depend on this capability existing.

**Independent Test**: Create a new task, set it to repeat weekly on Mondays,
save, and verify that task instances appear on the next 4 Mondays in the task list.

**Acceptance Scenarios**:
1. **Given** a user is viewing a task they own, **When** they click "Make Recurring"
   and select "Weekly on Mondays", **Then** they see a confirmation showing the
   recurrence pattern and next 3 occurrences.

2. **Given** a user has set a task to repeat daily, **When** they save the recurrence
   settings, **Then** the task shows a recurring indicator icon and the next
   occurrence date.

3. **Given** a user is creating a new task, **When** they enable recurrence before
   saving, **Then** the task is created with the recurrence pattern applied from
   the start date.
```

## Example 2: P2 User Story (Important)

```markdown
### User Story 2 - Edit Recurrence Pattern (Priority: P2)

A user realizes they set the wrong recurrence pattern and needs to change it.
They access the recurring task, modify the pattern (e.g., from weekly to monthly),
and the system updates all future occurrences while preserving completed instances.

**Why this priority**: Users will frequently need to adjust recurrence patterns
as their schedules change. While the feature works without this (users could
delete and recreate), it creates significant friction. Expected in a complete
recurring tasks implementation.

**Independent Test**: Create a weekly recurring task with 4 future instances,
change it to monthly, and verify that future instances are regenerated on the
new schedule while any completed instances remain unchanged.

**Acceptance Scenarios**:
1. **Given** a user has a weekly recurring task with 3 future instances, **When**
   they change the pattern to "Monthly on the 1st", **Then** the future instances
   are replaced with monthly occurrences and a confirmation message appears.

2. **Given** a recurring task has 2 completed and 3 pending instances, **When**
   the user edits the recurrence pattern, **Then** only the pending instances
   are affected and completed instances remain in history.

3. **Given** a user is editing a recurrence pattern, **When** they preview the
   changes, **Then** they see a comparison of current vs. new upcoming dates
   before confirming.
```

## Example 3: P3 User Story (Nice to Have)

```markdown
### User Story 3 - Custom Recurrence Patterns (Priority: P3)

A power user needs a recurrence pattern not covered by the standard options,
such as "every 2 weeks on Tuesday and Thursday" or "quarterly on the 15th".
They access an advanced recurrence builder to create custom patterns.

**Why this priority**: Standard daily/weekly/monthly patterns cover 90%+ of use
cases. Custom patterns serve a niche audience of power users with complex
scheduling needs. The feature is fully functional without this, making it a
future enhancement rather than initial release requirement.

**Independent Test**: Use the custom recurrence builder to create "every 2 weeks
on Tuesday", save, and verify that task instances appear on the correct alternating
Tuesdays.

**Acceptance Scenarios**:
1. **Given** a user clicks "Custom pattern" in recurrence options, **When** they
   select "Every 2 weeks" and "Tuesday, Thursday", **Then** they see a preview
   of the next 5 occurrences matching this pattern.

2. **Given** a user has created a custom quarterly pattern, **When** they view
   the recurring task, **Then** the recurrence description shows "Quarterly on
   the 15th" in human-readable format.
```

## Good vs. Bad Comparisons

### User Journey Description

**Good:**
> A user wants to pause their recurring task temporarily without losing the
> pattern. They mark the task as "paused", and no new instances are generated
> until they resume.

**Bad:**
> The system provides a pause functionality that sets the is_active flag to
> false and stops the cron job from generating TaskInstance records.

### Priority Justification

**Good:**
> This is the core value proposition of the feature. Users cannot create any
> recurring tasks without this, making all other stories dependent on it.

**Bad:**
> P1 because it's important and stakeholders want it.

### Independent Test

**Good:**
> Create a daily recurring task, complete today's instance, wait until tomorrow
> (or advance the system date), and verify a new instance appears automatically.

**Bad:**
> Test the recurrence functionality works correctly.

### Acceptance Scenario

**Good:**
> **Given** a user has a weekly recurring task, **When** they click "Skip next
> occurrence", **Then** the next instance is removed and the following week's
> instance becomes the new "next occurrence".

**Bad:**
> **Given** the RecurringTaskService is initialized, **When** skipNext() is
> called with a valid taskId, **Then** the next TaskInstance row is deleted
> and the sequence is recalculated.
