# Termination Conditions

The four conditions that end the Priority Loop.

---

## Condition 1: Success

**Trigger**: Zero Critical + Important gaps remaining.

```python
if gaps.critical.length == 0 AND gaps.important.length == 0:
    termination_reason = "success"
    proceed_to_phase_c()
```

**Outcome**:
- Workflow completes successfully
- Minor gaps logged as deferred
- Quality report generated
- Ready for next workflow phase (plan)

**State Update**:
```markdown
| **Loop Status** | completed |
| **Termination Reason** | success |
```

---

## Condition 2: Max Iterations

**Trigger**: Iteration count reaches maximum (10).

```python
if iteration >= 10:
    termination_reason = "max_iterations"
    log_remaining_gaps_as_known_issues()
    proceed_to_phase_c()
```

**Outcome**:
- Remaining Critical/Important gaps logged as known issues
- User notified of incomplete resolution
- Spec marked as "needs attention"
- Can still proceed to plan phase with caveats

**State Update**:
```markdown
| **Loop Status** | completed |
| **Termination Reason** | max_iterations |
| **Known Issues** | 2 Critical, 3 Important gaps unresolved |
```

**Known Issues Format**:
```markdown
## Known Issues (Max Iterations Reached)

The following gaps could not be resolved after 10 iterations:

| Gap ID | Priority | Description | Recommendation |
|--------|----------|-------------|----------------|
| G-005 | Critical | Auth timeout undefined | Address in implementation |
| G-008 | Important | Error format ambiguous | Clarify with dev team |
```

---

## Condition 3: Stale Detection

**Trigger**: Same gaps remain unresolved for 3 consecutive iterations.

```python
if same_gaps_for_3_iterations:
    termination_reason = "stale"
    escalate_to_user()
```

**Detection Logic**:
```python
def detect_staleness(gap_priority_queue, current_iteration):
    for gap in gap_priority_queue:
        if gap.status in ["pending", "clarifying"]:
            gap.stale_count = current_iteration - gap.first_seen_iteration
            if gap.stale_count >= 3:
                return True
    return False
```

**Escalation Message**:
```markdown
**Stale Gaps Detected**

The following gaps have remained unresolved for 3+ iterations:

| Gap ID | Question | Attempts |
|--------|----------|----------|
| G-001 | Auth failure handling? | 3 |

Options:
1. Provide different answers
2. Accept gaps as known limitations
3. Manually edit spec.md
```

**User Options**:

| Option | Action |
|--------|--------|
| Retry | Reset stale count, continue with refined questions |
| Accept | Mark as [KNOWN GAP], proceed to completion |
| Manual Edit | Stop workflow, user edits spec.md directly |

---

## Condition 4: No Progress

**Trigger**: Zero gaps resolved in current iteration.

```python
if resolved_this_iteration == 0:
    termination_reason = "no_progress"
    ask_user_to_decide()
```

**User Prompt**:
```markdown
**No Progress Detected**

No gaps were resolved in the last iteration. This may indicate:
- Answers need more specificity
- Questions need rephrasing
- Gaps are genuinely ambiguous

How should we proceed?
```

**User Options**:

| Option | Description | Action |
|--------|-------------|--------|
| Try again | Re-attempt with different answers | Continue loop |
| Accept current spec | Mark gaps as known issues | Proceed to completion |
| Abort workflow | Cancel and review manually | Terminate with "aborted" |

---

## Termination Decision Tree

```
Check Termination:
|
+-- Critical + Important == 0?
|   +-- YES --> terminate("success")
|   +-- NO --> continue
|
+-- iteration >= 10?
|   +-- YES --> terminate("max_iterations")
|   +-- NO --> continue
|
+-- same_gaps_for_3_iterations?
|   +-- YES --> escalate_to_user()
|   |           +-- User: Retry --> continue
|   |           +-- User: Accept --> terminate("stale_accepted")
|   |           +-- User: Manual --> terminate("manual_edit")
|   +-- NO --> continue
|
+-- resolved_this_iteration == 0?
|   +-- YES --> ask_user()
|   |           +-- User: Try again --> continue
|   |           +-- User: Accept --> terminate("accepted")
|   |           +-- User: Abort --> terminate("aborted")
|   +-- NO --> continue loop
```

---

## Termination Reasons Reference

| Reason | Trigger | Workflow Completed | Gaps Handled |
|--------|---------|-------------------|--------------|
| `success` | C+I gaps = 0 | Yes | All resolved |
| `max_iterations` | iteration >= 10 | Yes (with caveats) | Logged as known |
| `stale_accepted` | User accepts stale gaps | Yes | Marked as known |
| `manual_edit` | User chooses manual edit | No | User responsibility |
| `accepted` | User accepts no progress | Yes | Logged as known |
| `aborted` | User aborts | No | Not handled |

---

## Post-Termination Actions

### For Successful Completion

```python
def handle_success():
    log_deferred_minor_gaps()
    finalize_traceability_matrix()
    generate_quality_report()
    update_final_state("completed", "success")
```

### For Max Iterations

```python
def handle_max_iterations():
    log_remaining_gaps_as_known_issues()
    add_caveat_to_quality_report()
    update_final_state("completed", "max_iterations")
```

### For Stale/No Progress (User Accepted)

```python
def handle_user_accepted():
    mark_stale_gaps_as_known()
    log_user_decision()
    update_final_state("completed", termination_reason)
```

### For Abort

```python
def handle_abort():
    preserve_current_state()  # For potential resume
    update_final_state("terminated", "aborted")
    notify_user("Workflow aborted. State preserved in index.md.")
```
