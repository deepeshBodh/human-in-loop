---
name: strategy-implementation
description: Implementation-workflow patterns (cycle sequencing, execute-then-verify, targeted retry, escalation) consumed by the State Analyst alongside strategy-core for targeted Supervisor briefings.
---

# Strategy: Implementation

Workflow-specific patterns for the implementation workflow. Consumed by the State Analyst alongside `strategy-core` to produce targeted Supervisor briefings.

## Goal

Complete all implementation cycles with all gates passing. Success: `final-validation` gate verdict `ready` and `implementation-complete` milestone `achieved`.

## Success Criteria

- All tasks in `tasks.md` marked `[x]`
- `final-validation` gate verdict: `ready`
- `implementation-complete` milestone: `achieved`

## Patterns

### Cycle Sequencing

Foundation cycles execute sequentially (C1 before C2 before C3). Feature cycles begin only after all foundation cycles complete. The Analyst determines the current cycle by reading `tasks.md` checkboxes — the first cycle with unchecked tasks is the current cycle.

**Rationale**: Foundation cycles establish shared infrastructure that feature cycles depend on. Executing them out of order creates cascading failures that waste tokens on retry.

### Execute-then-Verify

Every `execute-cycle` node MUST be followed by a `verify-cycle` node within the same pass. Never skip verification, even when the cycle report claims all tasks passed. The testing-agent runs quality gates (lint, build, tests) independently.

**Rationale**: Self-reported success from the Staff Engineer is unreliable for the same reason self-review is unreliable in specification — systematic blind spots. Independent verification catches what the implementer cannot see in their own work.

### Targeted Retry

On checkpoint failure, the next `execute-cycle` dispatch focuses on the specific failures from the checkpoint report. The Staff Engineer traces failures to responsible tasks, re-opens only those tasks, and fixes them. Full re-implementation of the cycle wastes tokens on working code.

**Rationale**: Most checkpoint failures affect 1-2 tasks, not the entire cycle. Selective rework converges faster and avoids introducing new issues in previously-working code.

### Escalate Before Stall

After 3 retry attempts on a cycle (or 3 fix passes after final-validation), escalate to the user rather than continuing to retry. Include the checkpoint/validation report so the user has full context.

**Rationale**: 3 failed attempts signal a structural problem that more attempts will not resolve — missing context, contradictory requirements, or environmental issues. User intervention breaks the loop.

### Fix Pass Scoping

A fix pass after final-validation failure is scoped to the specific failures in the validation report. It is NOT a refactoring opportunity, a chance to improve code quality, or a license to make sweeping changes. The Staff Engineer addresses exactly what failed.

**Rationale**: Unconstrained fix passes can introduce more failures than they resolve. Tight scoping to reported failures maintains convergence toward completion.

## Anti-Patterns

- **Skip verification**: Running execute-cycle without follow-up verify-cycle — hides failures until final-validation
- **Full re-implementation on retry**: Re-doing all cycle tasks when checkpoint fails — wastes tokens on working code and risks new regressions
- **Continue past 3 retries**: Silently continuing retry loops instead of escalating — burns tokens without convergence
- **Premature final-validation**: Running final-validation before all cycles complete — will always fail, wastes a pass
- **Fix pass as refactoring**: Using fix passes to improve code beyond what the validation report requires — scope creep that risks new failures

## Guardrails

- All tasks in `tasks.md` must be `[x]` before final-validation runs (INV-002 analog for implement)
- Every execute-cycle must be followed by verify-cycle in the same pass (INV-003)
- Max 3 retry attempts per cycle or fix pass before mandatory user escalation (INV-004)
