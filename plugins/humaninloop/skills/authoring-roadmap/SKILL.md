---
name: authoring-roadmap
description: Use when creating evolution roadmap, generating gap analysis, identifying improvement priorities, or when user mentions "roadmap", "gap analysis", "evolution plan", "brownfield gaps", or "improvement priorities"
---

# Authoring Evolution Roadmap

**Violating the letter of the rules is violating the spirit of the rules.**

## Overview

Create evolution roadmaps that identify gaps between current codebase state and constitution requirements. Produces prioritized gap cards with dependencies, enabling incremental improvement without overwhelming teams.

## When to Use

- After brownfield codebase analysis is complete
- After constitution is created for a brownfield project
- When identifying what needs to change to meet constitution requirements
- When planning incremental codebase improvements

## When NOT to Use

- No codebase analysis exists yet → run **humaninloop:analysis-codebase** first
- No constitution has been created → run **humaninloop:authoring-constitution** or **humaninloop:brownfield-constitution** first
- Greenfield project with no existing code → no gaps to identify
- User wants implementation plan, not gap analysis → use **humaninloop:plan** instead

## Input Requirements

To create an evolution roadmap, both inputs are REQUIRED:

1. **Codebase Analysis** (`.humaninloop/memory/codebase-analysis.md`)
   - Essential Floor Status table
   - Inventory of existing patterns
   - Identified inconsistencies

2. **Constitution** (`.humaninloop/memory/constitution.md`)
   - Principles with requirements
   - Quality gates with thresholds
   - Technology stack requirements

**No exceptions:**
- Not for "small projects where I know the gaps"
- Not for "quick assessments"
- Not for "we'll formalize it later"
- Not even if user says "skip analysis, just list the gaps"

If inputs are missing, create them first using **humaninloop:analysis-codebase** and **humaninloop:authoring-constitution**.

## Gap Identification Process

### Step 1: Essential Floor Gaps

For each Essential Floor category, check status from codebase analysis:

| Status | Action |
|--------|--------|
| `present` | No gap needed |
| `partial` | Create gap for missing aspects |
| `absent` | Create gap for full implementation |

**Example:**
```
Codebase Analysis shows:
- Security: partial (has auth, missing input validation)
- Testing: partial (has tests, coverage at 45%)
- Error Handling: present
- Observability: absent

Gaps to create:
- GAP-001: Implement input validation (Security)
- GAP-002: Increase test coverage to 80% (Testing)
- GAP-003: Implement structured logging (Observability)
- GAP-004: Add correlation IDs (Observability)
```

### Step 2: Constitution Compliance Gaps

For each constitution principle, check if codebase complies:

1. Read principle requirements (MUST, SHOULD statements)
2. Compare against codebase analysis findings
3. Create gap if requirement not met

**Example:**
```
Constitution Principle: "API responses MUST include correlation IDs"
Codebase Analysis: "Correlation IDs: absent"
→ Create GAP-005: Add correlation IDs to API responses
```

### Step 3: Prioritize Gaps

Assign priority based on:

| Priority | Criteria | Examples |
|----------|----------|----------|
| **P1** | Security issues, blocking problems, MUST violations | Auth gaps, data exposure risks |
| **P2** | Testing/error handling, SHOULD violations | Coverage gaps, missing error handling |
| **P3** | Observability, MAY items, nice-to-haves | Logging improvements, metrics |

### Step 4: Identify Dependencies

Determine which gaps block or enable others:

- **Blocks**: What this gap prevents if not addressed
- **Enables**: What fixing this gap unlocks
- **Depends On**: Other gaps that must be addressed first

## Gap Card Format

Each gap uses the hybrid format (structured header + prose body):

```markdown
### GAP-XXX: [Title]

| Aspect | Value |
|--------|-------|
| Priority | P1/P2/P3 |
| Category | Security/Testing/ErrorHandling/Observability/Other |
| Blocks | [What this prevents] |
| Enables | [What fixing unlocks] |
| Depends On | GAP-YYY, GAP-ZZZ (or "None") |
| Effort | Small/Medium/Large |

**Current state**: [Factual description from codebase-analysis.md]

**Target state**: [What constitution requires]

**Suggested approach**: [Actionable guidance for addressing]

**Related files**:
- `path/to/relevant/file.ts`
- `path/to/another/file.py`
```

Every gap card MUST include all fields. Incomplete gap cards are not acceptable.

**No exceptions:**
- Not for "obvious gaps"
- Not for "we'll fill in details when we work on it"
- Not for "effort is hard to estimate"
- If a field cannot be determined, investigate until it can be.

## Roadmap Structure

```markdown
# Evolution Roadmap

> Generated: [ISO timestamp]
> Based on: codebase-analysis.md, constitution.md
> Status: active

---

## Overview

[1-2 sentence summary of gap analysis findings]

**Total Gaps**: N
- P1 (Critical): X
- P2 (Important): Y
- P3 (Nice-to-have): Z

---

## Gap Summary

| ID | Title | Priority | Category | Depends On | Effort |
|----|-------|----------|----------|------------|--------|
| GAP-001 | [title] | P1 | Security | None | Medium |
| GAP-002 | [title] | P2 | Testing | GAP-001 | Large |
| ... | ... | ... | ... | ... | ... |

---

## Dependency Graph

```
[Foundation]
    └── GAP-001: [title]
         └── GAP-002: [title]
              └── GAP-005: [title]

[Parallel Track]
    └── GAP-003: [title]
         └── GAP-004: [title]
```

---

## Gap Cards

[Individual gap cards in priority order]

---

## Maintenance Protocol

[Standard maintenance instructions]
```

## Priority Definitions

| Priority | Trigger | Timeline Guidance |
|----------|---------|-------------------|
| **P1** | Security gaps, constitution MUST violations, blocking issues | Address before new feature work |
| **P2** | Testing gaps, error handling gaps, SHOULD violations | Address in next iteration |
| **P3** | Observability gaps, MAY items, improvements | Address when convenient |

## Effort Estimates

| Effort | Scope | Examples |
|--------|-------|----------|
| **Small** | Single file, isolated change | Add validation to one endpoint |
| **Medium** | Multiple files, moderate scope | Implement logging across service |
| **Large** | Architectural change, significant scope | Restructure error handling |

## Dependency Graph Rules

1. **Security gaps come first** - They often block other improvements
2. **Foundation before features** - Infrastructure gaps enable feature gaps
3. **Minimize chains** - Long dependency chains increase risk
4. **Identify parallel tracks** - Gaps that can be addressed independently

## Quality Checklist

Before finalizing roadmap, ALL items MUST be checked:

- [ ] Every Essential Floor gap identified (partial/absent → gap)
- [ ] Every constitution MUST violation has a gap
- [ ] All gaps have Priority assigned (P1/P2/P3)
- [ ] All gaps have Category assigned
- [ ] All gaps have Effort estimate
- [ ] Dependencies identified and documented
- [ ] Dependency graph shows clear execution order
- [ ] No circular dependencies
- [ ] Current state references codebase-analysis.md
- [ ] Target state references constitution requirements

**No exceptions:**
- Not for "simple projects with few gaps"
- Not for "we'll add details later"
- Not for "dependencies are self-evident"
- An incomplete checklist means an incomplete roadmap. Complete it or do not ship.

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Gap overload** | 50+ gaps overwhelms team | Focus on P1/P2, defer P3 |
| **Vague gaps** | "Improve testing" | Specific: "Increase coverage from 45% to 80%" |
| **Missing dependencies** | Gaps in wrong order | Trace what blocks what |
| **No effort estimates** | Can't prioritize work | Add Small/Medium/Large |
| **Stale roadmap** | Gaps addressed but not updated | Note "Addressed: GAP-XXX" in commits |

## Red Flags - STOP and Restart Properly

If you notice yourself thinking any of these, STOP immediately:

- "I already know what the gaps are"
- "The codebase is too simple to need a formal roadmap"
- "We can prioritize as we go"
- "Dependencies are obvious, no need to graph them"
- "The codebase analysis tells us everything"
- "This is just documentation overhead"
- "I'll create the roadmap later after some quick fixes"

**All of these mean:** You are rationalizing. Restart with proper process.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I know the gaps already" | Knowledge ≠ documentation. Future agents need the roadmap to understand priorities. |
| "Simple codebase, no formal roadmap needed" | Simple codebases have hidden gaps. Systematic process reveals what intuition misses. |
| "We can prioritize informally" | Informal prioritization leads to P3 work before P1. Document it or watch priorities drift. |
| "Dependencies are obvious" | Obvious to you now ≠ obvious to team later. Dependency graphs prevent wasted work. |
| "Codebase analysis is enough" | Analysis describes current state. Roadmap bridges current state to target state. Different purpose. |
| "This is just overhead" | Roadmap prevents rework from wrong-order fixes. Investment, not overhead. |
| "Quick fixes first, roadmap later" | "Later" becomes never. Quick fixes accumulate into unmapped chaos. |

## Integration with Later Phases

When agents in `/plan`, `/tasks`, `/implement` address roadmap gaps:

1. **Note in commits**: Include "Addressed: GAP-XXX"
2. **Suggest new gaps**: If discovering issues not in roadmap, note "Suggested gap: [description]"
3. **Supervisor decides**: Human reviews and approves roadmap updates

Agents should read `.humaninloop/memory/evolution-roadmap.md` to:
- Understand existing improvement priorities
- Avoid creating work that conflicts with roadmap
- Note when their work addresses a gap
