# Issue Classification and Templates

This reference file provides severity classification rules, issue documentation formats, and report templates for task artifact reviews.

## Severity Classification

### Critical Issues

Issues that block progress or fundamentally undermine the artifact's purpose.

| Category | Examples |
|----------|----------|
| Missing coverage | P1/P2 story not mapped to any cycle |
| Structural violation | Horizontal slicing instead of vertical |
| TDD violation | Implementation tasks before test tasks |
| Missing foundation | No foundation cycles identified |
| Broken traceability | Cannot trace story to cycle to tasks |
| Missing file paths | Tasks without specific file locations |

**Action**: Must resolve before proceeding. Return to Task Architect.

### Important Issues

Significant gaps that should be resolved but don't fundamentally break the artifact.

| Category | Examples |
|----------|----------|
| Quality gaps | Vague checkpoint descriptions |
| Marker issues | Missing [P] markers on parallel cycles |
| Sizing issues | Cycles too large or too small |
| Dependency issues | Unnecessary inter-cycle dependencies |
| Format issues | Wrong task ID format |
| Brownfield gaps | Missing [EXTEND]/[MODIFY] markers |

**Action**: Flag for this iteration. Should fix before proceeding.

### Minor Issues

Polish items that can be deferred without significant impact.

| Category | Examples |
|----------|----------|
| Style | Inconsistent capitalization |
| Documentation | Missing optional descriptions |
| Organization | Suboptimal cycle ordering |
| Naming | Non-descriptive cycle titles |

**Action**: Note for later. Can proceed with these unresolved.

## Issue Documentation Format

### Standard Issue Format

```markdown
**Issue {ID}**: {Brief title}

- **Check**: {Which check triggered this}
- **Severity**: {Critical/Important/Minor}
- **Evidence**: {Specific quote or reference from artifact}
- **Impact**: {Why this matters}
- **Suggested Fix**: {Actionable recommendation}
```

### Example Issues

#### Critical Issue

```markdown
**Issue TM-001**: User story US-2 not mapped to any cycle

- **Check**: Story coverage
- **Severity**: Critical
- **Evidence**: task-mapping.md contains cycles for US-1, US-3, US-4 but no mention of US-2
- **Impact**: US-2 (P1 priority) will not be implemented
- **Suggested Fix**: Add a cycle for US-2 "Task completion" covering the mark-complete functionality
```

#### Important Issue

```markdown
**Issue TT-003**: Cycle 4 is horizontally sliced

- **Check**: Vertical slice validation
- **Severity**: Important
- **Evidence**: Cycle 4 creates "all service classes" without corresponding tests or endpoints
- **Impact**: Nothing testable until later cycles complete; violates vertical slice principle
- **Suggested Fix**: Restructure Cycle 4 to include test, service, and endpoint for one specific behavior
```

#### Minor Issue

```markdown
**Issue TT-007**: Inconsistent cycle title capitalization

- **Check**: Format consistency
- **Severity**: Minor
- **Evidence**: "Cycle 3: task Priority" vs "Cycle 4: Task Filtering"
- **Impact**: Visual inconsistency, no functional impact
- **Suggested Fix**: Standardize to title case: "Task Priority"
```

## Report Templates

### Mapping Review Report

```markdown
# Advocate Report: Mapping Review

## Summary

| Metric | Value |
|--------|-------|
| **Phase** | Mapping |
| **Artifact** | {path to task-mapping.md} |
| **Verdict** | {ready/needs-revision/critical-gaps} |

## Checks Executed

| Check | Result | Issue |
|-------|--------|-------|
| Story coverage | {pass/fail} | {issue ID or -} |
| Cycle identification | {pass/fail} | {issue ID or -} |
| Foundation separation | {pass/fail} | {issue ID or -} |
| Feature parallelization | {pass/fail} | {issue ID or -} |
| Dependency accuracy | {pass/fail} | {issue ID or -} |
| Slice sizing | {pass/fail} | {issue ID or -} |
| Traceability | {pass/fail} | {issue ID or -} |

## Issues Found

### Critical ({count})

{List each critical issue using standard format}

### Important ({count})

{List each important issue using standard format}

### Minor ({count})

{List each minor issue using standard format}

## Strengths

{What was done well in this artifact}

## Verdict

{Explanation of verdict with recommended next steps}
```

### Tasks Review Report

```markdown
# Advocate Report: Tasks Review

## Summary

| Metric | Value |
|--------|-------|
| **Phase** | Tasks |
| **Artifact** | {path to tasks.md} |
| **Verdict** | {ready/needs-revision/critical-gaps} |

## Checks Executed

| Check | Result | Issue |
|-------|--------|-------|
| Cycle coverage | {pass/fail} | {issue ID or -} |
| TDD structure | {pass/fail} | {issue ID or -} |
| File paths | {pass/fail} | {issue ID or -} |
| Task IDs | {pass/fail} | {issue ID or -} |
| Story labels | {pass/fail} | {issue ID or -} |
| Brownfield markers | {pass/fail} | {issue ID or -} |
| Parallel markers | {pass/fail} | {issue ID or -} |
| Checkpoints | {pass/fail} | {issue ID or -} |
| Dependencies | {pass/fail} | {issue ID or -} |

## Issues Found

### Critical ({count})

{List each critical issue using standard format}

### Important ({count})

{List each important issue using standard format}

### Minor ({count})

{List each minor issue using standard format}

## Strengths

{What was done well in this artifact}

## Verdict

{Explanation of verdict with recommended next steps}
```

## Verdict Decision Tree

```
Are there Critical issues?
├── Yes → verdict: critical-gaps
└── No → How many Important issues?
          ├── 0 → verdict: ready
          ├── 1-3 → verdict: needs-revision
          └── 4+ → verdict: critical-gaps
```

## Issue ID Conventions

| Phase | Prefix | Example |
|-------|--------|---------|
| Mapping | TM- | TM-001, TM-002 |
| Tasks | TT- | TT-001, TT-002 |
| Cross-artifact | TX- | TX-001, TX-002 |
