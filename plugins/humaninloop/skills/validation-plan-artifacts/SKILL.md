---
name: validation-plan-artifacts
description: Review planning artifacts (research, data model, contracts) for quality and completeness. Use when reviewing plan phase outputs, finding gaps in design decisions, or when you see "review research", "review data model", "review contracts", "plan quality", or "phase review".
---

# Reviewing Plan Artifacts

## Purpose

Find gaps in planning artifacts and generate issues that need resolution before proceeding to the next phase. Focus on design completeness and quality, not implementation details. This skill provides phase-specific review criteria for the Devil's Advocate.

## Review Focus by Phase

Each phase has specific checks to execute. The checks identify Critical, Important, and Minor issues.

| Phase | Focus Area | Key Checks |
|-------|------------|------------|
| A0 | Codebase Discovery | Coverage, entity/endpoint detection, collision assessment |
| B0 | Research | Marker resolution, alternatives, rationale quality |
| B1 | Data Model | Entity coverage, relationships, PII identification |
| B2 | Contracts | Endpoint coverage, schemas, error handling |
| B3 | Cross-Artifact | Alignment, consistency, traceability |

See [PHASE-CHECKLISTS.md](PHASE-CHECKLISTS.md) for detailed phase-specific checklists and key questions.

## Issue Classification

Issues are classified by severity to determine appropriate action:

| Severity | Definition | Action |
|----------|------------|--------|
| **Critical** | Blocks progress; must resolve | Return to responsible agent |
| **Important** | Significant gap; should resolve | Flag for this iteration |
| **Minor** | Polish item; can defer | Note for later |

See [ISSUE-TEMPLATES.md](ISSUE-TEMPLATES.md) for severity classification rules, issue documentation formats, and report templates.

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
