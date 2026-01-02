---
name: context-patterns
description: Patterns for structured context loading and management. Use when you need to systematically gather, organize, and maintain context across multi-step tasks. Applies to any workflow requiring context handoffs between phases or agents.
---

# Context Patterns

## Purpose

Provide structured patterns for loading, organizing, and managing context in multi-step workflows. These patterns ensure consistent context handling regardless of the specific domain or workflow.

## Core Principles

1. **Progressive Loading**: Load only what's needed, when it's needed
2. **Explicit Handoffs**: Document what context is passed between phases
3. **Single Source of Truth**: One location for workflow state
4. **Traceability**: Track where information came from

## Context Loading Pattern

### Phase 1: Identify Required Context

Before any task, enumerate:
- **Input artifacts**: What files/data must be read?
- **State files**: What workflow state must be loaded?
- **Configuration**: What settings apply?

### Phase 2: Load in Priority Order

```
1. Configuration (constraints, principles)
2. State files (current workflow position)
3. Input artifacts (content to process)
4. Prior outputs (from previous phases)
```

### Phase 3: Validate Completeness

Before proceeding:
- [ ] All required files exist and are readable
- [ ] State is consistent (no conflicting information)
- [ ] Dependencies from prior phases are satisfied

## Context Handoff Pattern

When completing a phase, document:

```markdown
### Handoff Notes

**Phase Completed**: {phase_name}
**Timestamp**: {ISO-8601}

**Outputs Produced**:
- {artifact_path}: {brief_description}

**State Updates**:
- {key}: {value}

**For Next Phase**:
- Required inputs: {list}
- Recommendations: {notes}
```

## Context File Patterns

### Index File Pattern

Central coordination file for workflow state:

```markdown
# Workflow Index

## Current State
- Phase: {current_phase}
- Iteration: {count}
- Status: {in_progress|blocked|complete}

## Artifact Registry
| Artifact | Status | Path |
|----------|--------|------|
| ... | ... | ... |

## Gap Queue
| Priority | ID | Description | Status |
|----------|-----|-------------|--------|
| ... | ... | ... | ... |

## Handoff Log
{append-only log of phase transitions}
```

### Context File Pattern

Phase-specific context accumulator:

```markdown
# {Workflow} Context

## Configuration
{loaded settings and constraints}

## Accumulated State
{information gathered across phases}

## Registries
{structured data extracted during workflow}

## Handoff Notes
{notes from each phase completion}
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Loading everything upfront** | Wastes context, may load stale data | Progressive loading |
| **Implicit handoffs** | Next phase doesn't know what changed | Explicit handoff notes |
| **Multiple state files** | Conflicting information | Single index file |
| **No validation** | Proceed with missing context | Check completeness |
| **Overwriting history** | Lose audit trail | Append-only logs |

## When to Use These Patterns

- Starting any multi-phase workflow
- Transitioning between workflow phases
- Debugging context-related issues
- Designing new workflow systems
