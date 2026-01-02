# Gap Filtering

Rules for filtering gaps before processing in the Priority Loop.

---

## The Filtering Rule

**Only process Critical and Important gaps** - Minor gaps can be deferred.

```
gaps_to_process = gaps.critical + gaps.important
gaps_deferred = gaps.minor
```

### Rationale

- **User fatigue prevention**: Too many clarifications overwhelm users
- **Focus on blockers**: Critical and Important gaps block spec completion
- **Incremental refinement**: Minor gaps can be addressed in later iterations

---

## Priority Classification

### Critical Gaps

Gaps that block understanding of core functionality.

**Signals**:
- Affects P1 user stories
- Missing fundamental requirement
- Security or data integrity impact
- Contradictory requirements

**Examples**:
```markdown
- "Authentication failure handling undefined" -> Critical (security, P1)
- "Payment processing requirements missing" -> Critical (core functionality)
- "User roles conflict between sections" -> Critical (contradiction)
```

### Important Gaps

Gaps that affect significant functionality but don't block core understanding.

**Signals**:
- Affects P2 user stories
- Ambiguous requirement needing clarification
- Missing edge case for main flow
- Performance requirement unquantified

**Examples**:
```markdown
- "Session timeout value unspecified" -> Important (significant UX impact)
- "'Fast response' not quantified" -> Important (ambiguity)
- "Error message format undefined" -> Important (affects UX)
```

### Minor Gaps

Polish, edge cases, and nice-to-have clarifications.

**Signals**:
- Affects only P3 user stories
- Edge case for rare scenario
- Formatting/style consistency
- Optional feature details

**Examples**:
```markdown
- "Loading spinner animation not specified" -> Minor (polish)
- "Behavior for 100+ simultaneous uploads" -> Minor (rare edge case)
- "Tooltip wording not defined" -> Minor (style)
```

---

## Filter Algorithm

```python
def filter_gaps(gaps):
    """
    Filter gaps to only Critical and Important.
    Returns tuple of (gaps_to_process, gaps_deferred)
    """
    gaps_to_process = []
    gaps_deferred = []

    for gap in gaps.critical:
        gaps_to_process.append(gap)

    for gap in gaps.important:
        gaps_to_process.append(gap)

    for gap in gaps.minor:
        gaps_deferred.append(gap)
        gap.status = "deferred"

    return (gaps_to_process, gaps_deferred)
```

---

## Early Exit Conditions

### No Gaps to Process

```python
if len(gaps_to_process) == 0:
    return {
        "clarifications_needed": False,
        "reason": "All gaps are Minor (deferred)",
        "deferred_count": len(gaps_deferred)
    }
```

### All Gaps Resolved

```python
if all(gap.status == "resolved" for gap in gaps_to_process):
    return {
        "clarifications_needed": False,
        "reason": "All Critical and Important gaps resolved",
        "ready_for_completion": True
    }
```

---

## Priority Mapping to User Stories

| Gap Priority | Maps To | Rationale |
|--------------|---------|-----------|
| Critical | P1 User Stories | Core functionality, must resolve |
| Important | P2 User Stories | Significant functionality |
| Minor | P3 User Stories | Nice-to-have, can defer |

### Example Mapping

```markdown
User Story US-001 (P1: Core authentication)
  └─> Gap G-001 (Critical): Auth failure handling undefined

User Story US-005 (P2: User preferences)
  └─> Gap G-005 (Important): Preference sync interval unspecified

User Story US-012 (P3: Customization)
  └─> Gap G-012 (Minor): Theme color options not documented
```

---

## Deferred Gap Handling

Deferred Minor gaps are logged but not processed:

```markdown
## Known Minor Gaps (Deferred)

| Gap ID | Description | FR Reference | Deferred At |
|--------|-------------|--------------|-------------|
| G-012 | Theme color options | FR-045 | Iteration 1 |
| G-015 | Animation timing | FR-052 | Iteration 1 |
```

These can be addressed in:
- Future iterations (if time permits)
- Post-completion refinement
- Implementation phase decisions
