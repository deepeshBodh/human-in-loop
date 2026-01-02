# ADR-007: Agent Communication Schema

**Status**: Proposed
**Date**: 2026-01-02
**Decision**: Define standard input and output envelope schemas for agent communication

---

## Problem Statement

Agents in the humaninloop ecosystem lack a standard communication protocol. Each agent defines its own input expectations and output format, making it difficult to:
- Compose agents in workflows
- Understand what an agent needs vs. produces
- Pass context between agents

## Context & Constraints

- **ADR-006**: `humaninloop-core` hosts shared infrastructure
- **ADR-005**: Agents are stateless (no workflow state persistence) but have tool bindings for I/O
- **Constraint**: Can't enforce schemas at runtime—documentation must be clear enough that agents follow naturally
- **Design Principle**: Standard but flexible—the envelope is the contract, contents can vary

## Decision

Define two schemas: **Agent Input Envelope** and **Agent Output Envelope**.

### Agent Input Envelope

```json
{
  "context": {
    "feature_id": "005-user-auth",
    "workflow": "specify",
    "iteration": 1
  },
  "paths": {
    "feature_root": "specs/005-user-auth/",
    "spec": "specs/005-user-auth/spec.md",
    "checks": "check-modules/spec-checks.md"
  },
  "task": {
    "action": "validate",
    "params": {}
  },
  "prior_context": [
    "Spec complete",
    "3 edge cases identified"
  ]
}
```

| Field | Required | Purpose |
|-------|----------|---------|
| `context` | Yes | Workflow identity and position |
| `paths` | Yes | All file paths the agent may need (artifacts, config, etc.) |
| `task` | Yes | What the agent should do |
| `prior_context` | No | Notes from previous agent in the workflow |

**Key Design Decisions:**
- **Paths, not content**: Agents receive file paths and read files themselves. Keeps input envelope small; agents decide what they need.
- **Config in paths**: No distinction between "config files" and "artifact files"—`paths` is the single source for all file references.
- **No agent names**: `prior_context` is just notes, not who sent them. Agents don't know the workflow graph.

### Agent Output Envelope

```json
{
  "success": true,
  "summary": "Validated spec. Found 3 gaps requiring attention.",
  "artifacts": [
    {
      "path": "specs/005-user-auth/spec.md",
      "operation": "update",
      "content": "..."
    }
  ],
  "notes": [
    "Ready for next phase",
    "Focus on auth edge cases"
  ],
  "recommendation": "proceed"
}
```

| Field | Required | Purpose |
|-------|----------|---------|
| `success` | Yes | Did the agent complete its task? |
| `summary` | Yes | Human-readable description of what happened (including errors) |
| `artifacts` | Yes | Files to write (can be empty array) |
| `notes` | No | Context for the next agent |
| `recommendation` | Yes | What should happen next |

**Key Design Decisions:**
- **Summary for everything**: Same field describes success or failure. No conditional error structures.
- **Artifacts only**: No separate `state_updates`. Artifacts are the source of truth.
- **Notes without routing**: Agents pass context forward but don't name the next agent—workflow decides routing.

### Recommendation Values

| Value | Meaning |
|-------|---------|
| `proceed` | Agent succeeded, continue workflow |
| `retry` | Agent needs another attempt (e.g., validation failed) |
| `escalate` | Agent blocked, needs user input |

Three values are sufficient. Workflow termination and step-skipping are orchestration decisions, not agent concerns.

### Artifact Structure

```json
{
  "path": "relative/path/to/file.md",
  "operation": "create | update",
  "content": "full file content"
}
```

| Field | Purpose |
|-------|---------|
| `path` | Relative path from feature root |
| `operation` | `create` for new files, `update` for modifications |
| `content` | Complete file content |

## Rationale

**Why paths instead of content?**
- Agents have tool bindings (Read, Write, Grep)—they're expected to do I/O
- Passing full file content bloats the input envelope
- Agents may only need portions of files

**Why no state_updates?**
- Artifacts are the source of truth
- Avoids duplicate data structures that can drift
- Workflow can parse artifacts if it needs structured data

**Why summary instead of result/error?**
- Single field for all outcomes keeps schema simple
- Human-readable by design
- No conditional structures based on success/failure

**Why notes without agent names?**
- Agents shouldn't know the workflow graph (ADR-005 layer boundaries)
- Context is valuable; coupling to specific agents is not
- Workflow orchestration decides sequencing

## Relationship to ADR-005

ADR-005 defines the conceptual contract pattern. This ADR provides the concrete schema. Key alignment:

| ADR-005 Concept | ADR-007 Implementation |
|-----------------|------------------------|
| "Agents are stateless functions" | Stateless re: workflow state; still perform I/O via tools |
| Input contract | `context` + `paths` + `task` + `prior_context` |
| Output contract | `success` + `summary` + `artifacts` + `notes` + `recommendation` |
| `next_recommendation` | `recommendation` (same three values) |

ADR-005's `state_updates` and `result` fields are superseded by this schema's simpler `artifacts` + `summary` approach.

## Implementation

Create a skill in `humaninloop-core`:

```
plugins/humaninloop-core/skills/agent-protocol/
├── SKILL.md              # Schema documentation
└── examples/
    ├── input.json        # Example input envelope
    └── output.json       # Example output envelope
```

Agents declare `skills: [agent-protocol]` to indicate compliance.

## Consequences

### Positive
- Clear, minimal contracts between agents
- Flexible contents within standard envelope
- No coupling between agents
- Consistent error handling

### Negative
- Existing agents need updating
- ADR-005 contract examples need revision to match

## Decision Trail

| Question | Options | Chosen | Reasoning |
|----------|---------|--------|-----------|
| Paths vs content | Paths, Content, Hybrid | Paths | Agents have tool bindings; keeps envelope small |
| Config location | Separate field, task.params, paths | Paths | Config files are just paths; single source for file refs |
| State updates | Keep, Remove, Optional | Remove | Artifacts are source of truth; avoids duplication |
| Result field | Keep, Artifacts only, Summary | Summary | Human-readable; consistent for success/failure |
| Handoff design | Keep as-is, Remove, Notes only | Notes only | Context without coupling to specific agents |
| Error handling | Structured error, Summary, Errors array | Summary | Keeps schema simple; same field for all outcomes |
| Recommendation values | Current 3, Add complete, Add skip | Current 3 | Workflow controls termination; agents just recommend |

## Related

- [ADR-006: humaninloop-core Plugin](./006-humaninloop-core-plugin.md) — Where the agent-protocol skill lives
- [ADR-005: Hexagonal Multi-Agent Architecture](./005-hexagonal-agent-architecture.md) — Layer boundaries and conceptual contracts
