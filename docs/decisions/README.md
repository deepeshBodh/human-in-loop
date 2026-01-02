# Architecture Decision Records

This folder contains Architecture Decision Records (ADRs) documenting significant technical decisions in the HumanInLoop Marketplace.

## What is an ADR?

An ADR captures the context, decision, and consequences of an architectural choice. They provide a historical record of *why* the codebase is structured the way it is.

## ADR Index

| ID | Title | Status |
|----|-------|--------|
| [001](./001-multi-agent-architecture.md) | Multi-Agent Architecture | Accepted |
| [002](./002-claude-code-native.md) | Claude Code Native Integration | Accepted |
| [003](./003-brownfield-first.md) | Brownfield-First Design | Accepted |
| [004](./004-specify-plugin-extraction.md) | Specify Plugin Extraction | Accepted |
| [005](./005-hexagonal-agent-architecture.md) | Hexagonal Multi-Agent Architecture | Proposed |
| [006](./006-humaninloop-core-plugin.md) | humaninloop-core Plugin | Proposed |

## ADR Template

When adding a new ADR, use this structure:

```markdown
# ADR-NNN: Title

**Status:** Proposed | Accepted | Deprecated | Superseded
**Date:** YYYY-MM-DD

## Context

What is the issue that we're seeing that is motivating this decision?

## Decision

What is the change that we're proposing and/or doing?

## Rationale

Why is this the right decision? What alternatives were considered?

## Consequences

What becomes easier or harder because of this decision?

## Related

Links to related ADRs, code, or documentation.
```

## Contributing

When making significant architectural decisions:
1. Create a new ADR with the next available number
2. Discuss in a PR if the decision warrants team input
3. Update the index in this README
