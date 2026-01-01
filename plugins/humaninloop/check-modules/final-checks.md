# Final Validation Checks (Phase 3)

> Cross-artifact validation and full constitution sweep.
> Used by Validator Agent during Phase 3 of the plan workflow.
> This is the last validation before plan completion.

---

## Check Categories

### Cross-Artifact Consistency

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| FIN-001 | Entity name consistency | Entity names consistent across data-model.md and contracts/ | auto-resolve |
| FIN-002 | Attribute consistency | Attribute names and types consistent across artifacts | auto-resolve |
| FIN-003 | Research reflected | Research decisions reflected in data model and contracts | auto-resolve |
| FIN-004 | No contradictions | No contradictory statements between artifacts | auto-resolve |

### Traceability

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| FIN-005 | Requirements traced | All spec requirements (FR-xxx) traced to artifacts | auto-retry |
| FIN-006 | Criteria verifiable | All success criteria (SC-xxx) verifiable from plan | auto-retry |
| FIN-007 | User story coverage | User stories map to complete endpoint sets | auto-retry |

### Constitution Full Sweep

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| FIN-008 | All principles checked | All constitution principles have been checked across phases | escalate |
| FIN-009 | Violations documented | Any violations documented with justification | escalate |
| FIN-010 | Overrides recorded | Override approvals recorded in plan-context.md | escalate |

### Artifact Completeness

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| FIN-011 | research.md complete | Research artifact present and complete | auto-retry |
| FIN-012 | data-model.md complete | Data model artifact present and complete | auto-retry |
| FIN-013 | contracts/ complete | Contract artifacts present and complete | auto-retry |
| FIN-014 | quickstart.md complete | Quickstart artifact present and complete | auto-retry |
| FIN-015 | plan.md ready | Plan summary ready to be generated | auto-retry |

---

## Tier Behavior

| Tier | Behavior | Max Retries |
|------|----------|-------------|
| `auto-resolve` | Validator auto-fixes naming/consistency issues | N/A |
| `auto-retry` | Loop back to affected phase agent | 2 |
| `escalate` | Return to Supervisor for user decision | N/A |

---

## Gap Classification

| Priority | Checks | Rationale |
|----------|--------|-----------|
| Critical | FIN-005, FIN-008 | Missing traceability or unchecked principles are blocking |
| Important | FIN-001, FIN-002, FIN-003, FIN-006, FIN-007, FIN-009, FIN-010 | Quality issues to resolve before completion |
| Minor | FIN-004, FIN-011, FIN-012, FIN-013, FIN-014, FIN-015 | Can be auto-resolved; completeness is verifiable |

---

## Validation Process

```
1. Load ALL plan artifacts:
   - research.md
   - data-model.md
   - contracts/*.yaml
   - quickstart.md
2. Load spec.md for traceability validation
3. Load plan-context.md for registries and constitution results
4. For each check in order:
   a. Execute check logic
   b. If FAIL:
      - Classify gap priority
      - Assign tier behavior
      - Determine loop-back target (which phase/agent)
      - Add to gap queue
5. Compile full traceability chain
6. Return validation_report with:
   - total_checks
   - passed_count
   - gaps[] with priority, tier, loop_back_target
   - traceability_complete: boolean
   - result: pass | fail | partial
```

---

## Loop-Back Logic

When Phase 3 finds gaps, determine which phase to loop back to:

| Gap Type | Loop Back To |
|----------|--------------|
| Research-related (FIN-003) | Phase 0: Research |
| Entity/model issues (FIN-001, FIN-002) | Phase 1: Domain Model |
| Contract/endpoint issues (FIN-007) | Phase 2: Contracts |
| Traceability gaps (FIN-005, FIN-006) | Phase 1 or 2 depending on gap |
| Constitution issues (FIN-008, FIN-009, FIN-010) | Supervisor escalation |
| Completeness (FIN-011 to FIN-015) | Respective phase |

---

## Traceability Chain Compilation

On successful validation, populate index.md Plan Traceability:

```markdown
### Full Traceability Chain

| FR ID | Entity | Endpoint | Coverage |
|-------|--------|----------|----------|
| FR-001 | User | POST /auth/login | ✓ Full |
| FR-002 | User, Session | POST /auth/login, GET /auth/session | ✓ Full |
| FR-003 | Session | DELETE /auth/logout | ✓ Full |
| FR-004 | User | POST /auth/reset | ⚠ Partial |
```

---

## Constitution Summary

Compile constitution check results from all phases:

```markdown
| Phase | Principles | Result | Notes |
|-------|------------|--------|-------|
| 0 | Technology Choices | pass | - |
| 1 | Data Privacy | pass | PII fields encrypted |
| 2 | API Standards | pass | RESTful design |
| 3 | Full Sweep | pass | All principles validated |
```

---

## Example Gap Output

```json
{
  "gap_id": "G-FIN-005",
  "check_id": "FIN-005",
  "priority": "Critical",
  "tier": "auto-retry",
  "description": "FR-008 (Audit logging) has no traced entity or endpoint",
  "affected_fr": "FR-008",
  "loop_back_target": "Phase 1: Domain Model",
  "suggested_action": "Domain Model Agent should add AuditLog entity, then Contract Agent should add audit endpoint"
}
```

---

## Completion Criteria

Phase 3 validation passes when:

1. All Critical gaps resolved (count = 0)
2. All Important gaps resolved (count = 0)
3. Minor gaps logged as deferred (optional)
4. Traceability chain complete
5. Constitution full sweep passed or overrides approved
6. All artifacts present and complete
