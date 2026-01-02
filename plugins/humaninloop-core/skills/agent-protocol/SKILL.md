---
name: agent-protocol
description: Standard input/output envelope schema for agent communication.
  Agents declaring this skill follow the ADR-007 communication protocol,
  enabling workflow composition without tight coupling between agents.
---

# Agent Protocol

## Purpose

Define standard envelopes for agent input and output to enable workflow
composition without tight coupling between agents. This protocol ensures:

- Clear contracts between agents and workflows
- Flexible contents within standard envelope
- No coupling between agents (agents don't know the workflow graph)
- Consistent error handling via summary field

## Input Envelope Schema

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
    "index": "specs/005-user-auth/.workflow/index.md",
    "constitution": ".humaninloop/memory/constitution.md"
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

### Input Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `context` | Yes | Workflow identity and position |
| `context.feature_id` | Yes | Feature identifier (null for scaffold agent) |
| `context.workflow` | Yes | Workflow name (specify, plan, tasks) |
| `context.iteration` | Yes | Current iteration number |
| `paths` | Yes | All file paths the agent may need |
| `task` | Yes | What the agent should do |
| `task.action` | Yes | Action verb (validate, create, classify_gaps, etc.) |
| `task.params` | Yes | Action-specific parameters (can be empty) |
| `prior_context` | No | Notes from previous agent in the workflow |

### Key Design Decisions

- **Paths, not content**: Agents receive file paths and read files themselves. Keeps input envelope small; agents decide what they need.
- **Config in paths**: No distinction between "config files" and "artifact files" - `paths` is the single source for all file references.
- **No agent names in prior_context**: Just notes, not who sent them. Agents don't know the workflow graph.

## Output Envelope Schema

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

### Output Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `success` | Yes | Did the agent complete its task? |
| `summary` | Yes | Human-readable description of what happened (including errors) |
| `artifacts` | Yes | Files to write (can be empty array) |
| `notes` | No | Context for the next agent |
| `recommendation` | Yes | What should happen next |

### Key Design Decisions

- **Summary for everything**: Same field describes success or failure. No conditional error structures.
- **Artifacts only**: No separate `state_updates`. Artifacts are the source of truth.
- **Notes without routing**: Agents pass context forward but don't name the next agent - workflow decides routing.

## Recommendation Values

| Value | Meaning |
|-------|---------|
| `proceed` | Agent succeeded, continue workflow |
| `retry` | Agent needs another attempt (e.g., validation failed) |
| `escalate` | Agent blocked, needs user input |

Three values are sufficient. Workflow termination and step-skipping are orchestration decisions, not agent concerns.

## Artifact Structure

```json
{
  "path": "relative/path/to/file.md",
  "operation": "create | update",
  "content": "full file content"
}
```

| Field | Purpose |
|-------|---------|
| `path` | Relative path from repository root |
| `operation` | `create` for new files, `update` for modifications |
| `content` | Complete file content |

## Field Mapping Patterns

When migrating existing agents to this protocol, use these patterns:

### Domain-Specific Input Fields

Map to `task.params`:

```
# Before
{ "bounds": {...}, "brownfield_overrides": {...} }

# After
{ "task": { "action": "discover", "params": { "bounds": {...}, "brownfield_overrides": {...} } } }
```

### Dual-Mode Agents

Use `task.action` for mode:

```
# Before
{ "mode": "classify_gaps" }

# After
{ "task": { "action": "classify_gaps", "params": {...} } }
```

### Domain-Specific Output Fields

Summarize in `notes`:

```
# Before
{ "validation_report": { "passed": 8, "failed": 1 }, "collision_risks": [...] }

# After
{ "notes": ["Validation: 8 passed, 1 failed", "2 collision risks detected"] }
```

### State Updates

Eliminate - return updated index.md as artifact:

```
# Before
{ "state_updates": { "gap_priority_queue": [...] } }

# After
{ "artifacts": [{ "path": ".workflow/index.md", "operation": "update", "content": "..." }] }
```

## When to Use This Protocol

- Agents composable in workflows
- Agents that exchange context
- Agents that produce artifacts
- Any stateless agent function

## Examples

See `examples/input.json` and `examples/output.json` for complete examples.

## Related

- [ADR-007: Agent Communication Schema](../../../docs/decisions/007-agent-communication-schema.md) - Authoritative specification
- [ADR-005: Hexagonal Multi-Agent Architecture](../../../docs/decisions/005-hexagonal-agent-architecture.md) - Layer boundaries
