# ADR-005: Decoupled Agents Architecture

**Status:** Proposed
**Date:** 2026-01-03

## Context

The humaninloop plugin uses specialized agents (ADR-001) that are currently tightly coupled to their parent workflows. For example, `spec-writer.md` contains:

1. **Workflow-specific file paths** - Hardcoded references to `index.md`, `specify-context.md`
2. **Workflow artifact updates** - Logic to update workflow state files
3. **Workflow-specific output** - Fields like `specify_context_updated`, `index_synced`

This coupling creates several problems:

| Problem | Impact |
|---------|--------|
| **Non-portable agents** | `spec-writer` can only be used within `specify.md` workflow |
| **Mixed responsibilities** | Agents handle both domain work AND workflow orchestration |
| **Hard to test** | Testing requires full workflow context |
| **Maintenance burden** | Changing workflow structure requires updating agents |

The question: How should we decouple agents from workflows?

## Decision

Adopt a **Decoupled Agents Architecture** with these principles:

1. **Agents are pure domain experts** - They have domain knowledge, not workflow knowledge
2. **Supervisors communicate via natural language** - No rigid schemas or protocols
3. **Artifacts are self-describing** - Agents read their input from artifacts, not supervisor prompts
4. **Artifact chain** - Each agent's output becomes the next agent's input

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ARTIFACT CHAIN                                     │
│                                                                             │
│   context.md ──→ spec.md ──→ research.md ──→ plan.md ──→ tasks.md         │
│        │              │            │             │            │             │
│        ▼              ▼            ▼             ▼            ▼             │
│   spec-writer   plan-research  plan-domain  plan-contract  task-gen        │
└─────────────────────────────────────────────────────────────────────────────┘

Supervisors orchestrate, agents transform artifacts:

┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  specify.md   │         │   plan.md     │         │   tasks.md    │
│  (supervisor) │         │  (supervisor) │         │  (supervisor) │
│               │         │               │         │               │
│ • Points agent│         │ • Points agent│         │ • Points agent│
│   to artifact │         │   to artifact │         │   to artifact │
│ • Receives    │         │ • Receives    │         │ • Receives    │
│   prose report│         │   prose report│         │   prose report│
│ • Updates     │         │ • Updates     │         │ • Updates     │
│   workflow    │         │   workflow    │         │   workflow    │
│   state       │         │   state       │         │   state       │
└───────────────┘         └───────────────┘         └───────────────┘
```

### Communication Design

#### Supervisor → Agent (Natural Language)

Supervisors spawn agents with simple, natural language prompts:

```
Work on the feature at specs/007-push-notifications/

Read the context.md in that directory for feature context and requirements.
Write the specification to spec.md in the same directory.
```

The supervisor does NOT:
- Specify which skills to use (agent knows its own skills)
- Dictate output format (agent knows its domain)
- Pass feature description (artifact contains it)

#### Agent Input (Self-Describing Artifacts)

Agents read their context from artifacts, not supervisor prompts. The context file is the handoff artifact:

**`specs/007-push-notifications/context.md`**

```markdown
---
feature_id: "007-push-notifications"
title: "Push Notifications for Task Reminders"
created: 2026-01-03
status: initialized
---

# Feature Request

Push notifications for task reminders. Users should receive push notifications
when tasks are due. Mobile and desktop support needed.

## Context Files

Read these for project context:
- `.humaninloop/memory/constitution.md` - Project standards and conventions
- `.humaninloop/memory/tech-stack.md` - Technical constraints

## User Notes

> "I want users to get notified before their tasks are due. Maybe 15 minutes
> before? Also need to work on both phone and laptop."

— From user conversation, 2026-01-03

## Output

Write specification to: `spec.md` (same directory)
```

#### Agent Output (Structured Prose)

Agents report back using structured prose with consistent headings. This is **domain knowledge**—the agent knows what's relevant to report about its work:

```markdown
## What I Created

Wrote specification to `specs/007-push-notifications/spec.md`:
- 5 user stories (3 P1, 2 P2)
- 12 functional requirements (FR-001 through FR-012)
- 4 edge cases identified

## Clarifications Needed

1. **OAuth Providers** (FR-003): Which providers should be supported?
   - Options: Google only, Google + GitHub, All major providers
   - Impact: Scope

2. **Notification Timing** (FR-007): How far in advance to notify?
   - Options: 15 minutes, 1 hour, User-configurable
   - Impact: UX

## Assumptions Made

- Firebase Cloud Messaging for cross-platform delivery (based on tech-stack.md)
- Notifications are opt-in by default
- No SMS fallback unless explicitly requested
```

The supervisor parses this prose to update workflow state.

### Domain Knowledge vs Workflow Knowledge

Agents retain **domain knowledge** but shed **workflow knowledge**:

| Type | Example | Where It Lives |
|------|---------|----------------|
| **Domain knowledge** | "Spec writing produces user stories, requirements, clarifications" | Agent |
| **Domain knowledge** | "I should report what I created, questions I have, assumptions I made" | Agent |
| **Workflow knowledge** | "Update index.md Document Availability Matrix" | Supervisor |
| **Workflow knowledge** | "Set specify-context.md status to 'writing'" | Supervisor |
| **Workflow knowledge** | "Return JSON with `specify_context_updated: true`" | Supervisor |

### Artifact Chain

Each agent's output becomes the next agent's input. No separate context files needed after the first:

| Agent | Reads | Writes |
|-------|-------|--------|
| context-agent | User description | `context.md` |
| spec-writer | `context.md` | `spec.md` |
| plan-research | `spec.md` | `research.md` |
| plan-domain | `spec.md` + `research.md` | `data-model.md` |
| plan-contract | `data-model.md` | `contracts/` |
| task-planner | `plan.md` | `task-mapping.md` |
| task-generator | `task-mapping.md` | `tasks.md` |

The artifacts are self-describing—each contains enough context for the next agent to work.

## Rationale

### Why Natural Language Communication

- **No coupling to schemas** - Supervisors and agents can evolve independently
- **Human-readable** - Easy to debug and understand what happened
- **Flexible** - Different supervisors can ask for different things without agent changes

### Why Self-Describing Artifacts

- **Single source of truth** - Feature context lives in the artifact, not duplicated in prompts
- **Testable** - Create a context file, invoke agent, verify output—no workflow needed
- **Reusable** - Anyone can invoke an agent by pointing it at an artifact

### Why Structured Prose Output

- **Domain-appropriate** - Agents report what's relevant to their domain
- **Parseable** - Consistent headings let supervisors find information
- **Not rigid** - Agents can add sections as needed without breaking contracts

### Why Agents Keep Domain Knowledge

Domain knowledge is the agent's expertise:
- A spec-writer knows specs have requirements, user stories, clarifications
- A plan-researcher knows research surfaces technical unknowns and options
- This is portable—useful regardless of which workflow invokes the agent

Workflow knowledge is orchestration:
- Which file to update next
- What status to set
- How to sync state across workflows
- This belongs to the supervisor

## Consequences

### Positive

- **Testability** - Point agent at artifact, verify output. No workflow context needed.
- **Portability** - Agents can be reused across workflows or standalone
- **Clarity** - Clean separation between domain work and orchestration
- **Simplicity** - Agents become shorter (remove workflow update logic)

### Negative

- **Supervisors grow** - Supervisors handle all state updates and prose parsing
- **Migration effort** - Existing agents need refactoring
- **Prose parsing** - Supervisors need to extract structure from prose (but this is tractable with consistent headings)

### Neutral

- Agents become simpler, supervisors become more explicit
- Total complexity shifts but doesn't increase
- Artifacts become more important as the communication medium

## Migration Path

| Phase | Action |
|-------|--------|
| 1 | Define context file format for specify workflow |
| 2 | Refactor `spec-writer.md`: remove Phase 4 (workflow updates), update output to structured prose |
| 3 | Update `specify.md`: parse prose output, handle all state updates |
| 4 | Test spec-writer in isolation with mock context file |
| 5 | Test full specify workflow end-to-end |
| 6 | Refactor remaining agents (plan-*, task-*) following same pattern |

## Example: Before and After

### Before (spec-writer.md)

```markdown
## Phase 4: Artifact Updates

**Update specify-context.md:**
1. Set status to `writing`
2. Set current_agent to `spec-writer`
3. Update Specification Progress table
...

**Sync to index.md:**
1. Update Document Availability Matrix
2. Update Workflow Status Table
3. Initialize Priority Loop State
...

## Output Format

Return JSON:
{
  "success": true,
  "specify_context_updated": true,
  "index_synced": true,
  ...
}
```

### After (spec-writer.md)

```markdown
## Input

Read the context artifact from the directory you're pointed to.
The context file contains:
- Feature description and context
- Context files to read for project standards
- Where to write your output

## Your Work

Write a specification following your domain expertise:
- User stories with priorities
- Functional requirements
- Edge cases
- Success criteria

Use your skills (authoring-user-stories, authoring-requirements) for guidance.

## Output

Report back with structured prose:

### What I Created
[Summary of artifact written, counts of stories/requirements]

### Clarifications Needed
[Questions that need user input before proceeding]

### Assumptions Made
[Decisions you made when the spec was ambiguous]

You are workflow-agnostic. The supervisor handles all state updates.
```

### After (specify.md supervisor)

```markdown
## A2: Write Specification

1. Spawn spec-writer agent:
   "Work on the feature at {feature_dir}/. Read context.md for context."

2. Receive prose report from agent

3. Parse report:
   - Extract clarification count from "Clarifications Needed" section
   - Extract requirement count from "What I Created" section

4. Update workflow state:
   - Set specify-context.md status based on clarification count
   - Update index.md Document Availability Matrix
   - Log decisions from "Assumptions Made" section

5. Route next step:
   - If clarifications needed → clarify phase
   - If no clarifications → validation phase
```

## Future Considerations

If patterns emerge across agents (common headings, common information), we may formalize these as conventions or templates in a future ADR. This decision intentionally keeps things simple and natural.

## Related

- [ADR-001: Multi-Agent Architecture](./001-multi-agent-architecture.md)
- [ADR-004: Skill-Augmented Agents](./004-skill-augmented-agents.md)
