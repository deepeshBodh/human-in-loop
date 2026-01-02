---
name: specification-workflow-lifecycle
description: Domain knowledge for iterative specification workflows. Defines 3-phase architecture (Initial -> Priority Loop -> Completion), 4 termination conditions, resume/restart patterns, and artifact application strategies. Establishes iteration caps (max 10 iterations, 3 clarifications/iteration) and stale detection thresholds specific to specification workflows.
---

# Specification Workflow Lifecycle Skill

## Purpose

Comprehensive domain knowledge for orchestrating the specification workflow lifecycle. This skill defines the phases, state transitions, termination conditions, and recovery patterns that ensure specifications reach completion through iterative refinement.

## Quick Reference

| Task | Reference |
|------|-----------|
| Understand workflow phases | [PHASES.md](PHASES.md) |
| Check termination conditions | [TERMINATION.md](TERMINATION.md) |
| Handle resume/recovery | [RECOVERY.md](RECOVERY.md) |
| Manage state transitions | [STATE.md](STATE.md) |

## Workflow Architecture

```
+---------------------------------------------------------------------+
|                    SPECIFICATION WORKFLOW                             |
+---------------------------------------------------------------------+
|                                                                       |
|  PHASE A: Initial Specification                                       |
|  +-- A1: Scaffold (create branch, directories)                       |
|  +-- A2: Spec Writer [create] (write spec content)                   |
|  +-- A3: Validator (validate with spec-checks.md)                    |
|  +-- A4: Checklist Agent (generate requirements checklist)           |
|  +-- A5: Gap Classifier (classify gaps into questions)               |
|                                                                       |
|  PHASE B: Priority Loop                                               |
|  WHILE (critical + important > 0) AND (iteration < 10):             |
|  +-- B1: Present gaps via AskUserQuestion                            |
|  +-- B2: Spec Writer [update] (apply answers to spec)                |
|  +-- B3: Validator (re-validate spec)                                |
|  +-- B4: Check termination conditions                                 |
|  +-- B5: Update index.md state                                        |
|                                                                       |
|  PHASE C: Completion                                                  |
|  +-- C1: Log deferred minor gaps                                     |
|  +-- C2: Finalize traceability matrix                                |
|  +-- C3: Generate quality report                                     |
|  +-- C4: Update final state                                          |
|                                                                       |
+---------------------------------------------------------------------+
```

## Key Constraints

| Constraint | Value | Rationale |
|------------|-------|-----------|
| Max Iterations | 10 | Prevent infinite loops |
| Max Clarifications/Iteration | 3 | Reduce user fatigue |
| Stale Threshold | 3 iterations | Detect stuck gaps |
| Resume Support | Yes | Enable crash recovery |

## State Machine

```
+-------------+     +---------------+     +-----------+
| not_started | --> | scaffolding   | --> | spec_     |
+-------------+     +---------------+     | writing   |
                                          +-----------+
                                               |
                    +---------------+          v
                    | completed     | <-- +-----------+
                    +---------------+     | validating|
                          ^               +-----------+
                          |                    |
                    +---------------+          v
                    | terminated    |     +-----------+
                    +---------------+     | clarifying|
                          ^               +-----------+
                          |                    |
                          +--------------------+
```

## Termination Conditions Summary

| Condition | Trigger | Outcome |
|-----------|---------|---------|
| Success | Zero Critical + Important gaps | Proceed to completion |
| Max Iterations | iteration >= 10 | Log remaining gaps, complete |
| Stale Detection | Same gaps for 3 iterations | Escalate to user |
| No Progress | resolved_this_iteration == 0 | Ask user to decide |

## Stateless Agent Pattern

> **Core Principle**: Agents are stateless functions. The workflow owns all state.

```
Agents READ files for context
Agents RETURN artifacts and state_updates
Workflow WRITES files and applies state updates
```

This ensures:
- Crash recovery is possible (state in files)
- Agents can be retried without side effects
- State changes are auditable

## When to Load Additional Files

- **Planning workflow phases?** Load [PHASES.md](PHASES.md)
- **Checking if workflow should end?** Load [TERMINATION.md](TERMINATION.md)
- **Resuming from crash?** Load [RECOVERY.md](RECOVERY.md)
- **Managing loop state?** Load [STATE.md](STATE.md)
