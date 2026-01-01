# Phase 0: Research Procedures

Detailed procedures for the Research phase (plan-builder, phase 0).

---

## Mission

Resolve technical unknowns from the specification by researching options and documenting decisions. Output: `research.md` with all unknowns resolved.

---

## Unknown Extraction

Compile all unknowns to resolve:

### Explicit Unknowns
- `[NEEDS CLARIFICATION]` markers in spec

### Implicit Unknowns
Technology decisions implied by requirements:
- Data storage (what kind of database?)
- Authentication (what mechanism?)
- API style (REST, GraphQL, gRPC?)
- External integrations (what services?)

### Recording Format

For each unknown:
- **Source**: FR-xxx, US#, or general section
- **Question**: What needs to be decided
- **Impact**: What depends on this decision

---

## Research & Decision Making

For each unknown:

### 1. Identify Options
At least 2-3 alternatives:
- Industry standards
- Project constraints
- Constitution principles
- **Brownfield**: Include "Use existing" when applicable

### 2. Evaluate Each Option

| Option | Pros | Cons |
|--------|------|------|
| Option A | ... | ... |
| Option B | ... | ... |

Consider:
- Fit with other decisions
- Complexity and risk
- **Brownfield**: Integration complexity with existing codebase

### 3. Make Decision
- Choose most appropriate option
- Document rationale (WHY this choice)
- Note trade-offs accepted
- **Brownfield**: Document why existing tech was/wasn't reused

### 4. Check Constitution
- Does choice follow `[phase:0]` principles?
- If deviation, document justification

---

## research.md Format

```markdown
# Research: {feature_id}

> Technical research and decisions for the planning phase.

---

## Summary

| Unknown | Decision | Rationale |
|---------|----------|-----------|
| ... | ... | ... |

---

## Decision 1: [Unknown Name]

**Source**: [FR-xxx / US#]

**Question**: [What needed to be decided]

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| ... | ... | ... |

**Decision**: [Chosen option]

**Rationale**: [Why this choice]

**Trade-offs Accepted**: [What we're giving up]

**Constitution Alignment**: [How this aligns with principles]

---

## Dependencies

| Decision | Depends On | Impacts |
|----------|------------|---------|
| ... | ... | ... |

---

## Open Questions

[Any remaining questions for escalation - should be empty for pass]
```

---

## Quality Checklist

- [ ] All `[NEEDS CLARIFICATION]` markers addressed
- [ ] All implicit technology decisions made
- [ ] Each decision has at least 2 alternatives
- [ ] Each decision has clear rationale
- [ ] Constitution `[phase:0]` principles checked
- [ ] Dependencies between decisions documented
- [ ] research.md is complete and well-structured
