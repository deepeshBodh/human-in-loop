---
name: strategy-implementation
description: This skill MUST be invoked when the user says "implementation strategy", "cycle sequencing", or "implement workflow patterns". SHOULD also invoke when user mentions "execute-then-verify", "targeted retry", "fix pass", or "implementation escalation". Provides implementation-workflow patterns consumed alongside strategy-core for targeted briefings.
---

# Strategy: Implementation

## Overview

Workflow-specific patterns for implementation workflows. Provides heuristics for cycle sequencing, execute-then-verify pairing, targeted retry, and escalation. Consumed alongside `humaninloop:strategy-core` to produce targeted briefings.

## When to Use

- Producing briefings for implementation workflow passes
- Determining cycle execution order (foundation vs feature)
- Deciding whether to retry, fix, or escalate after failures
- Evaluating whether verification should follow execution
- Assessing convergence signals across implementation passes

## When NOT to Use

- **Specification workflows** — Use `humaninloop:strategy-specification` instead
- **Graph operations** — Use `hil-dag` MCP tools instead
- **Executing implementation tasks** — Use `humaninloop:executing-tdd-cycle` instead
- **Running quality gates** — Use `humaninloop:testing-end-user` instead

## Goal

Complete all implementation cycles with all gates passing. Success: final-validation gate verdict `ready` and implementation-complete milestone `achieved`.

## Success Criteria

- All tasks in `tasks.md` marked `[x]`
- Final-validation gate verdict: `ready`
- Implementation-complete milestone: `achieved`

## Core Patterns

### Cycle Sequencing

Foundation cycles execute sequentially (C1 before C2 before C3). Feature cycles begin only after all foundation cycles complete. Determine the current cycle by reading `tasks.md` checkboxes — the first cycle with unchecked tasks is the current cycle.

**Rationale**: Foundation cycles establish shared infrastructure that feature cycles depend on. Executing them out of order creates cascading failures that waste tokens on retry.

### Execute-then-Verify

Every execution node MUST be followed by a verification node within the same pass. Never skip verification, even when the cycle report claims all tasks passed. Quality gates (lint, build, tests) run independently of the implementer.

**Rationale**: Self-reported success is unreliable for the same reason self-review is unreliable in specification — systematic blind spots. Independent verification catches what the implementer cannot see in their own work.

### Targeted Retry

On checkpoint failure, the next execution dispatch focuses on the specific failures from the checkpoint report. Trace failures to responsible tasks, re-open only those tasks, and fix them. Full re-implementation of the cycle wastes tokens on working code.

**Rationale**: Most checkpoint failures affect 1-2 tasks, not the entire cycle. Selective rework converges faster and avoids introducing new issues in previously-working code.

### Escalate Before Stall

After 3 retry attempts on a cycle (or 3 fix passes after final-validation), escalate to the user rather than continuing to retry. Include the checkpoint/validation report so the user has full context.

**Rationale**: 3 failed attempts signal a structural problem that more attempts will not resolve — missing context, contradictory requirements, or environmental issues. User intervention breaks the loop.

### Fix Pass Scoping

A fix pass after validation failure is scoped to the specific failures in the validation report. It is NOT a refactoring opportunity, a chance to improve code quality, or a license to make sweeping changes. Address exactly what failed.

**Rationale**: Unconstrained fix passes can introduce more failures than they resolve. Tight scoping to reported failures maintains convergence toward completion.

## Guardrails

- All tasks in `tasks.md` must be `[x]` before final-validation runs
- Every execution node must be followed by a verification node in the same pass
- Max 3 retry attempts per cycle or fix pass before mandatory user escalation

## Common Mistakes

### Skipping Verification After Execution
Running an execution cycle without follow-up verification — hides failures until final-validation when they are more expensive to fix.

### Full Re-Implementation on Retry
Re-doing all cycle tasks when a checkpoint fails. Most failures affect 1-2 tasks. Selective rework converges faster and avoids regressions in working code.

### Continuing Past 3 Retries
Silently continuing retry loops instead of escalating. Burns tokens without convergence. 3 failures signal a structural problem that needs human intervention.

### Premature Final-Validation
Running final-validation before all cycles complete. Will always fail because unchecked tasks remain. Wastes a pass.

### Using Fix Passes for Refactoring
Expanding fix pass scope beyond what the validation report requires. Scope creep during fix passes risks introducing new failures while resolving old ones.
