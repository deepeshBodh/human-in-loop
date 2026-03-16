---
type: plan-feasibility-review
artifact: "{artifact_path}"
iteration: 1
created: "{timestamp}"
updated: "{timestamp}"
---

# Feasibility Intersection Review

> Principal Architect review of cross-artifact contradictions.
> Generated during plan workflow.

---

## Review Summary

| Field | Value |
|-------|-------|
| **Artifacts Reviewed** | `{artifact_paths}` |
| **Reviewed** | {timestamp} |
| **Verdict** | `{feasible | infeasible | needs-revision}` |

---

## Verdict: `{verdict}`

{One-sentence explanation of the verdict}

---

## Cross-Artifact Contradictions

> Impossible combinations that no single artifact reveals in isolation.

| # | Artifact A | Artifact B | Contradiction | Severity | Suggested Resolution |
|---|-----------|-----------|---------------|----------|----------------------|
| 1 | {artifact + ID} | {artifact + ID} | {description of conflict} | {Critical / Important} | {specific action} |

{If no contradictions: "No cross-artifact contradictions found."}

---

## Constraint-Decision Conflicts

> Technology choices that violate stated hard constraints.

| Constraint | Decision | Conflict | Resolution |
|------------|----------|----------|------------|
| {C-XXX}: {name} | {D-XXX}: {name} | {how they conflict} | {action to resolve} |

{If none: "No constraint-decision conflicts found."}

---

## NFR-Constraint Impossibilities

> Quality targets that cannot be met given stated constraints or chosen technologies.

| NFR | Constraint/Decision | Why Impossible | Resolution |
|-----|---------------------|----------------|------------|
| {NFR-XXX}: {target} | {C-XXX or D-XXX}: {name} | {why target is unachievable} | {relax NFR / change decision / escalate} |

{If none: "No NFR-constraint impossibilities found."}

---

## Strengths Noted

- {Strength 1 — what was done well}
- {Strength 2 — what was done well}

---

## Next Steps

Based on the verdict:

- **If `feasible`**: Proceed to Devil's Advocate completeness review
- **If `needs-revision`**: Re-invoke Technical Analyst with contradictions above
- **If `infeasible`**: Escalate to supervisor for user decision

---
