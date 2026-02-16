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

### Core Phase
<!-- If phase == core -->
| Metric | Count |
|--------|-------|
| Technical Requirements (TRs) | {{tr_count}} |
| Constraints | {{constraint_count}} |
| FR Coverage | {{fr_coverage}} |

| TR ID | Source FR | Priority | Description |
|-------|----------|----------|-------------|
| {{tr_id}} | {{source_fr}} | {{priority}} | {{description}} |

### Supplementary Phase
<!-- If phase == supplementary -->
| Metric | Count |
|--------|-------|
| Non-Functional Requirements | {{nfr_count}} |
| Integration Points | {{integration_count}} |
| Data Sensitivity Classifications | {{ds_count}} |

| NFR ID | Category | Target | Measurement |
|--------|----------|--------|-------------|
| {{nfr_id}} | {{category}} | {{target}} | {{measurement}} |

---

## Constitution Alignment

{{constitution_alignment}}

---

## Open Questions

{{open_questions}}

---

## Ready for Review

{{ready_for_review}}
