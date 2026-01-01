# Workflow Context: {{feature_id}}

> This file maintains shared state across agents in the specify workflow.
> Each agent reads this before starting and updates it after completing.

## Feature

| Field | Value |
|-------|-------|
| **ID** | {{feature_id}} |
| **Description** | {{original_description}} |
| **Branch** | {{branch_name}} |
| **Created** | {{timestamp}} |
| **Status** | {{status}} |

**Status values**: `scaffolding` → `writing` → `clarifying` → `ready`

## Paths

| Path | Location |
|------|----------|
| Feature Dir | `specs/{{feature_id}}/` |
| Spec File | `specs/{{feature_id}}/spec.md` |
| Checklist | `specs/{{feature_id}}/checklists/requirements.md` |
| Context | `specs/{{feature_id}}/.workflow/context.md` |

## Decisions Log

> Append-only log of decisions made during workflow. Each agent adds entries.

| Timestamp | Agent | Decision | Rationale |
|-----------|-------|----------|-----------|
| | | | |

## Clarifications

### Pending

> Questions awaiting user answers. Spec Writer adds, Supervisor presents to user.

| ID | Location | Question | Options | Priority |
|----|----------|----------|---------|----------|
| | | | | |

**Priority**: `scope` > `security` > `ux` > `technical`

### Resolved

> Answered clarifications. Clarify Agent updates spec and moves here.

| ID | Question | Answer | Applied To |
|----|----------|--------|------------|
| | | | |

## Agent Handoff Notes

> Critical context for the next agent. Updated by each agent before completing.

### From Scaffold Agent
<!-- Branch created, directories initialized, template copied -->

### From Spec Writer Agent
<!-- Sections completed, clarifications identified, assumptions made -->

### From Clarify Agent
<!-- Answers applied, remaining issues, spec quality status -->
