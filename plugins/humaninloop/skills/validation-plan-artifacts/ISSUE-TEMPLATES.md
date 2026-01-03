# Issue Templates and Classification

This reference file contains issue documentation formats, severity classification rules, and report templates for plan artifact reviews.

## Severity Levels

| Severity | Definition | Action |
|----------|------------|--------|
| **Critical** | Blocks progress; must resolve | Return to responsible agent |
| **Important** | Significant gap; should resolve | Flag for this iteration |
| **Minor** | Polish item; can defer | Note for later |

## Classification Rules

```
CRITICAL if:
- Missing entity/endpoint from requirements
- Unresolved NEEDS CLARIFICATION marker
- No alternatives considered for major decision
- Security/privacy issue (unmarked PII, etc.)
- Broken traceability (can't trace FR to implementation)

IMPORTANT if:
- Missing validation rules
- Incomplete error handling
- Weak rationale documentation
- State machine gaps
- Brownfield misalignment

MINOR if:
- Naming inconsistency
- Missing examples
- Documentation formatting
- Non-critical missing details
```

---

## Issue Documentation Format

### Individual Issue Template

```markdown
### Issue: [Short description]

**Severity**: Critical | Important | Minor
**Phase**: A0 | B0 | B1 | B2 | B3
**Artifact**: [Which file has the issue]
**Check Failed**: [Which review check]

**Problem**:
[What is wrong or missing]

**Evidence**:
[Where this gap appears - cite requirements or artifacts]

**Impact**:
[What happens if not resolved]

**Suggested Fix**:
[How the responsible agent should address this]
```

### Issue Table Format

```markdown
## Issues Found

| # | Severity | Phase | Description | Artifact | Suggested Action |
|---|----------|-------|-------------|----------|------------------|
| 1 | Critical | B1 | Session entity missing expiresAt | data-model.md | Add expiresAt timestamp |
| 2 | Important | B2 | No 429 error for login | contracts/ | Add rate limit response |
| 3 | Minor | B2 | Inconsistent path naming | contracts/ | Standardize to kebab-case |
```

---

## Advocate Report Format

```markdown
## Plan Artifact Review: {Phase Name}

**Artifact Reviewed**: {file path}
**Reviewer**: Devil's Advocate
**Date**: {timestamp}

---

### Verdict: [ready | needs-revision | critical-gaps]

---

### Critical Issues

[Issues that MUST be resolved before proceeding]

| # | Issue | Evidence | Suggested Fix |
|---|-------|----------|---------------|
| 1 | [Description] | [Source] | [Action] |

---

### Important Issues

[Issues that SHOULD be addressed in this iteration]

| # | Issue | Evidence | Suggested Fix |
|---|-------|----------|---------------|

---

### Minor Issues

[Polish items that can be deferred]

| # | Issue | Suggested Fix |
|---|-------|---------------|

---

### Strengths Noted

[What was done well - acknowledge good work]

- [Strength 1]
- [Strength 2]

---

### Recommended Actions

1. [Specific action for responsible archetype]
2. [Specific action for responsible archetype]

---

### Cross-Artifact Concerns

[Issues that span multiple artifacts - for final validation]

- [Concern 1]
- [Concern 2]
```

---

## Verdict Criteria

### ready

All of the following:
- Zero Critical issues
- Zero Important issues (or all auto-resolved)
- Minor issues documented for future

### needs-revision

Any of the following:
- 1-3 Important issues to resolve
- Minor issues affecting usability
- Gaps that can be fixed in one iteration

### critical-gaps

Any of the following:
- 1+ Critical issues
- 4+ Important issues
- Missing major artifact section
- Unrecoverable in single iteration

---

## Anti-Patterns to Avoid

- **Implementation focus**: Review design, not code details
- **Vague issues**: "Could be better" - specify what and how
- **Severity inflation**: Not everything is Critical
- **Missing evidence**: Issues need citations to artifacts
- **No suggestions**: Every issue needs a path to resolution
- **Ignoring strengths**: Acknowledge good work
- **Rubber stamping**: Being too agreeable defeats the purpose
