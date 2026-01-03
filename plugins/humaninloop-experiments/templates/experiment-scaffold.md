---
type: experiment
experiment_id: exp-YYYYMMDD-HHMMSS
iteration: 1
created: YYYY-MM-DDTHH:MM:SS
status: scaffolded
---

# Experiment Request

## Hypothesis

[Describe what you're testing and what you expect to happen]

Example:
> Decoupled agents with artifact chains will reduce agent complexity by 40%
> because workflow logic is removed from agent definitions.

## Goals

- [ ] Primary goal
- [ ] Secondary goal
- [ ] Success criteria

## Context Files

- `.humaninloop/memory/constitution.md` - Project standards (if exists)
- [List any relevant existing artifacts]

## Variables

**Changing (Independent)**:
- [What you're modifying]

**Constant (Control)**:
- [What stays the same]

## Constraints

- [Any limitations or requirements]
- [Time/scope boundaries]

## Supervisor Instructions

[Instructions for the experiment-runner agent]

Write results to: `result.md` (same directory)

Report back with structured prose:
- `## What I Created` - Experiment executed, key findings
- `## Results Summary` - Pass/Fail with evidence
- `## Clarifications Needed` - Questions requiring user input (if any)
- `## Assumptions Made` - Decisions made when scope was ambiguous
- `## Recommendations` - Suggested next steps

## Clarification Log

[Empty on first iteration - supervisor appends Q&A rounds here]
