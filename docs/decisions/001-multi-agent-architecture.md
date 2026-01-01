# ADR-001: Multi-Agent Architecture

**Status:** Accepted
**Date:** 2026-01-01

## Context

Specification-driven development requires multiple distinct capabilities: requirement clarification, spec writing, codebase analysis, planning, task generation, and validation. These are cognitively different tasks that benefit from specialized focus.

The question: Should these capabilities live in a single monolithic agent, or be distributed across multiple specialized agents?

## Decision

Use a **multi-agent architecture** where each workflow stage is handled by focused, specialized agents.

Current agents in the humaninloop plugin:
- **Specification stage:** `spec-writer`, `spec-clarify`
- **Planning stage:** `plan-builder` (phase-aware), `plan-validator`, `codebase-discovery`
- **Task stage:** `task-planner`, `task-generator`, `task-validator`, `gap-classifier`
- **Implementation stage:** `scaffold-agent`, `checklist-writer`, `checklist-context-analyzer`

## Rationale

### Benefits of multi-agent approach

1. **Focused responsibilities** - Each agent has a clear, testable purpose. The `spec-writer` only writes specs; the `plan-validator` only validates plans.

2. **Independent evolution** - Agents can be improved, replaced, or versioned independently without affecting the entire workflow.

3. **Composability** - Teams can use subsets of agents or compose custom workflows from available agents.

4. **Reduced context bloat** - Each agent receives only the context it needs, improving response quality and reducing token usage.

5. **Easier debugging** - When something fails, the responsible agent is immediately identifiable.

### Alternatives considered

**Monolithic agent:** A single large agent handling all workflow stages.
- Rejected because: Context pollution between stages, harder to maintain, all-or-nothing changes, difficult to test individual capabilities.

**Pipeline with handoff files only:** Agents communicate only via file artifacts.
- Partially adopted: File artifacts are the primary communication mechanism, but agents can also be invoked directly by commands.

## Consequences

- **Positive:** Clear ownership, testable agents, flexible composition
- **Negative:** More files to maintain, need clear contracts between agents
- **Neutral:** Requires documentation of agent responsibilities and handoff protocols

## Related

- [Plugin structure](../../plugins/humaninloop/README.md)
- Each agent has its own markdown file in `plugins/humaninloop/agents/`
