# Gap Classification

Rules and algorithms for grouping gaps into focused clarification questions.

---

## Gap Filtering

**Only process Critical and Important gaps** - Minor gaps can be deferred.

```
gaps_to_process = gaps.critical + gaps.important
```

If `gaps_to_process` is empty, classification can skip - no clarifications needed.

---

## Grouping Rules

Group gaps by these criteria (in priority order):

1. **Same FR reference** - Gaps affecting the same requirement
2. **Same domain** - Gaps in same domain (auth, data, API, etc.)
3. **Same section** - Gaps in same spec section
4. **Related concepts** - Gaps about related topics (e.g., timeout + retry + error handling)

---

## Grouping Algorithm

```
for each gap in gaps_to_process:
  domain = extract_domain(gap.fr_ref, gap.question)

  if existing_group_matches(domain):
    add_to_group(gap)
  else:
    create_new_group(domain, gap)

# Merge small groups
for group in groups where len(group) == 1:
  if can_merge_with_related_group(group):
    merge_groups()
```

---

## Prioritization

**Maximum 3 clarifications per iteration.** If more groups exist, prioritize by:

1. Critical priority first
2. Number of gaps in group (more = higher priority)
3. Impact on user stories (P1 > P2 > P3)

---

## Question Generation

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

### Question ID Format

- `C{iteration}.{number}` - e.g., C1.1, C1.2, C1.3 for iteration 1
- Continues: C2.1, C2.2 for iteration 2
- Until loop completes

---

## Stale Detection

Track which gaps have appeared in previous iterations:

```
for each gap in gaps_to_process:
  if gap.id in previous_iteration_gaps:
    gap.stale_count++
    if gap.stale_count >= 3:
      mark_as_stale(gap)
      escalate_to_user("Gap {gap.id} unresolved after 3 iterations")
```

---

## Smart Grouping Examples

### Example 1: Authentication Domain Grouping

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

### Example 2: API Domain Grouping

**Input Gaps**:
```json
[
  {"chk_id": "CHK025", "fr_ref": "FR-010", "question": "Rate limiting not specified"},
  {"chk_id": "CHK026", "fr_ref": "FR-011", "question": "Error response format undefined"},
  {"chk_id": "CHK027", "fr_ref": "FR-010", "question": "Timeout behavior not specified"}
]
```

**Output Clarification**:
```markdown
[NEEDS CLARIFICATION: C1.2]
**Question**: Regarding API behavior, please clarify:
- What are the rate limiting thresholds?
- What is the standard error response format?
- What is the request timeout and retry behavior?
**Priority**: Important (affects API consistency)
```

---

## State Updates

### Update Gap Priority Queue

For each gap being converted to clarification:
```markdown
| Priority | Gap ID | CHK Source | FR Reference | Question | Status |
|----------|--------|------------|--------------|----------|--------|
| Critical | G-001 | CHK015 | FR-003 | Auth failure handling | clarifying |
| Important | G-002 | CHK022 | FR-007 | Session timeout? | clarifying |
```

### Update Priority Loop State

```markdown
| Field | Value |
|-------|-------|
| **Loop Status** | clarifying |
| **Current Iteration** | {iteration} / 10 |
| **Last Activity** | {timestamp} |
```

### Update Traceability Matrix

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
