---
name: validation-expertise
description: Patterns for quality validation and gap classification. Use when validating artifacts against quality criteria, classifying issues by severity, or deciding resolution strategies. Applies to any quality assurance or review task.
---

# Validation Expertise

## Purpose

Provide systematic approaches for validating artifacts against quality criteria, classifying gaps by severity, and determining appropriate resolution strategies. These patterns apply to any domain requiring quality assurance.

## Core Principles

1. **Criteria-Driven**: Validate against explicit, defined checks
2. **Severity Classification**: Not all issues are equal
3. **Tiered Resolution**: Match response to severity
4. **Traceable Gaps**: Every issue has ID, description, status
5. **Clear Verdicts**: Pass, fail, or partial—never ambiguous

## Validation Execution Pattern

### Phase 1: Load Criteria

Before validating, ensure you have:
- **Check definitions**: What to validate
- **Tier assignments**: How to handle failures
- **Priority classifications**: How to rank issues

### Phase 2: Execute Checks

For each check:

```
1. Parse check definition (ID, description, tier)
2. Execute check logic against artifact
3. Record result: PASS or FAIL
4. If FAIL: classify priority, assign tier, add to gap queue
```

### Phase 3: Determine Verdict

| Verdict | Condition |
|---------|-----------|
| **Pass** | 0 Critical, 0 Important gaps |
| **Partial** | 0 Critical, >0 Important (all auto-resolved) |
| **Fail** | >0 Critical OR >0 Important (unresolved) |

## Gap Classification Pattern

### Priority Levels

| Priority | Description | Examples |
|----------|-------------|----------|
| **Critical** | Blocks downstream work; foundational issue | Missing required entity, security violation |
| **Important** | Should be fixed before proceeding | Incomplete validation rules, missing edge cases |
| **Minor** | Can be deferred or auto-resolved | Style issues, optimization opportunities |

### Classification Questions

Ask these to determine priority:

1. **Does this block the next step?** → Critical if yes
2. **Does this affect correctness?** → Important if yes
3. **Is this about polish/optimization?** → Minor if yes

## Tiered Resolution Pattern

### Tier Definitions

| Tier | When to Use | Behavior |
|------|-------------|----------|
| **auto-resolve** | Simple, mechanical fixes | Fix immediately, log action |
| **auto-retry** | Needs rework by original agent | Return with guidance, max 2 retries |
| **escalate** | Requires human judgment | Prepare question, wait for input |

### Tier Assignment Rules

```
IF check is objective AND fix is deterministic:
  tier = auto-resolve
ELSE IF check is objective AND fix requires context:
  tier = auto-retry
ELSE IF check involves judgment OR policy:
  tier = escalate
```

### Resolution Flow

```
┌─────────────┐
│ Gap Found   │
└──────┬──────┘
       ▼
  ┌────────────┐
  │ What tier? │
  └────┬───────┘
       │
  ┌────┴────┬──────────┐
  ▼         ▼          ▼
auto-    auto-      escalate
resolve  retry
  │         │          │
  ▼         ▼          ▼
Fix it   Return     Prepare
& log    with       question
         guidance   & wait
```

## Gap Queue Pattern

### Gap Entry Format

```markdown
| Priority | ID | Check | Description | Tier | Status |
|----------|-----|-------|-------------|------|--------|
| Critical | G-001 | CHK-005 | Missing User entity | auto-retry | pending |
```

### Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Not yet addressed |
| `in_progress` | Being worked on |
| `resolved` | Fixed, awaiting re-validation |
| `escalated` | Waiting for human input |
| `accepted` | Closed as won't-fix (with justification) |

## Validation Report Pattern

### Report Structure

```markdown
## Validation Report

**Artifact**: {artifact_name}
**Checks Executed**: {count}
**Verdict**: {pass|partial|fail}

### Summary
- Passed: {count}
- Failed: {count}
  - Critical: {count}
  - Important: {count}
  - Minor: {count}

### Gaps Found

#### Critical
{list or "None"}

#### Important
{list or "None"}

#### Minor
{list or "None"}

### Resolution Actions
- Auto-resolved: {count} ({list})
- Pending retry: {count} ({list})
- Escalated: {count} ({list})

### Next Action
{proceed|retry|escalate} - {reason}
```

## Check Definition Pattern

### Check Format

```markdown
| ID | Check | Description | Tier |
|----|-------|-------------|------|
| CHK-001 | {name} | {what it validates} | {auto-resolve|auto-retry|escalate} |
```

### Good Check Examples

| ID | Check | Description | Tier |
|----|-------|-------------|------|
| CHK-001 | Required fields | All required fields are present | auto-resolve |
| CHK-002 | Type consistency | Field types match schema | auto-retry |
| CHK-003 | Security review | No sensitive data exposed | escalate |

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Vague checks** | Can't objectively evaluate | Make checks specific and testable |
| **All critical** | Nothing is prioritized | Use full priority range |
| **Skip auto-resolve** | Manual work for trivial fixes | Automate mechanical fixes |
| **Silent failures** | Issues not tracked | Log every gap |
| **Infinite retry** | Never escalates | Cap retries, then escalate |

## When to Use These Patterns

- Validating any artifact against quality criteria
- Reviewing code, documents, or designs
- Building validation into automated workflows
- Triaging issues in any domain
- Designing quality gates
