# Gap Classification

Rules and algorithms for grouping gaps into focused clarification questions.

> **Core Skill Composition**: This skill extends prioritization-patterns from humaninloop-core.
> Grouping algorithms and staleness detection are defined in core; this file adds spec-specific
> clarification generation patterns.

---

## Gap Filtering

*Applies prioritization-patterns severity classification.*

**Only process Critical and Important gaps** - Minor gaps can be deferred.

```
gaps_to_process = gaps.critical + gaps.important
```

If `gaps_to_process` is empty, classification can skip - no clarifications needed.

---

## Grouping Rules

*See prioritization-patterns/GROUPING.md for the full grouping algorithm.*

Apply core grouping criteria in order:
1. Same FR reference
2. Same domain (auth, data, API)
3. Same section
4. Related concepts

**Spec-Specific Grouping Context:**
- FR references map to spec sections
- Domain extraction uses spec-defined domains
- CHK IDs link to checklist items for traceability

---

## Prioritization

*See prioritization-patterns/SEVERITY.md for severity classification.*

**Maximum 3 clarifications per iteration.** If more groups exist, prioritize by:
1. Critical priority first
2. Number of gaps in group
3. Impact on user stories (P1 > P2 > P3)

---

## Stale Detection

*See prioritization-patterns/STALENESS.md for detection algorithm.*

Apply staleness thresholds:
- 2 iterations: Warning flag
- 3+ iterations: Escalate to user

**Spec-Specific Escalation:**
```
if gap.stale_count >= 3:
  escalate_to_user("Gap {gap.id} unresolved after 3 iterations")
  # Add to spec with [KNOWN GAP] marker instead of blocking
```

---

## Question Generation (Spec-Specific)

This section is unique to specification clarifications.

### Single Gap in Group

```markdown
[NEEDS CLARIFICATION: C{iteration}.{number}]
**Question**: {gap.question}
**Options**:
1. {option_1}
2. {option_2}
3. {option_3}
**Source**: CHK{chk_id} validating FR-{fr_ref}
**Priority**: {Critical|Important}
```

### Multiple Gaps in Group

```markdown
[NEEDS CLARIFICATION: C{iteration}.{number}]
**Question**: Regarding {domain}, please clarify:
- {gap_1.question}
- {gap_2.question}
- {gap_3.question}
**Combined Options**:
For {sub_question_1}: {options}
For {sub_question_2}: {options}
**Source**: CHK{ids} validating FR-{refs}
**Priority**: {highest_priority_in_group}
```

### Clarification ID Format

| Format | Source | Example |
|--------|--------|---------|
| `Q-S{n}` | Spec writing phase | Q-S1, Q-S2 |
| `C{iter}.{n}` | Gap classification (Priority Loop) | C1.1, C2.3 |

---

## Smart Grouping Examples

### Example: Authentication Domain

**Input Gaps**:
```json
[
  {"chk_id": "CHK015", "fr_ref": "FR-003", "question": "What happens on auth failure?"},
  {"chk_id": "CHK016", "fr_ref": "FR-003", "question": "How many retries before lockout?"},
  {"chk_id": "CHK017", "fr_ref": "FR-004", "question": "Password reset flow undefined"}
]
```

**Output Clarification**:
```markdown
[NEEDS CLARIFICATION: C1.1]
**Question**: Regarding authentication error handling, please clarify:
- What should happen when authentication fails?
- How many failed attempts before account lockout?
- What is the password reset flow?
**Priority**: Critical (affects P1 user stories)
```

---

## State Updates (Spec-Specific)

### Gap Priority Queue Format

```markdown
| Priority | Gap ID | CHK Source | FR Reference | Question | Status |
|----------|--------|------------|--------------|----------|--------|
| Critical | G-001 | CHK015 | FR-003 | Auth failure handling | clarifying |
| Important | G-002 | CHK022 | FR-007 | Session timeout? | clarifying |
```

### Priority Loop State Format

```markdown
| Field | Value |
|-------|-------|
| **Loop Status** | clarifying |
| **Current Iteration** | {iteration} / 10 |
| **Last Activity** | {timestamp} |
```

### Traceability Matrix Update

```markdown
| FR ID | CHK IDs | Coverage Status | Notes |
|-------|---------|-----------------|-------|
| FR-003 | CHK015 | Gap Found | -> C1.1 created |
| FR-007 | CHK022 | Gap Found | -> C1.2 created |
```

---

## Output Contract

```json
{
  "success": true,
  "clarifications_needed": true,
  "clarifications": [
    {
      "id": "C1.1",
      "priority": "Critical",
      "domain": "authentication",
      "question": "What should happen when authentication fails?",
      "options": ["Return 401", "Redirect to login", "Lock account"],
      "source_gaps": ["G-001"],
      "source_chks": ["CHK015"],
      "fr_refs": ["FR-003"]
    }
  ],
  "deferred_minor_gaps": 5,
  "grouping_summary": {
    "original_gaps": 8,
    "after_grouping": 2
  }
}
```
