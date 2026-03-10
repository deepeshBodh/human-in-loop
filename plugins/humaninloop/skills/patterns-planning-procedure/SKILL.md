---
name: patterns-planning-procedure
description: >
  This skill MUST be invoked when the user says "plan procedure",
  "planning workflow", "fill planner report", or "resolve markers".
  SHOULD also invoke when user mentions "evolution roadmap",
  "quickstart structure", "quality gates", "NEEDS CLARIFICATION",
  or "planner report". Procedural planning knowledge for research,
  data model, and contract phases.
---

# Planning Procedure Patterns

## Overview

Provide procedural knowledge for the planning workflow: evolution roadmap integration, specification marker resolution, quickstart guide authoring, planner report population, and phase-aware quality gates.

## When to Use

- Starting a planning phase (research, data model, contracts)
- Filling out `planner-report.md` after producing an artifact
- Resolving `[NEEDS CLARIFICATION]` markers from specification
- Writing `quickstart.md` for a feature
- Checking whether work addresses evolution roadmap gaps
- Determining phase completion criteria

## When NOT to Use

- **Technology decisions** - Use `humaninloop:patterns-technical-decisions`
- **Entity modeling** - Use `humaninloop:patterns-entity-modeling`
- **API contract design** - Use `humaninloop:patterns-api-contracts`
- **Artifact review/validation** - Use `humaninloop:validation-plan-artifacts`
- **Codebase analysis** - Use `humaninloop:analysis-codebase`

## Evolution Roadmap Integration

Before starting any planning phase, check for an evolution roadmap at `.humaninloop/memory/evolution-roadmap.md`.

### Pre-Phase: Read the Roadmap

| Step | Action |
|------|--------|
| 1 | Read `.humaninloop/memory/evolution-roadmap.md` |
| 2 | Extract P1 gap priorities and dependency graph |
| 3 | Note gaps relevant to the current feature |
| 4 | Record relevant gap IDs for use in report |

### During Phase: Track Gaps

When producing artifacts, check whether work addresses existing gaps:

```markdown
## Roadmap Alignment

| Gap ID | Title | Status |
|--------|-------|--------|
| GAP-001 | Configure pytest infrastructure | Addressed |
| GAP-005 | Standardize SKILL.md frontmatter | Not relevant |
```

Include `Addressed: GAP-XXX` annotations in the planner report when work resolves or partially resolves a gap.

### Post-Phase: Discover New Gaps

If the planning process reveals issues not in the current roadmap, add to the planner report:

```markdown
Suggested gap: [Description of newly discovered gap]
```

Never auto-update the roadmap. Suggestions go in the planner report for human review.

### No Roadmap Present

If `.humaninloop/memory/evolution-roadmap.md` does not exist, skip roadmap integration. Note its absence in the planner report under Open Questions.

## Specification Marker Resolution

### Hunting Markers

Search the specification for unresolved markers before starting each phase:

```bash
grep -n "\[NEEDS CLARIFICATION\]\|\[TBD\]\|\[TODO\]\|\[PLACEHOLDER\]" specs/{feature-id}/spec.md
```

### Resolution Process

| Marker Type | Action |
|-------------|--------|
| `[NEEDS CLARIFICATION]` | Research and resolve, or escalate to supervisor |
| `[TBD]` | Make a decision and document rationale |
| `[TODO]` | Complete the missing content |
| `[PLACEHOLDER]` | Replace with actual content |

### Resolution Documentation

Document each resolved marker in the planner report:

| Marker | Location | Resolution | Rationale |
|--------|----------|------------|-----------|
| [NEEDS CLARIFICATION]: Auth mechanism | spec.md L45 | JWT with refresh tokens | Stateless, fits scale |
| [TBD]: Rate limiting | spec.md L78 | Token bucket, 100 req/min | Standard for API tier |

Every `[NEEDS CLARIFICATION]` marker MUST be either resolved or explicitly escalated. Do not leave markers unaddressed.

## Quickstart Guide Structure

When producing `quickstart.md` during the contracts phase, include these sections:

| Section | Content |
|---------|---------|
| Authentication | Auth sequence with request/response examples |
| Common User Flows | Primary user actions as curl examples |
| Error Handling | Common error responses with recovery guidance |
| Quick Reference | Endpoint summary table |

Use realistic values, not placeholder gibberish. Every curl example MUST be copy-pasteable.

See [QUICKSTART-AND-REPORT.md](references/QUICKSTART-AND-REPORT.md) for complete templates and examples.

## Planner Report Population

Fill `planner-report.md` using the template at `${CLAUDE_PLUGIN_ROOT}/templates/planner-report-template.md`. See [QUICKSTART-AND-REPORT.md](references/QUICKSTART-AND-REPORT.md) for field-by-field guidance.

### Phase-Specific Key Outputs

| Phase | Key Outputs Table |
|-------|-------------------|
| Research | Decision / Choice / Rationale for each technical decision |
| Data Model | Entity / Attributes / Relationships / Status for each entity |
| Contracts | Endpoint / Method / Description for each endpoint |

### Required Sections Checklist

- [ ] Summary metrics (phase, artifact path, completion status)
- [ ] What Was Produced (narrative of work done)
- [ ] Key Outputs (phase-specific table)
- [ ] Constitution Alignment (how decisions align with principles)
- [ ] Open Questions (unresolved items for supervisor)
- [ ] Roadmap Alignment (gap tracking, if roadmap exists)
- [ ] Resolved Markers (markers addressed in this phase)
- [ ] Ready for Review (self-assessment of artifact quality)

## Phase Quality Gates

### Research Phase Complete When

- [ ] All `[NEEDS CLARIFICATION]` markers from spec addressed
- [ ] Each decision has 2+ alternatives evaluated
- [ ] Trade-offs documented for each decision
- [ ] Constitution alignment verified
- [ ] Brownfield stack evaluated (if applicable)
- [ ] Roadmap gaps checked and noted
- [ ] Planner report filled completely

### Data Model Phase Complete When

- [ ] Every noun from requirements evaluated for entity status
- [ ] All entities have id, createdAt, updatedAt fields
- [ ] Relationships include cardinality and direction
- [ ] PII fields identified and marked
- [ ] State machines documented for stateful entities
- [ ] Traceability to requirements documented
- [ ] Planner report filled completely

### Contracts Phase Complete When

- [ ] Every user action mapped to an endpoint
- [ ] All endpoints have request/response schemas
- [ ] Error responses defined for all failure modes
- [ ] Schemas consistent with data model entities
- [ ] Quickstart.md contains authentication, user flows, error handling
- [ ] OpenAPI spec validates
- [ ] Planner report filled completely

## Common Mistakes

### Skipping Roadmap Check
Starting a phase without reading evolution-roadmap.md. Always check for roadmap existence before starting any phase.

### Leaving Markers Unresolved
Producing research.md while `[NEEDS CLARIFICATION]` markers remain. Search spec for all marker types before finalizing any artifact.

### Placeholder Quickstart Examples
Writing `curl -X POST /api/endpoint -d '{"key": "value"}'`. Use realistic data matching actual schema definitions.

### Empty Report Sections
Leaving "Open Questions" or "Constitution Alignment" blank. Every section gets content -- write "None identified" if genuinely empty.

### Phase Gate Skipping
Declaring a phase complete without checking the quality gate. Run the phase-specific checklist before reporting completion.
