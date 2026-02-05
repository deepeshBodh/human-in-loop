---
name: patterns-technical-decisions
description: This skill MUST be invoked when the user says "evaluate alternatives", "make technology choice", "document decision", "technology choice", "trade-offs", "decision record", "rationale", or "why we chose". SHOULD also invoke when user mentions "alternatives" or "NEEDS CLARIFICATION".
---

# Making Technical Decisions

## Overview

Provide a complete framework for technology decisions: evaluate alternatives against consistent criteria, make informed choices, and document decisions so future maintainers understand WHY choices were made.

## When to Use

- Choosing between technology options (libraries, frameworks, services)
- When research.md requires "NEEDS CLARIFICATION" resolution
- Documenting architectural decisions for the team
- When spec or plan requires technology choice justification
- Evaluating existing stack vs new dependencies
- Any decision with long-term maintenance implications

## When NOT to Use

- **Trivial changes** - No architectural impact, obvious solution
- **Decisions already documented** - Existing ADR covers the scenario
- **Emergency hotfixes** - Document decision post-facto, don't block fix
- **Pure implementation details** - Internal code structure without external impact
- **Reversible choices** - Easily changed later without consequence

## Decision Workflow

```
1. EVALUATE    →    2. DECIDE    →    3. DOCUMENT
   Options           Best fit          For posterity
```

### Phase 1: Evaluate Options

For each decision point, consider 2-3 alternatives minimum.

**Quick Criteria Reference:**

| Criterion | Key Question |
|-----------|--------------|
| **Fit** | Does it solve the problem fully? |
| **Complexity** | How hard to implement and maintain? |
| **Team Familiarity** | Does the team know this tech? |
| **Ecosystem** | Good docs, active community? |
| **Scalability** | Will it grow with the project? |
| **Security** | Good security posture? |
| **Cost** | Total cost of ownership? |
| **Brownfield Alignment** | Fits existing stack? |

See [EVALUATION-MATRIX.md](references/EVALUATION-MATRIX.md) for detailed criteria, scoring, and technology category comparisons.

### Phase 2: Decide

Score options against weighted criteria. Document:
- Which option scores best
- Why criteria were weighted as they were
- What trade-offs are accepted

**Quick Comparison Format:**

| Option | Pros | Cons | Alignment | Verdict |
|--------|------|------|-----------|---------|
| Option A | + Fast, + Simple | - New dep | High | **Best** |
| Option B | + Familiar | - Slow | Medium | Good |
| Option C | + Feature-rich | - Complex | Low | Poor |

### Phase 3: Document

Record decisions in ADR format for future maintainers.

**Quick Decision Record:**

```markdown
## Decision: [Title]

**Status**: Proposed | Accepted | Deprecated

**Context**: [Why this decision is needed]

**Decision**: [What we chose]

**Rationale**: [Why - connect to criteria]

**Trade-offs Accepted**: [What we gave up]
```

See [DECISION-RECORD.md](references/DECISION-RECORD.md) for full ADR format, consequences, and dependency tracking.

## research.md Output

Decisions go in `research.md` with this structure:

```markdown
# Research: {feature_id}

## Summary

| ID | Decision | Choice | Rationale |
|----|----------|--------|-----------|
| D1 | Auth mechanism | JWT | Stateless, scalable |
| D2 | Session storage | PostgreSQL | Existing stack |

---

## Decision 1: [Title]

[Full decision record]

---

## Dependencies

| Decision | Depends On | Impacts |
|----------|------------|---------|
| D2 | D1 | Session table schema |
```

## Brownfield Alignment

Always check existing stack first:

| Scenario | Alignment | Action |
|----------|-----------|--------|
| Existing dep solves problem | High | Prefer reuse |
| New dep, same ecosystem | Medium | Document justification |
| New dep, different ecosystem | Low | Strong justification needed |
| Conflicting with existing | None | Avoid or escalate |

## Quality Checklist

Before finalizing:

**Evaluation:**
- [ ] At least 2-3 alternatives considered
- [ ] Criteria weighted by project context
- [ ] Each option has pros/cons
- [ ] Brownfield alignment assessed

**Documentation:**
- [ ] Context explains WHY decision is needed
- [ ] Rationale connects to specific criteria
- [ ] Trade-offs explicitly documented
- [ ] Constitution alignment checked
- [ ] Dependencies between decisions mapped

## Common Mistakes

### Single Option "Evaluation"
❌ "We evaluated Option A and chose it"
✅ "We compared Option A, Option B, and Option C against weighted criteria"

### Shiny Object Syndrome
❌ Choosing newest technology because it's trending
✅ Require strong justification for unfamiliar dependencies over existing stack

### Vague Rationale
❌ "We chose JWT because it's better"
✅ "We chose JWT because: stateless (fits our scale), team familiarity (3/4 devs), ecosystem support"

### Ignoring Team Skills
❌ Choosing Rust for a Python team without accounting for learning curve
✅ Weight team familiarity criterion appropriately in evaluation matrix

### Missing Trade-offs
❌ Only listing positives of chosen option
✅ Explicitly document what was given up: "Trade-off: JWT requires token refresh handling"

### Orphan Decisions
❌ Decisions documented in isolation
✅ Map decision dependencies: "D2 (session storage) depends on D1 (auth mechanism)"

### Constitution Blindness
❌ Making decisions that violate project principles
✅ Check alignment with constitution before finalizing
