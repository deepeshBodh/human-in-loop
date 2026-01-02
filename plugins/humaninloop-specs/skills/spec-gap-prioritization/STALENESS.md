# Stale Gap Detection

Rules for detecting and handling gaps that remain unresolved across iterations.

---

## Staleness Thresholds

| Iterations | Status | Action |
|------------|--------|--------|
| 1 | Normal | Process normally |
| 2 | Warning | Flag for attention |
| 3+ | Stale | Escalate to user |

---

## Detection Algorithm

```python
def detect_stale_gaps(gap_priority_queue, current_iteration):
    """
    Detect gaps that have been unresolved for too long.
    Returns list of stale gaps requiring escalation.
    """
    stale_gaps = []
    warning_gaps = []

    for gap in gap_priority_queue:
        if gap.status in ["pending", "clarifying"]:
            stale_count = current_iteration - gap.first_seen_iteration

            if stale_count >= 3:
                gap.stale_count = stale_count
                stale_gaps.append(gap)
            elif stale_count == 2:
                warning_gaps.append(gap)

    return {
        "stale": stale_gaps,
        "warning": warning_gaps
    }
```

---

## Tracking Stale Count

The Gap Priority Queue tracks stale count:

```markdown
| Priority | Gap ID | CHK Source | FR Reference | Status | First Seen | Stale Count |
|----------|--------|------------|--------------|--------|------------|-------------|
| Critical | G-001 | CHK015 | FR-003 | clarifying | Iter 1 | 2 |
| Important | G-002 | CHK022 | FR-007 | pending | Iter 1 | 2 |
| Critical | G-003 | CHK018 | FR-004 | clarifying | Iter 2 | 1 |
```

---

## Escalation Protocol

When a gap reaches stale threshold (3+ iterations):

### Step 1: Mark as Escalated

```python
gap.status = "escalated"
gap.escalation_reason = f"Unresolved after {gap.stale_count} iterations"
```

### Step 2: Generate Escalation Message

```markdown
**Stale Gaps Detected**

The following gaps have remained unresolved for 3+ iterations:

| Gap ID | Question | Attempts | Last Answer |
|--------|----------|----------|-------------|
| G-001 | Auth failure handling? | 3 | "Show error message" |

This may indicate:
1. The question needs rephrasing
2. The answer needs more detail
3. This is a genuine ambiguity that should be documented
```

### Step 3: Present Options to User

```markdown
Options:
1. **Provide Different Answer**: Re-attempt with more specific guidance
2. **Accept as Known Gap**: Document as [KNOWN GAP] in spec and continue
3. **Manual Edit**: Stop workflow and edit spec.md directly
```

---

## Spec-Specific Escalation

### [KNOWN GAP] Marker

When user chooses to accept a stale gap:

```markdown
# In spec.md
[KNOWN GAP: G-001]
**Issue**: Authentication failure handling not fully specified
**Reason**: Deferred to implementation phase
**Decision**: Development team will propose solution during implementation
**Documented**: Iteration 3, 2024-01-15
```

### Update Gap Priority Queue

```markdown
| Priority | Gap ID | Status | Resolution |
|----------|--------|--------|------------|
| Critical | G-001 | known_gap | Documented for implementation |
```

---

## Warning Handling (2 Iterations)

For gaps at 2 iterations, add a warning flag:

```markdown
[CLARIFICATION: C3.1] ⚠️ (Attempt 2 of 3)
**Question**: What should happen on authentication failure?
**Previous Answer**: "Show error message"
**Why Still Open**: Answer too vague - need specific error codes and messages

Please provide more specific details.
```

---

## Preventing Staleness

### During Question Generation

Make questions more specific if previous answer was insufficient:

```python
def refine_question(gap, previous_answer):
    """
    Refine question based on insufficient previous answer.
    """
    if gap.stale_count >= 2:
        return {
            "question": gap.original_question,
            "context": f"Previous answer was: '{previous_answer}'",
            "guidance": "Please provide more specific details, such as:",
            "suggestions": generate_specific_suggestions(gap)
        }
```

### Example Refinement

```markdown
# Iteration 1
Question: What should happen on authentication failure?
Answer: "Show error message"

# Iteration 2 (refined)
Question: What should happen on authentication failure?
Previous Answer: "Show error message"
Please specify:
- What error message text?
- Where should it display?
- Should the form be cleared?
- How many retries before lockout?
```

---

## Stale Detection in Index.md

Track staleness in Priority Loop State:

```markdown
## Priority Loop State

| Field | Value |
|-------|-------|
| **Loop Status** | clarifying |
| **Current Iteration** | 3 / 10 |
| **Stale Gaps** | 1 (G-001) |
| **Warning Gaps** | 2 (G-005, G-008) |
| **Last Activity** | 2024-01-15T10:30:00Z |
```

---

## Termination Due to Staleness

Staleness can trigger workflow termination:

```python
def check_stale_termination(stale_gaps, user_response):
    """
    Check if staleness should terminate workflow.
    """
    if len(stale_gaps) > 0:
        if user_response == "accept_known_gaps":
            # Mark all stale gaps as known, continue
            for gap in stale_gaps:
                gap.status = "known_gap"
            return {"terminate": False, "action": "continue"}

        elif user_response == "abort":
            return {
                "terminate": True,
                "reason": "stale_gaps_unresolved",
                "gaps": stale_gaps
            }

        elif user_response == "retry":
            # Reset stale count, try again with refined questions
            for gap in stale_gaps:
                gap.stale_count = 0
            return {"terminate": False, "action": "retry"}
```
