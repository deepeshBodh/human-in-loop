# Validation Principles

Core principles and self-validation checks for requirements quality checklists.

---

## The "Unit Tests for English" Philosophy

Checklists validate REQUIREMENTS quality, NOT implementation correctness.

### What This Means

| Validate | Do NOT Validate |
|----------|-----------------|
| Are requirements written clearly? | Does the code work? |
| Are all scenarios documented? | Does the feature function? |
| Can requirements be measured? | Do tests pass? |
| Are requirements consistent? | Is the UI correct? |

### The Litmus Test

Ask: "Can I answer this by reading the spec, without running the software?"

- **Yes** -> Valid checklist item
- **No** -> Implementation verification (prohibited)

---

## Required Question Format

All checklist items MUST be phrased as questions about the written requirements.

### Valid Patterns

```markdown
"Are [requirements] defined for [scenario]?"
"Is [term] quantified with specific criteria?"
"Are requirements consistent between [A] and [B]?"
"Can [criterion] be objectively measured?"
"Is [aspect] documented in the spec?"
```

### Question Structure

```markdown
- [ ] CHK### - {Question about requirements}? [{Quality Dimension}, {Reference}]
```

Components:
- `CHK###` - Unique identifier
- Question - Ends with `?`
- Quality Dimension - At least one from [DIMENSIONS.md](DIMENSIONS.md)
- Reference - `Spec §X.Y` or `Gap` or `FR-###`

---

## Quality Markers (Always Include)

Every checklist item MUST include at least one quality dimension tag:

| Marker | When to Use |
|--------|-------------|
| `[Completeness]` | Checking if requirements exist |
| `[Clarity]` | Checking if requirements are unambiguous |
| `[Consistency]` | Checking if requirements align |
| `[Measurability]` | Checking if criteria are testable |
| `[Coverage]` | Checking if scenarios are addressed |
| `[Edge Case]` | Checking boundary conditions |
| `[Gap]` | Indicating missing requirement |
| `[Ambiguity]` | Indicating vague language |

---

## Self-Validation Checks

Apply these checks before returning a checklist:

| ID | Check | Tier | Action on Fail |
|----|-------|------|----------------|
| QV-001 | Zero items test implementation behavior | auto-retry | Rewrite items |
| QV-002 | 100% items in question format | auto-retry | Reformat items |
| QV-003 | 100% items include quality dimension marker | auto-resolve | Add markers |
| QV-004 | 80%+ items have traceability reference | auto-retry | Add references |
| QV-005 | Item count <= 40 (after consolidation) | auto-resolve | Consolidate |
| QV-006 | State updates include gaps and traceability | auto-resolve | Add state |

### Tier Definitions

- **auto-resolve**: Fix automatically without retry
- **auto-retry**: Regenerate the failing items
- **escalate**: Report to user/workflow

---

## Verdict Determination

| Outcome | Condition |
|---------|-----------|
| **Pass** | All checks pass |
| **Partial** | Minor gaps auto-resolved |
| **Fail** | Critical or Important gaps unresolved -> retry before returning |

---

## Traceability Requirements

### Minimum Coverage

- **80% of items** must have traceability references
- References link to specific spec sections or identify gaps

### Reference Formats

| Format | Meaning |
|--------|---------|
| `Spec §2.1` | References spec section 2.1 |
| `FR-001` | References Functional Requirement 001 |
| `SC-001` | References Success Criterion 001 |
| `Gap` | Identifies missing requirement |
| `NFR-2` | References Non-Functional Requirement 2 |

### Example with Traceability

```markdown
- [ ] CHK015 - Are error messages defined for authentication failures? [Completeness, Gap]
- [ ] CHK016 - Is "fast response" quantified? [Clarity, Ambiguity, Spec §NFR-2]
- [ ] CHK017 - Can SC-001 success criterion be objectively verified? [Measurability, SC-001]
```

---

## Consolidation Rules

Apply when item count exceeds 40:

### Step 1: Prioritize by Risk/Impact

Use severity from prioritization-patterns:
1. Critical items (security, data integrity)
2. Important items (functionality, user experience)
3. Minor items (polish, edge cases)

### Step 2: Merge Near-Duplicates

Combine items checking the same requirement aspect:

```markdown
# Before
- [ ] CHK010 - Is password length specified? [Clarity]
- [ ] CHK011 - Is password complexity specified? [Clarity]

# After
- [ ] CHK010 - Are password requirements (length, complexity) specified? [Clarity, FR-005]
```

### Step 3: Consolidate Edge Cases

Group related edge cases into compound items:

```markdown
# Before
- [ ] CHK050 - Is empty input behavior defined?
- [ ] CHK051 - Is null input behavior defined?
- [ ] CHK052 - Is whitespace-only input behavior defined?

# After
- [ ] CHK050 - Are boundary behaviors defined for input (empty, null, whitespace)? [Edge Case]
```

### Step 4: Remove Lowest-Impact

If still over threshold, remove items with lowest impact score.
