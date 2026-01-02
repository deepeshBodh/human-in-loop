# ADR-007: Workflow Primitives Skill Architecture

**Status**: Proposed
**Date**: 2026-01-02
**Decision**: Create a layered skill architecture in `humaninloop-core` that standardizes state management, artifact generation, and agent message protocol for current and future plugins

---

## Problem Statement

The humaninloop plugin ecosystem lacks standardized patterns for:
1. **State management**: Each workflow reinvents how to track workflow state (index files, context, progress)
2. **Artifact generation**: Agents have inconsistent approaches to returning file content and state updates
3. **Agent message protocol**: No standard for how agents receive input or communicate handoffs

Currently, humaninloop-specs has mature implementations of these patterns, but they're embedded in workflow-specific code. New plugins must reverse-engineer these patterns or invent their own, leading to inconsistency and slower plugin development.

## Context & Constraints

- **ADR-006**: Established `humaninloop-core` as the home for shared skills and agents
- **ADR-005**: Hexagonal architecture with skills as atomic domain knowledge
- **Proven patterns**: humaninloop-specs has battle-tested state management, artifact generation, and messaging patterns
- **Goal**: Accelerate new plugin development by providing reusable primitives
- **Constraint**: Claude agents can't be "enforced" at runtime—patterns must be documented and templated, not validated

## Decision

### Layered Skill Architecture

Create a base skill plus domain-aligned extensions:

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `workflow-primitives` | Essential patterns every workflow agent needs | Always |
| `validation-loops` | Iterative quality checks with gap tracking | Workflows with validation (specify, plan) |
| `clarification-protocol` | Structured user clarifications | Workflows gathering user input |
| `resume-recovery` | State machine for workflow continuation | Long-running workflows |

### Core Skill Contents (workflow-primitives)

| Pattern | Purpose |
|---------|---------|
| State registry structure | Unified index.md with metadata, status, document availability |
| Artifact return format | `{ artifacts, state_updates, next_recommendation }` |
| Agent input envelope | Standard input structure (`context`, `paths`, `task`) |
| Handoff notes | Context passing between agents |
| Decisions log | Audit trail of agent decisions |

### Consumption Model: Template + Schema

- **Templates**: Copyable starting points (index-template.md, artifact-schema.md)
- **Schemas**: Documented structures for validation and reference
- **Examples**: Filled-in examples showing patterns in use

Agents declare `skills: [workflow-primitives]` and use templates as starting points.

### Agent Input Envelope

All agents receive a standard input structure:

```json
{
  "context": {
    "feature_id": "005-user-auth",
    "workflow": "specify|plan|tasks",
    "iteration": 1,
    "plugin": "humaninloop-specs"
  },
  "paths": {
    "index": "specs/005-user-auth/.workflow/index.md",
    "spec": "specs/005-user-auth/spec.md",
    "constitution": ".humaninloop/memory/constitution.md"
  },
  "task": {
    "mode": "create|update|validate|apply_answers",
    "params": {}
  }
}
```

### Artifact Return Format

All agents return a standard output structure:

```json
{
  "success": true,
  "artifacts": [
    {
      "path": "relative/path/to/file.md",
      "operation": "create|overwrite",
      "content": "full file content"
    }
  ],
  "state_updates": {
    "workflow_status": { "current_agent": "...", "status": "..." },
    "document_availability": { "spec.md": "present" },
    "decisions_log": [{ "timestamp": "...", "agent": "...", "decision": "...", "rationale": "..." }],
    "handoff_notes": { "from": "...", "notes": ["..."] }
  },
  "next_recommendation": "proceed|retry|escalate"
}
```

### State Registry (index.md) Core Sections

```markdown
# Feature Index: {feature_id}

## Metadata
- **Feature ID**: {feature_id}
- **Branch**: {branch_name}
- **Created**: {timestamp}
- **Workflow**: {workflow_name}

## Document Availability
| Document | Status |
|----------|--------|
| spec.md | absent/present |

## Workflow Status
- **Current Phase**: {phase}
- **Current Agent**: {agent}
- **Status**: not_started/in_progress/completed/blocked

## Decisions Log
| Timestamp | Agent | Decision | Rationale |
|-----------|-------|----------|-----------|

## Agent Handoff Notes
### From {agent_name}
- {context_item}
- Ready for: {next_agent}
```

## Architecture

```
plugins/humaninloop-core/
└── skills/
    ├── workflow-primitives/          # BASE SKILL
    │   ├── SKILL.md                  # Patterns documentation
    │   ├── templates/
    │   │   ├── index-template.md     # State registry skeleton
    │   │   └── artifact-schema.md    # Return format documentation
    │   └── examples/
    │       ├── minimal-index.md      # Simplest possible index
    │       ├── agent-input.json      # Example input envelope
    │       └── agent-output.json     # Example artifact return
    │
    ├── validation-loops/             # EXTENSION
    │   ├── SKILL.md
    │   ├── templates/
    │   │   ├── gap-queue-section.md  # Index section for gaps
    │   │   └── check-module-template.md
    │   └── examples/
    │       └── validation-flow.md
    │
    ├── clarification-protocol/       # EXTENSION
    │   ├── SKILL.md
    │   ├── templates/
    │   │   └── clarification-section.md
    │   └── examples/
    │       └── question-format.json
    │
    └── resume-recovery/              # EXTENSION
        ├── SKILL.md
        └── examples/
            └── state-machine.md
```

### Extension Details

#### validation-loops

Adds to index.md:
- Gap Priority Queue (gaps with priority, status, tier)
- Gap Resolution History (append-only log)
- Traceability Matrix (requirement ↔ check mapping)

Provides:
- Check module format
- Tier behavior (auto-resolve, auto-retry, escalate)
- Termination conditions

#### clarification-protocol

Adds to index.md:
- Unified Pending Questions
- Iteration tracking

Provides:
- Question format for AskUserQuestion
- Answer application patterns
- Iteration limits and stale detection

#### resume-recovery

Adds to index.md:
- Loop status enum
- Stale detection counters

Provides:
- State machine patterns
- Recovery decision logic
- Termination reasons

## Rationale

### Why Layered (Core + Extensions)?

1. **Simple on-ramp**: New plugins start with just `workflow-primitives`
2. **Opt-in complexity**: Advanced patterns only when needed
3. **Mirrors reality**: Not all workflows need validation loops or clarifications
4. **Manageable learning curve**: Three extensions is learnable

### Why Template + Schema Consumption?

1. **Concrete starting points**: Copy template, fill in your sections
2. **No false promises**: Can't enforce agent output at runtime
3. **Documentation value**: Schemas clarify expectations
4. **Flexibility**: Templates can be customized per workflow

### Why Typed Input Envelope?

1. **Reduces cognitive load**: Every agent knows input shape
2. **Self-documenting**: Schema shows what's available
3. **Scalable**: New path types added without changing signatures
4. **Task clarity**: `task.mode` helps agents understand their role

### Why Domain-Aligned Extensions (Not Workflow-Aligned)?

1. **Reusability**: Validation loops used by both specify and plan workflows
2. **Capability focus**: Extensions describe what they enable, not which workflow uses them
3. **Composability**: Combine extensions as needed per agent

## Decision Trail

### 1. Primary Goal
- **Options**: Consistency enforcement, Accelerated development, Cross-plugin interoperability
- **Chosen**: Accelerated development
- **Reasoning**: Extract proven patterns as reusable primitives; consistency emerges naturally

### 2. Structure
- **Options**: Single unified skill, Three separate skills, Layered (core + extensions)
- **Chosen**: Layered
- **Reasoning**: Simple on-ramp with optional complexity; mirrors hexagonal architecture

### 3. Core Contents
- **Options**: Minimal (just essentials), Practical (essentials + common patterns), Rich (most patterns)
- **Chosen**: Practical
- **Reasoning**: Decisions log and resume/recovery are universally valuable; gap queues are workflow-specific

### 4. Consumption Model
- **Options**: Documentation-only, Template + Schema, Declarative contracts
- **Chosen**: Template + Schema
- **Reasoning**: Concrete starting points without pretending runtime enforcement exists

### 5. Agent Input
- **Options**: Implicit contracts, Typed input schema, Path registry pattern
- **Chosen**: Typed input schema
- **Reasoning**: Consistent envelope reduces confusion; self-documenting; scales well

### 6. Extensions
- **Options**: Single extension, Domain-aligned extensions, Workflow-specific extensions
- **Chosen**: Domain-aligned
- **Reasoning**: Reusable across workflows; capability-focused not identity-focused

## Consequences

### Positive

- **Faster plugin development**: Templates and schemas reduce boilerplate
- **Consistency**: Shared primitives create uniform patterns across plugins
- **Discoverability**: Standard structures make workflows easier to understand
- **Maintainability**: Patterns updated in one place benefit all plugins
- **Onboarding**: New contributors learn one pattern, apply it everywhere

### Negative

- **Migration effort**: Existing agents in humaninloop-specs need updating
- **Learning curve**: Plugin authors must learn the primitives
- **Coordination**: Changes to primitives affect multiple plugins

### Risks

- **Over-standardization**: Forcing patterns where flexibility is needed
- **Template drift**: Copied templates diverge from source over time
- **Incomplete extraction**: Missing patterns discovered after implementation

## Implementation Roadmap

### Phase 1: Create Base Skill Structure

```
plugins/humaninloop-core/skills/workflow-primitives/
├── SKILL.md
├── templates/
│   ├── index-template.md
│   └── artifact-schema.md
└── examples/
    ├── minimal-index.md
    ├── agent-input.json
    └── agent-output.json
```

### Phase 2: Extract Patterns from humaninloop-specs

1. Extract index.md core sections into template
2. Document artifact return format
3. Define agent input envelope schema
4. Create minimal examples

### Phase 3: Create Extension Skills

1. Create `validation-loops` skill (extract from spec-checks, validator patterns)
2. Create `clarification-protocol` skill (extract from spec-clarify patterns)
3. Create `resume-recovery` skill (extract from priority loop state machine)

### Phase 4: Update humaninloop-specs Agents

1. Add `skills: [workflow-primitives]` to all agents
2. Add extension skills where needed
3. Refactor agents to use standard input envelope
4. Ensure artifact returns match schema

### Phase 5: Validate with New Plugin

1. Create minimal test plugin using only the skills
2. Verify templates are sufficient
3. Document gaps and iterate

### Phase 6: Update humaninloop (plan/tasks)

1. Apply same patterns to plan and tasks workflows
2. Ensure consistency across all humaninloop plugins

## Open Questions

1. **Template variables**: Use `{placeholders}` or `{{mustache}}` syntax?
2. **Schema format**: Provide JSON Schema files for tooling?
3. **Skill versioning**: How to handle breaking changes to primitives?
4. **Validation tooling**: Should we provide a "lint" command that checks agent outputs?
5. **Cross-workflow state**: How do artifacts flow from specify → plan → tasks?

## Related

- [ADR-006: humaninloop-core Plugin](./006-humaninloop-core-plugin.md) - Where these skills will live
- [ADR-005: Hexagonal Multi-Agent Architecture](./005-hexagonal-agent-architecture.md) - Layer boundaries and skill composition
- [ADR-004: Specify Plugin Extraction](./004-specify-plugin-extraction.md) - Reference implementation patterns
