# Cycle Report Format

The Staff Engineer produces a `cycle-report.md` after each cycle execution. The report has two consumption patterns: structured YAML frontmatter for the checkpoint gate (deterministic evaluation) and prose sections for the State Analyst (briefings and carry_forward context).

## Frontmatter Schema

```yaml
---
cycle: 3                    # Cycle number (integer) or "fix" for fix passes
attempt: 1                  # Attempt number within this cycle (1 = first attempt)
tasks_total: 4              # Total tasks in this cycle's task list
tasks_completed: 4          # Tasks marked [x] after execution
files_created:              # New files created during this cycle
  - src/routes/api.ts
  - src/routes/api.test.ts
files_modified:             # Existing files modified during this cycle
  - src/models/user.ts
brownfield_tasks: 1         # Count of tasks with [EXTEND] or [MODIFY] markers
checkpoint_criteria_met: true  # Staff Engineer's self-assessment (checkpoint gate verifies independently)
---
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cycle` | integer or `"fix"` | yes | Cycle number from tasks.md, or `"fix"` for fix passes |
| `attempt` | integer | yes | 1 for first attempt, increments on retry |
| `tasks_total` | integer | yes | Number of tasks in the cycle task list |
| `tasks_completed` | integer | yes | Number of tasks marked `[x]` after execution |
| `files_created` | list of strings | yes | Paths of new files created (empty list if none) |
| `files_modified` | list of strings | yes | Paths of existing files modified (empty list if none) |
| `brownfield_tasks` | integer | yes | Count of tasks with `[EXTEND]` or `[MODIFY]` markers |
| `checkpoint_criteria_met` | boolean | yes | Staff Engineer's assessment of whether checkpoint criteria are satisfied |

## Prose Sections

### Cycle Header

```markdown
## Cycle {N}: {Cycle Title from tasks.md}
```

For fix passes:
```markdown
## Fix Pass: {Summary of failures being addressed}
```

### What Was Done

Describe what was implemented, in enough detail for the State Analyst to understand the state of the codebase. Include:
- Key implementation decisions
- Which tasks required brownfield integration
- Any deviations from the task descriptions (and why)

### Decisions Made

Document decisions that are not obvious from the task descriptions:
- Technology choices within the task's scope
- Pattern choices when multiple valid approaches existed
- Trade-offs made and rationale

### Notes for Next Cycle

Information the next cycle's Staff Engineer dispatch needs to know:
- Files or interfaces that were created/modified that affect future cycles
- Patterns established that should be followed
- Potential conflicts with upcoming tasks
- Improvement opportunities noticed but not acted on (scope discipline)

## Example

```markdown
---
cycle: 3
attempt: 1
tasks_total: 4
tasks_completed: 4
files_created:
  - src/routes/api.ts
  - src/routes/api.test.ts
files_modified:
  - src/models/user.ts
brownfield_tasks: 1
checkpoint_criteria_met: true
---

## Cycle 3: API Route Layer

### What Was Done
Implemented REST endpoints for user CRUD operations. T3.1 wrote failing tests for all 4 endpoints. T3.2-T3.3 implemented the route handlers and middleware. T3.4 extended the existing User model with a `lastLogin` field ([EXTEND] task — followed existing Sequelize patterns).

### Decisions Made
- Chose Express router over Koa because plan.md specifies Express
- Used async/await with try-catch for error handling to match existing patterns in src/middleware/

### Notes for Next Cycle
- The `User` model was extended with `lastLogin` field — C4 should account for this in the auth middleware
- Error handling follows the `AppError` class pattern from src/utils/errors.ts
- API routes are registered in src/routes/index.ts — future cycles adding routes should follow the same pattern
```
