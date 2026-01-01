# ADR-003: Brownfield-First Design

**Status:** Accepted
**Date:** 2026-01-01

## Context

Most real-world development happens in existing codebases (brownfield), not greenfield projects. Specification-driven tools often assume you're starting fresh, making them awkward for:
- Adding features to existing systems
- Refactoring legacy code
- Integrating with established patterns

We need to decide whether humaninloop prioritizes greenfield or brownfield scenarios.

## Decision

Design all workflows to be **brownfield-first**: assume an existing codebase with established patterns, conventions, and constraints.

Greenfield projects are treated as a special case (simpler brownfield with no existing code).

## Rationale

### What brownfield-first means in practice

1. **Codebase discovery is mandatory** - Before planning, agents analyze existing code to understand patterns, conventions, and integration points.

2. **Specs reference existing entities** - Specifications explicitly map new features to existing components, not just abstract requirements.

3. **Plans include integration points** - Implementation plans identify where new code connects to existing code, not just what new code to write.

4. **Tasks have brownfield markers** - Generated tasks distinguish between new code, modifications to existing code, and integration work.

5. **Validation checks existing patterns** - Check modules verify that plans respect existing architectural decisions.

### Benefits

1. **Realistic workflows** - Matches how most development actually happens
2. **Reduces integration surprises** - Existing code is analyzed upfront, not discovered during implementation
3. **Preserves existing patterns** - New code follows established conventions
4. **Supports incremental adoption** - Teams can adopt humaninloop in existing projects without restructuring

### Alternatives considered

**Greenfield-first with brownfield adapters:** Build for new projects, add legacy support later.
- Rejected because: Results in awkward brownfield experience. Better to design for the harder case (brownfield) and get greenfield for free.

**Separate greenfield/brownfield modes:** Different commands or flags for each scenario.
- Rejected because: Adds cognitive overhead. One workflow that handles both is simpler.

## Consequences

- **Positive:** Works naturally with existing codebases, realistic workflow
- **Negative:** Slightly more complexity for pure greenfield (codebase discovery still runs, just finds nothing)
- **Neutral:** Requires more sophisticated codebase analysis agents

## Related

- `codebase-discovery` agent
- `gap-classifier` agent
- Brownfield markers in `tasks-template.md`
