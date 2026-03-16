---
name: executing-tdd-cycle
description: This skill MUST be invoked when implementing cycle task lists via TDD red/green/refactor discipline. SHOULD also invoke when encountering tasks with `[EXTEND]`/`[MODIFY]` markers, cycle-report generation, or retry handling after checkpoint failure.
---

# Executing TDD Cycles

## Overview

Transform a cycle task list into implemented code via strict red/green/refactor discipline. Parse tasks from `tasks.md`, write failing tests first, implement code to pass them, refactor, mark tasks complete, and produce a structured `cycle-report.md`. This skill governs both normal cycle execution and retry/fix modes.

**Violating the letter of the rules is violating the spirit of the rules.**

TDD discipline exists to catch failures before they compound. Every shortcut in this process is a regression waiting to happen.

## When to Use

- Executing a cycle's task list from `tasks.md`
- Retry after checkpoint failure (targeted rework)
- Fix mode after final-validation failure (unconstrained by cycle boundaries)
- Any task with `[EXTEND]` or `[MODIFY]` markers (invoke `brownfield-integration` skill alongside)
- Writing cycle-report.md after cycle completion

## When NOT to Use

- Running quality gates (lint, build, test suite) — that is the testing-agent's responsibility
- Parsing or evaluating checkpoint/validation reports — that is the State Analyst's responsibility
- Deciding which cycle to execute next — that is determined by the Analyst briefing
- Modifying DAG state or pass lifecycle — that belongs to the DAG Assembler

## Core Process

### Cycle Execution Sequence

Execute in strict order. No skipping steps. No reordering.

**1. Parse Cycle Tasks**

Extract the task list for the current cycle from `tasks.md`. See [references/TASK-PARSING.md](references/TASK-PARSING.md) for parsing rules.

For each task, extract:
- Task ID (`T{N}.{X}`)
- Description
- File path(s) in backticks
- `[EXTEND]` or `[MODIFY]` markers
- Sub-bullet details

**2. Red Phase — Write Failing Tests**

For each task that specifies a test:
1. Write the test file at the specified path
2. Run the test to verify it **fails**
3. Verify the failure reason matches expectations (not a syntax error, import error, or wrong assertion)
4. If the test passes without implementation, the test is not testing what you think — rewrite it

**3. Green Phase — Implement Code**

For each implementation task:
1. Write the minimum code to make the failing test pass
2. Run the test to verify it **passes**
3. Do not add features, abstractions, or optimizations the task did not request
4. For `[EXTEND]` tasks: read the existing file first, follow existing patterns (invoke `brownfield-integration` skill)
5. For `[MODIFY]` tasks: read the existing file first, change only what the task specifies (invoke `brownfield-integration` skill)

**4. Refactor Phase**

After tests pass:
1. Remove duplication introduced in this cycle only
2. Improve names if unclear
3. Do NOT refactor code from previous cycles
4. Do NOT add abstractions "for the future"
5. Re-run tests after refactoring to confirm they still pass

**5. Mark Tasks Complete**

Update `tasks.md`: change `- [ ]` to `- [x]` for each completed task in this cycle.

**6. Write Cycle Report**

Produce `cycle-report.md` following the format in [references/CYCLE-REPORT-FORMAT.md](references/CYCLE-REPORT-FORMAT.md).

### Progress Tracking

- Mark each task `[x]` in `tasks.md` immediately after completing it
- Write `cycle-report.md` with YAML frontmatter and prose sections
- Frontmatter provides structured data for the checkpoint gate
- Prose sections provide context for the State Analyst and carry_forward

### Retry Handling

When dispatched after a checkpoint failure:

1. Read the checkpoint report to identify specific failures
2. Trace each failure to the responsible task(s)
3. Re-open failed tasks: change `- [x]` back to `- [ ]` in `tasks.md`
4. Execute only the re-opened tasks through the red/green/refactor cycle
5. Do NOT re-implement tasks that passed — they are done
6. Write a new `cycle-report.md` with updated attempt number

### Fix Mode

When dispatched after final-validation failure:

1. Read the final-validation report to identify specific failures
2. Fix each failure — you are NOT constrained by cycle boundaries
3. May touch files from any cycle as needed to resolve failures
4. Scope strictly to reported failures — this is not a refactoring opportunity
5. Write `cycle-report.md` with `cycle: fix` in frontmatter

## Red Flags — STOP and Restart Properly

If any of these thoughts arise, STOP immediately:

- "The test already passes so I'll skip writing it first"
- "I'll write all the code first and tests after"
- "This task is trivial, no test needed"
- "I'll refactor this existing code while I'm here"
- "The task says EXTEND but I need to rewrite this"
- "I'll add this helper/utility that will be useful later"
- "The checkpoint will catch it if something's wrong"
- "I know this works from the previous cycle"

**All of these mean:** Rationalization in progress. Return to the execution sequence. Follow every step.

See [references/TDD-ANTI-RATIONALIZATION.md](references/TDD-ANTI-RATIONALIZATION.md) for the full rationalization table.

## Common Mistakes

### Mistake: Writing Tests After Implementation

**What goes wrong:** Tests become retroactive justification. They pass because they were written to match the code, not because the code satisfies the requirement.

**Fix:** Always write the test first. Run it. Verify it fails for the right reason. Then implement.

### Mistake: Full Cycle Re-Implementation on Retry

**What goes wrong:** Working code gets rewritten, introducing new bugs. Token budget wasted on already-complete tasks.

**Fix:** Trace failures to specific tasks. Re-open only those tasks. Leave passing code untouched.

### Mistake: Scope Creep During Refactor Phase

**What goes wrong:** "While I'm here" changes accumulate. New bugs appear in code that was working. Cycle report doesn't reflect actual changes.

**Fix:** Refactor phase is limited to code introduced in this cycle. Note improvement opportunities in the cycle report's "Notes for Next Cycle" section.

### Mistake: Skipping Failure Reason Verification

**What goes wrong:** Test fails due to syntax error or wrong import, not because the assertion caught a missing implementation. Green phase "passes" the test by fixing the syntax, not by implementing the feature.

**Fix:** After writing a failing test, verify the failure message matches your expectation. A `ModuleNotFoundError` is not a meaningful test failure.

## Reference Files

- [references/CYCLE-REPORT-FORMAT.md](references/CYCLE-REPORT-FORMAT.md) — Structured YAML frontmatter schema and prose sections
- [references/TASK-PARSING.md](references/TASK-PARSING.md) — Task pattern extraction, file paths, markers
- [references/TDD-ANTI-RATIONALIZATION.md](references/TDD-ANTI-RATIONALIZATION.md) — Common shortcuts and why they fail
