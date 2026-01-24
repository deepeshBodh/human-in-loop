---
name: patterns-technical-decisions
description: This skill should be used when the user asks to "evaluate alternatives", "make technology choice", "document decision", or mentions "technology choice", "alternatives", "trade-offs", "decision record", "rationale", "why we chose", or "NEEDS CLARIFICATION". Provides evaluation framework and ADR documentation format.
---

# Making Technical Decisions

## Purpose

Provide a complete framework for technology decisions: evaluate alternatives against consistent criteria, make informed choices, and document decisions so future maintainers understand WHY choices were made.

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

See [EVALUATION-MATRIX.md](EVALUATION-MATRIX.md) for detailed criteria, scoring, and technology category comparisons.

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

See [DECISION-RECORD.md](DECISION-RECORD.md) for full ADR format, consequences, and dependency tracking.

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

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Single option "evaluation" | No real choice | Always list alternatives |
| Shiny object syndrome | New tech bias | Require strong justification |
| Vague rationale | "It's better" | Connect to criteria |
| Ignoring team skills | Hidden costs | Weight familiarity |
| Missing consequences | Only positives | List negatives too |
| Orphan decisions | No connections | Map dependencies |
| Constitution blindness | Principle violations | Check alignment |
