# ADR-005: Decoupled Agents with Protocol Skills

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
| **Duplicated patterns** | Each workflow defines its own input/output conventions |
| **Mixed responsibilities** | Agents handle both domain work AND workflow orchestration |
| **Hard to test** | Testing requires full workflow context |
| **Maintenance burden** | Changing workflow structure requires updating agents |

The question: How should we decouple agents from workflows while maintaining structured communication?

## Decision

Adopt a **Decoupled Agents with Protocol Skills** architecture where:

- **Agents are pure domain experts** - They read context, write their artifact, return structured metadata
- **Protocol skills define communication contracts** - Reusable across all workflows
- **Workflow skills handle orchestration operations** - Supervisors delegate state updates
- **Supervisors own workflow logic** - They use protocols to communicate with any agent

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PROTOCOL SKILLS (shared)                        │
├─────────────────────────────────────────────────────────────────────┤
│ protocol-agent-input     → Base input contract for ALL agents       │
│ protocol-agent-output    → Base output contract for ALL agents      │
│ protocol-clarification   → How ANY agent signals clarifications     │
│ workflow-update-context  → Update context files (any workflow)      │
│ workflow-sync-index      → Sync to index.md (any workflow)          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────────┐
        ▼                           ▼                               ▼
┌───────────────┐           ┌───────────────┐               ┌───────────────┐
│  specify.md   │           │   plan.md     │               │   tasks.md    │
│  (supervisor) │           │  (supervisor) │               │  (supervisor) │
└───────┬───────┘           └───────┬───────┘               └───────┬───────┘
        │                           │                               │
        ▼                           ▼                               ▼
┌───────────────┐           ┌───────────────┐               ┌───────────────┐
│  spec-writer  │           │ plan-research │               │ task-planner  │
│    (agent)    │           │    (agent)    │               │    (agent)    │
└───────────────┘           └───────────────┘               └───────────────┘
```

### Protocol Skills

New skill category following ADR-004 naming conventions:

| Skill | Purpose |
|-------|---------|
| `protocol-agent-input` | Base input contract for all agents |
| `protocol-agent-output` | Base output contract for all agents |
| `protocol-clarification` | Standard format for clarification requests |

### Workflow Skills

| Skill | Purpose |
|-------|---------|
| `workflow-update-context` | Update workflow context files with agent output |
| `workflow-sync-index` | Sync state to workflow index.md |

### Agent Responsibilities (After)

| Responsibility | Before | After |
|----------------|--------|-------|
| Read context files | Agent hardcodes paths | Supervisor provides paths |
| Write domain artifact | Agent writes | Agent writes (unchanged) |
| Return structured data | Ad-hoc JSON | Follows `protocol-agent-output` |
| Update workflow state | Agent updates directly | Supervisor invokes workflow skills |
| Know parent workflow | Agent knows | Agent is agnostic |

### Input/Output Contracts

**Base Input (all agents receive):**
```json
{
  "feature_id": "007-notifications",
  "output_path": "specs/007-notifications/spec.md",
  "context_files": ["path/to/constitution.md", "..."]
}
```

**Base Output (all agents return):**
```json
{
  "success": true,
  "artifact_path": "specs/007-notifications/spec.md",
  "clarifications": [],
  "assumptions": [],
  "decisions": []
}
```

**Extension Pattern:**
Agents extend base contracts with domain-specific fields. Extensions are documented in the agent's `.md` file, not in separate skills.

```yaml
# In spec-writer.md
---
name: spec-writer-agent
protocols: protocol-agent-input, protocol-agent-output, protocol-clarification
skills: authoring-user-stories, authoring-requirements
---

## Input Extensions
| Field | Required | Type |
|-------|----------|------|
| feature_description | yes | string |

## Output Extensions
| Field | Type |
|-------|------|
| requirements_list | string[] |
| user_story_count | number |
```

## Rationale

### Why Protocol Skills (vs alternatives)

| Alternative | Why Not |
|-------------|---------|
| **Contracts in agent files** | Can't be referenced by supervisors; no single source of truth |
| **Agent-specific contract skills** | Not reusable; `contract-spec-writer` only helps one agent |
| **No contracts** | Ad-hoc communication leads to inconsistency and bugs |
| **Protocol skills** | Reusable across all workflows; agents extend as needed |

### Why Minimum Viable Contracts

Contracts define a **floor, not a ceiling**:

- **Required fields** ensure agents always get what they need
- **Optional fields** let supervisors add intelligence based on context
- **Extensions** let agents request domain-specific data

This balances reliability with flexibility.

### Why Agents Write Their Own Artifacts

Agents write their primary artifact (e.g., `spec.md`) because:
- They have the content; shuttling it back adds no value
- Writing is a core capability in Claude Code's agent model
- The artifact is their domain responsibility

Agents do NOT write workflow artifacts (e.g., `index.md`) because:
- Workflow state is the supervisor's responsibility
- Decoupling requires clear boundaries
- Workflow skills encapsulate this logic for reuse

### Alignment with ADR-004

This decision extends ADR-004 (Skill-Augmented Agents) with two new skill categories:

| Category | Purpose | Examples |
|----------|---------|----------|
| `protocol-*` | Communication contracts | agent-input, agent-output, clarification |
| `workflow-*` | Workflow operations | update-context, sync-index |

These follow the same principles: reusable knowledge, progressive disclosure, flat structure with naming conventions.

## Consequences

### Positive

- **Portability** - Agents can be used by any workflow or externally
- **Consistency** - All workflows speak the same protocol language
- **Testability** - Agents can be tested with mock inputs following protocols
- **Maintainability** - Update a protocol once, all workflows benefit
- **Composability** - Mix and match agents across workflows
- **Clear boundaries** - Agents do domain work; supervisors do orchestration

### Negative

- **More skills to maintain** - Protocol and workflow skills add files
- **Migration effort** - Existing agents need refactoring
- **Learning curve** - Contributors must understand protocol pattern

### Neutral

- Agents become simpler (less code) but reference more skills
- Supervisors become slightly more complex (invoke workflow skills)
- Total system complexity remains similar, but better distributed

## Migration Path

| Phase | Action |
|-------|--------|
| 1 | Create `protocol-agent-input` skill |
| 2 | Create `protocol-agent-output` skill |
| 3 | Create `protocol-clarification` skill |
| 4 | Create `workflow-update-context` skill |
| 5 | Create `workflow-sync-index` skill |
| 6 | Refactor `spec-writer.md` as proof of concept |
| 7 | Update `specify.md` to use protocols and workflow skills |
| 8 | Refactor remaining agents (plan-*, task-*) |
| 9 | Update `plan.md` and `tasks.md` |

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
```

### After (spec-writer.md)

```markdown
## Output

Return structured JSON following `protocol-agent-output`:

{
  "success": true,
  "artifact_path": "{output_path}",
  "clarifications": [...],
  "requirements_list": ["FR-001", "FR-002"],
  "user_story_count": 3
}

Note: Workflow state updates are handled by the supervisor
using workflow skills. This agent is workflow-agnostic.
```

### After (specify.md)

```markdown
## A2: Write Specification

1. Spawn spec-writer agent with protocol-compliant input
2. Receive protocol-compliant output
3. Invoke `workflow-update-context` skill with output
4. Invoke `workflow-sync-index` skill with output
5. Proceed to validation
```

## Related

- [ADR-001: Multi-Agent Architecture](./001-multi-agent-architecture.md)
- [ADR-004: Skill-Augmented Agents](./004-skill-augmented-agents.md)
- [Agent Skills Documentation](../agent-skills-documentation.md)
