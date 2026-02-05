---
name: validation-plan-artifacts
description: This skill MUST be invoked when the user says "review research", "review data model", "review contracts", "plan quality", "phase review", or "design gaps". SHOULD also invoke when user mentions "artifact review" or "planning validation".
---

# Reviewing Plan Artifacts

## Overview

Find gaps in planning artifacts and generate issues that need resolution before proceeding to the next phase. Focus on design completeness and quality, not implementation details. This skill provides phase-specific review criteria for the Devil's Advocate.

## When to Use

- Reviewing research.md after B0 phase completion
- Reviewing data-model.md after B1 phase completion
- Reviewing contracts/ after B2 phase completion
- Validating cross-artifact consistency before task generation
- When plan architect requests artifact review
- Quality gate checks before phase transitions

## When NOT to Use

- **Implementation code review** - Use code review tools instead
- **Task artifact review** - Use `humaninloop:validation-task-artifacts` instead
- **Specification review** - Use `humaninloop:analysis-specifications` instead
- **Constitution review** - Use `humaninloop:validation-constitution` instead
- **During active drafting** - Wait for artifact completion before review

## Review Focus by Phase

Each phase has specific checks to execute. The checks identify Critical, Important, and Minor issues.

| Phase | Focus Area | Key Checks |
|-------|------------|------------|
| A0 | Codebase Discovery | Coverage, entity/endpoint detection, collision assessment |
| B0 | Research | Marker resolution, alternatives, rationale quality |
| B1 | Data Model | Entity coverage, relationships, PII identification |
| B2 | Contracts | Endpoint coverage, schemas, error handling |
| B3 | Cross-Artifact | Alignment, consistency, traceability |

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

For phases after the first artifact (data-model, contracts), use incremental review to optimize time while preserving rigor.

### Full Review (New Artifact Only)

- Execute ALL phase-specific checks from PHASE-CHECKLISTS.md
- Document issues with full evidence
- This is the primary focus—no shortcuts

### Consistency Check (Previous Artifacts)

- Use the cross-artifact checklist in [PHASE-CHECKLISTS.md](references/PHASE-CHECKLISTS.md#cross-artifact-consistency)
- Do NOT re-read previous artifacts in full
- Spot-check: entity names, requirement IDs, decision references
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
| **New Artifact** | {artifact} - FULL REVIEW |
| **Previous Artifacts** | CONSISTENCY CHECK ONLY |

## New Artifact Issues

{Full issue documentation with evidence}

## Cross-Artifact Consistency

| Check | Status | Notes |
|-------|--------|-------|
| Entity names | Pass/Fail | {any mismatches} |
| Requirement IDs | Pass/Fail | {any gaps} |
| Decision alignment | Pass/Fail | {any contradictions} |

## Verdict

{ready / needs-revision / critical-gaps}
```

### Phase Application

| Phase | Full Review | Consistency Check |
|-------|-------------|-------------------|
| B0 (Research) | research.md | — (first artifact) |
| B1 (Data Model) | data-model.md | research.md (1-2 min) |
| B2 (Contracts) | contracts/, quickstart.md | research.md + data-model.md (2-3 min) |

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
