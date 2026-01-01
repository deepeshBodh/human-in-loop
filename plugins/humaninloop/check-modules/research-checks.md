# Research Checks (Phase 0)

> Validation checks for research.md artifact.
> Used by Validator Agent during Phase 0 of the plan workflow.

---

## Check Categories

### Completeness Checks

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| RES-001 | All unknowns resolved | Every NEEDS CLARIFICATION from spec has a corresponding decision in research.md | auto-retry |
| RES-002 | Decisions documented | Each unknown has a documented decision with clear choice | auto-retry |
| RES-003 | Rationale provided | Each decision has rationale explaining why this choice was made | auto-retry |
| RES-004 | Alternatives listed | Alternatives considered are documented for each decision | auto-retry |

### Quality Checks

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| RES-005 | Technology appropriate | Decisions are appropriate for spec constraints and requirements | auto-resolve |
| RES-006 | No conflicts | No conflicting decisions (e.g., choosing both SQL and NoSQL for same data) | auto-resolve |
| RES-007 | Dependencies identified | Dependencies between technology choices are documented | auto-resolve |

### Constitution Alignment [phase:0]

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| RES-008 | Tech principles followed | Technology choices align with constitution Technology Choices principles | escalate |
| RES-009 | Deviations justified | Any deviations from principles have documented justification | escalate |

---

## Tier Behavior

| Tier | Behavior | Max Retries |
|------|----------|-------------|
| `auto-retry` | Research Agent retries with guidance | 2 |
| `auto-resolve` | Validator flags, Research Agent auto-fixes | N/A |
| `escalate` | Return to Supervisor for user decision | N/A |

---

## Gap Classification

| Priority | Checks | Rationale |
|----------|--------|-----------|
| Critical | RES-001, RES-008 | Unresolved unknowns block design; constitution violations require user approval |
| Important | RES-002, RES-003, RES-004, RES-009 | Quality issues that should be fixed but don't block |
| Minor | RES-005, RES-006, RES-007 | Can be auto-resolved or deferred |

---

## Validation Process

```
1. Load research.md
2. Load spec.md and extract NEEDS CLARIFICATION markers
3. For each check in order:
   a. Execute check logic
   b. If FAIL:
      - Classify gap priority
      - Assign tier behavior
      - Add to gap queue
4. Return validation_report with:
   - total_checks
   - passed_count
   - gaps[] with priority, tier, description
   - result: pass | fail | partial
```

---

## Example Gap Output

```json
{
  "gap_id": "G-RES-001",
  "check_id": "RES-001",
  "priority": "Critical",
  "tier": "auto-retry",
  "description": "Unknown 'session storage mechanism' from spec not resolved in research.md",
  "affected_fr": "FR-003",
  "suggested_action": "Research Agent should add decision for session storage"
}
```
