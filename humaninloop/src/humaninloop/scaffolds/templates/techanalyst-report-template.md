# Technical Analyst Report

> Feature: {{feature_id}}
> Phase: {{phase}}
> Iteration: {{iteration}}
> Generated: {{timestamp}}

---

## Summary

| Metric | Value |
|--------|-------|
| **Phase** | {{phase}} |
| **Artifacts Produced** | {{artifacts_produced}} |
| **Completion** | {{completion_status}} |

---

## What Was Produced

{{production_summary}}

---

## Key Outputs

### Analysis Phase
<!-- If phase == analysis -->
| Metric | Count |
|--------|-------|
| Technical Requirements (TRs) | {{tr_count}} |
| Constraints | {{constraint_count}} |
| Decisions | {{decision_count}} |
| Non-Functional Requirements | {{nfr_count}} |
| FR Coverage | {{fr_coverage}} |

| TR ID | Source FR | Priority | Description |
|-------|----------|----------|-------------|
| {{tr_id}} | {{source_fr}} | {{priority}} | {{description}} |

### Design Phase
<!-- If phase == design -->
| Metric | Count |
|--------|-------|
| Entities | {{entity_count}} |
| Relationships | {{relationship_count}} |
| Endpoints | {{endpoint_count}} |
| Data Classifications | {{classification_count}} |
| Integration Points | {{integration_count}} |

---

## Constitution Alignment

{{constitution_alignment}}

---

## Open Questions

{{open_questions}}

---

## Ready for Review

{{ready_for_review}}
