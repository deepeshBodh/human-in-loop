---
name: validation-task-artifacts
description: This skill MUST be invoked when the user says "review task mapping", "review tasks", "validate cycles", or "check TDD structure". SHOULD also invoke when user mentions "task quality", "cycle review", "vertical slice", or "task artifact".
---

# Reviewing Task Artifacts

## Overview

Find gaps in task artifacts and generate issues that need resolution before proceeding to the next phase. Focus on vertical slice completeness, TDD structure, and traceability. This skill provides phase-specific review criteria for the Devil's Advocate.

## When to Use

- Reviewing task-mapping.md after mapping phase completes
- Validating tasks.md before implementation begins
- Cross-checking traceability between stories, cycles, and tasks
- Assessing TDD structure compliance in cycle definitions
- Generating advocate reports with classified issues
- Quality gate checks before implementation starts

## When NOT to Use

- **Plan artifact review** - **OPTIONAL:** Use `humaninloop:validation-plan-artifacts` instead
- **Implementation code review** - Use code review tools
- **Creating task artifacts** - This skill is for validation only
- **When tasks.md doesn't exist yet** - Wait for Task Architect to complete
- **Specification review** - **OPTIONAL:** Use `humaninloop:analysis-specifications` instead

## Review Focus by Phase

Each phase has specific checks to execute. The checks identify Critical, Important, and Minor issues.

| Phase | Focus Area | Key Checks |
|-------|------------|------------|
| Mapping | Story coverage | All P1/P2 stories mapped to cycles |
| Mapping | Slice quality | Cycles are true vertical slices |
| Mapping | Dependencies | Foundation vs feature correctly identified |
| Tasks | TDD structure | Test-first task ordering in each cycle |
| Tasks | Coverage | All cycles have implementation tasks |
| Tasks | Format | Task IDs, file paths, markers correct |
| Cross | Traceability | Stories -> Cycles -> Tasks chain complete |

See [PHASE-CHECKLISTS.md](references/PHASE-CHECKLISTS.md) for detailed phase-specific checklists and key questions.

## Issue Classification

Issues are classified by severity to determine appropriate action:

| Severity | Definition | Action |
|----------|------------|--------|
| **Critical** | Blocks progress; must resolve | Return to Task Architect |
| **Important** | Significant gap; should resolve | Flag for this iteration |
| **Minor** | Polish item; can defer | Note for later |

See [ISSUE-TEMPLATES.md](references/ISSUE-TEMPLATES.md) for severity classification rules, issue documentation formats, and report templates.

## Review Process

### Step 1: Gather Context

Read and understand:
- The artifact being reviewed (task-mapping.md or tasks.md)
- The spec requirements (user stories, acceptance criteria)
- Plan artifacts (for consistency checks)
- Previous task artifacts (for cross-phase checks)

### Step 2: Execute Checks

For each check in the phase-specific checklist:
1. Ask the question
2. Look for evidence in the artifact
3. If issue found, classify severity
4. Document the issue

### Step 3: Cross-Reference

- Check traceability (can trace story -> cycle -> tasks)
- Check consistency (mapping and tasks agree)
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

## Key Principles to Validate

### Vertical Slicing

- Cycles should deliver user value, not horizontal layers
- Each cycle should be independently testable
- Foundation cycles contain shared infrastructure
- Feature cycles can parallelize

### TDD Structure

- Every cycle starts with a test task
- Implementation follows the test
- Refactor and demo complete the cycle
- No implementation without tests

### Traceability

- Every P1/P2 story maps to at least one cycle
- Every cycle has corresponding tasks
- Every task has a specific file path
- Story labels link tasks to requirements

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

### Skipping Cross-Artifact Checks
❌ Reviewing task-mapping.md in isolation
✅ Always verify alignment with stories from spec and data model

### Over-Classification of Severity
❌ Marking formatting issues as "Critical"
✅ Reserve Critical for gaps that genuinely block implementation

### Missing Evidence in Issue Reports
❌ "The cycles are not vertical slices"
✅ "Cycle 2 groups all database tasks (tasks 2.1-2.4) without user-facing value - horizontal layer, not vertical slice"

### Not Verifying TEST Task Presence
❌ Assuming every cycle has proper TDD structure
✅ Explicitly check each cycle starts with a TEST: task before implementation

### Ignoring Traceability Gaps
❌ Accepting tasks without story labels
✅ Every task MUST trace back to a user story via cycle mapping

### Reviewing During Active Drafting
❌ Reviewing incomplete task artifacts mid-creation
✅ Wait for Task Architect to signal completion before validation
