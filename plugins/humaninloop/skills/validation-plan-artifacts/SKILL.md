---
name: validation-plan-artifacts
description: This skill MUST be invoked when the user says "review research", "review data model", "review contracts", "plan quality", "phase review", or "design gaps". SHOULD also invoke when user mentions "artifact review" or "planning validation".
---

# Reviewing Plan Artifacts

## Overview

Find gaps in planning artifacts and generate issues that need resolution before proceeding. Focus on design completeness and quality, not implementation details. This skill provides phase-specific review criteria for artifact reviewers.

**Violating the letter of the rules is violating the spirit of the rules.**

## When to Use

- Reviewing requirements.md + constraints-and-decisions.md + nfrs.md after P1 (Analysis) phase completion
- Reviewing data-model.md + contracts/api.yaml + quickstart.md after P2 (Design) phase completion
- Validating cross-artifact consistency before task generation
- Quality gate checks before phase transitions

## When NOT to Use

- **Implementation code review** — Use code review tools instead
- **Task artifact review** — Use `humaninloop:validation-task-artifacts` instead
- **Specification review** — Use `humaninloop:analysis-specifications` instead
- **Constitution review** — Use `humaninloop:validation-constitution` instead
- **During active drafting** — Wait for artifact completion before review

## Review Focus by Phase

Each phase has specific checks to execute. The checks identify Critical, Important, and Minor issues.

| Phase | Focus Area | Key Checks |
|-------|------------|------------|
| A0 | Codebase Discovery | Coverage, entity/endpoint detection, collision assessment |
| P1 | Analysis | FR coverage, orphan TRs, testable criteria, sourced constraints, decision alternatives, NFR measurability |
| P2 | Design | Entity coverage, relationships, data sensitivity, endpoint coverage, schemas, error handling, integration boundaries |
| P3 | Cross-Artifact | Alignment, consistency, traceability |

See [PHASE-CHECKLISTS.md](references/PHASE-CHECKLISTS.md) for detailed phase-specific checklists and key questions.

## Issue Classification

Issues are classified by severity to determine appropriate action:

| Severity | Definition | Action |
|----------|------------|--------|
| **Critical** | Blocks progress; must resolve | Return to responsible agent |
| **Important** | Significant gap; should resolve | Flag for this iteration |
| **Minor** | Polish item; can defer | Note for later |

See [ISSUE-TEMPLATES.md](references/ISSUE-TEMPLATES.md) for severity classification rules, issue documentation formats, and report templates.

## Review Process

### Step 1: Gather Context

Read and understand:
- The artifact being reviewed
- The spec requirements it should satisfy
- Previous artifacts (for consistency checks)
- Constitution principles (for compliance)

### Step 2: Execute Checks

For each check in the phase-specific checklist:
1. Ask the question
2. Look for evidence in the artifact
3. If issue found, classify severity
4. Document the issue

### Step 3: Cross-Reference

- Check traceability (can trace requirement -> artifact)
- Check consistency (artifacts agree with each other)
- Check completeness (nothing obviously missing)

### Step 4: Generate Report

- Classify verdict based on issues found
- Document all issues with evidence
- Provide specific, actionable suggestions
- Acknowledge what was done well

## Incremental Review Mode

For Phase P2 (Design), use incremental review to optimize time while preserving rigor.

### Full Review (New Artifacts Only)

- Execute ALL phase-specific checks from PHASE-CHECKLISTS.md
- Document issues with full evidence
- This is the primary focus — no shortcuts

### Consistency Check (Previous Artifacts)

- Use the cross-artifact checklist in [PHASE-CHECKLISTS.md](references/PHASE-CHECKLISTS.md#cross-artifact-consistency)
- Do NOT re-read previous artifacts in full
- Spot-check: entity names, requirement IDs, decision references, constraint alignment
- Flag only inconsistencies between artifacts
- **Time budget**: 1-2 minutes per previous artifact

### When to Escalate to Full Re-Review

- If 2+ consistency issues found → re-read that specific artifact
- If contradictions detected → flag for supervisor
- If unsure → note uncertainty in report, recommend targeted review

### Report Format (Incremental Mode)

```markdown
## Review Summary

| Aspect | Status |
|--------|--------|
| **New Artifacts** | {artifacts} - FULL REVIEW |
| **Previous Artifacts** | CONSISTENCY CHECK ONLY |

## New Artifact Issues

{Full issue documentation with evidence}

## Cross-Artifact Consistency

| Check | Status | Notes |
|-------|--------|-------|
| Entity names match TRs | Pass/Fail | {any mismatches} |
| Schemas match data model | Pass/Fail | {any gaps} |
| Decisions honored in design | Pass/Fail | {any contradictions} |
| Sensitivity annotations present | Pass/Fail | {any missing} |
| Integration boundaries documented | Pass/Fail | {any missing} |

## Verdict

{ready / needs-revision / critical-gaps}
```

### Phase Application

| Phase | Full Review | Consistency Check |
|-------|-------------|-------------------|
| P1 (Analysis) | requirements.md, constraints-and-decisions.md, nfrs.md | — (first phase) |
| P2 (Design) | data-model.md, contracts/api.yaml, quickstart.md | requirements.md + constraints-and-decisions.md + nfrs.md (2-3 min) |

---

## Verdict Criteria

| Verdict | Criteria |
|---------|----------|
| **ready** | Zero Critical, zero Important issues |
| **needs-revision** | 1-3 Important issues, fixable in one iteration |
| **critical-gaps** | 1+ Critical or 4+ Important issues |

## Quality Checklist

Before finalizing review, verify:

- [ ] All phase-specific checks executed
- [ ] Issues properly classified by severity
- [ ] Evidence cited for each issue
- [ ] Suggested fixes are actionable
- [ ] Verdict matches issue severity
- [ ] Cross-artifact concerns noted
- [ ] Strengths acknowledged

## Common Mistakes

### Over-Classification of Severity
❌ Marking style issues as "Critical"
✅ Reserve Critical for issues that genuinely block progress

### Missing Evidence
❌ "The data model is incomplete"
✅ "The data model is missing the User entity referenced in FR-003"

### Vague Suggestions
❌ "Fix the contracts"
✅ "Add error response schema for 404 case in GET /users/{id}"

### Reviewing Implementation Details
❌ Commenting on code patterns, variable names, or framework choices
✅ Focus on design completeness, traceability, and consistency

### Skipping Cross-Artifact Checks
❌ Reviewing only the new artifact in isolation
✅ Always verify consistency with previous phase artifacts

### Excessive Re-Reading
❌ Re-reading all previous artifacts in full for every review
✅ Use incremental review mode with targeted consistency checks

## Red Flags - STOP and Restart Properly

If you notice yourself thinking any of these, STOP immediately:

- "This case is different because..." — It is not. Run the checklist.
- "I'm following the spirit, not the letter" — The letter IS the spirit.
- "The artifacts look good enough" — Good enough is not ready. Evidence or rejection.
- "I'll skip cross-artifact checks, the previous review was thorough" — Previous reviews do not guarantee current consistency.
- "This severity is only Minor, not Important" — If you are rationalizing severity DOWN, it is probably the higher level.
- "The reviewer already checked this" — Unless you have evidence of a prior review in this iteration, it was not checked.
- "I'll note it but not block on it" — If it meets Critical or Important criteria, it blocks. Period.

## Common Rationalizations

| Rationalization | Counter |
|----------------|---------|
| "The spec was vague, so the artifact can be vague" | Vagueness in spec is a gap to flag, not permission to propagate. |
| "This is a minor feature, full review is overkill" | Scale of feature does not change the review process. Every artifact gets every applicable check. |
| "Time pressure means we should skip cross-artifact checks" | Cross-artifact inconsistencies caught now save days of rework later. |
| "The author is senior, they know what they're doing" | Author seniority is irrelevant. Evidence-based review only. |
| "I already found enough issues" | Finding issues is not a quota. Run every check, document every finding. |
| "This check doesn't apply to this type of feature" | If the check is in the phase checklist, it applies. Flag as N/A with justification if genuinely inapplicable. |
| "The constraint is obvious, it doesn't need documentation" | Obvious constraints are the ones most often violated. Document them. |
