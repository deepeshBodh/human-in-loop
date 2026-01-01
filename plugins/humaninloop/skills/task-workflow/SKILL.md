---
name: task-workflow
description: Reference manual for the task workflow phases (Mapping, Generation). Provides shared patterns for context loading, brownfield handling, and phase-specific procedures. Referenced by task-builder and task-validator agents.
---

# Task Workflow Skill

## Purpose

Comprehensive guidance for executing the multi-phase task workflow that transforms plan artifacts into implementation tasks. This skill provides shared patterns across all task phases and phase-specific procedures.

## Task Workflow Overview

```
Phase T1: Mapping    -> task-mapping.md (story-to-component mappings)
    |
Phase T2: Generation -> tasks.md (implementation task list)
    |
Validation           -> Validate after each phase
```

## Quick Reference

| Task | Reference |
|------|-----------|
| Load context files | [CONTEXT.md](CONTEXT.md) |
| Handle brownfield projects | [BROWNFIELD.md](BROWNFIELD.md) |
| Phase T1: Story mapping | [MAPPING.md](MAPPING.md) |
| Phase T2: Task generation | [TASKS.md](TASKS.md) |
| Validation procedures | [VALIDATION.md](VALIDATION.md) |

## Shared Artifacts

| Artifact | Purpose | Created By |
|----------|---------|------------|
| `tasks-context.md` | Workflow state, handoffs | All phases |
| `index.md` | Cross-workflow sync | All phases |
| `task-mapping.md` | Story-component mappings | Phase T1 |
| `tasks.md` | Implementation task list | Phase T2 |

## Input Documents

| Document | Purpose | Required |
|----------|---------|----------|
| `spec.md` | User stories, requirements | Yes |
| `plan.md` | Tech stack, decisions | Yes |
| `data-model.md` | Entity definitions | Optional |
| `contracts/` | API endpoints | Optional |
| `research.md` | Technical decisions | Optional |
| `codebase-inventory.json` | Brownfield context | If exists |

## Common Constraints

Both task-builder and task-validator share these constraints:
- **No user interaction** - Supervisor handles communication
- **Autonomous execution** - Complete phase without external input
- **Context sync required** - Update tasks-context.md and index.md
- **Brownfield awareness** - Apply markers for existing code
- **Traceability** - Link tasks to user stories (US#) and requirements (FR-xxx)
