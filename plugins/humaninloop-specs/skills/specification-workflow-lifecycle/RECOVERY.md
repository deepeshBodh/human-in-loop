# Recovery Patterns

Resume detection and crash recovery for the specification workflow.

---

## Resume Detection

Before starting a new workflow, check for existing interrupted workflows.

### Detection Algorithm

```python
def detect_resumable_workflow(feature_description):
    """
    Search for existing index.md files with incomplete status.
    """
    for spec_dir in glob("specs/*/"):
        index_path = f"{spec_dir}.workflow/index.md"
        if exists(index_path):
            index = parse_index(index_path)
            if index.loop_status not in ["completed", "terminated"]:
                if matches_feature(index.feature_name, feature_description):
                    return {
                        "found": True,
                        "feature_id": index.feature_id,
                        "iteration": index.current_iteration,
                        "loop_status": index.loop_status,
                        "index_path": index_path
                    }
    return {"found": False}
```

### User Prompt for Resume

```markdown
Found interrupted workflow for '005-user-auth'.

| Field | Value |
|-------|-------|
| Status | clarifying |
| Iteration | 2 / 10 |
| Pending Clarifications | 2 |
| Last Activity | 2024-01-15T10:30:00Z |

How would you like to proceed?
```

**Options**:

| Option | Description | Action |
|--------|-------------|--------|
| Resume | Continue from iteration 2 | Jump to saved state |
| Start Fresh | Delete and restart | Remove directory, start A1 |

---

## State Recovery

### Loop Status to Phase Mapping

| loop_status | Resume Point | Required Actions |
|-------------|--------------|------------------|
| `not_started` | Phase A1 | Full workflow |
| `scaffolding` | Phase A1 | Re-run scaffold |
| `spec_writing` | Phase A2 | Re-run spec writer |
| `validating` | Phase A3 or B3 | Re-run validation |
| `clarifying` | Phase B1 | Present pending questions |
| `completed` | None | Report already done |
| `terminated` | None | Report termination reason |

### Recovery Procedure

```python
def resume_workflow(index):
    """
    Resume workflow from saved state.
    """
    status = index.loop_status
    iteration = index.current_iteration

    if status == "not_started":
        return start_phase_a()

    elif status == "scaffolding":
        # Scaffold may have partially completed
        if exists(index.paths.spec_file):
            return start_phase_a2()
        else:
            return start_phase_a1()

    elif status == "spec_writing":
        return start_phase_a2()

    elif status == "validating":
        if iteration == 1:
            # Initial validation (Phase A)
            return start_phase_a3()
        else:
            # Loop validation (Phase B)
            return start_phase_b3(iteration)

    elif status == "clarifying":
        # Resume with pending questions
        pending = index.pending_questions
        return start_phase_b1(pending, iteration)

    elif status == "completed":
        return report_already_completed()

    elif status == "terminated":
        return report_termination(index.termination_reason)
```

---

## State Preservation

### What Gets Saved

The index.md file preserves complete workflow state:

```markdown
## Priority Loop State

| Field | Value |
|-------|-------|
| **Loop Status** | clarifying |
| **Current Iteration** | 2 / 10 |
| **Last Activity** | 2024-01-15T10:30:00Z |
| **Stale Count** | 0 / 3 |

## Pending Questions

| ID | Question Summary | Gaps | Status |
|----|------------------|------|--------|
| C2.1 | Session timeout | G-004 | awaiting_answer |

## Gap Priority Queue

| Priority | Gap ID | Status | Resolution |
|----------|--------|--------|------------|
| Critical | G-001 | resolved | Applied in iteration 1 |
| Important | G-004 | clarifying | Pending C2.1 |

## Gap Resolution History

| Gap ID | Iteration | Action | Details |
|--------|-----------|--------|---------|
| G-001 | 1 | resolved | Answer: "15 minute timeout" |
```

### When State Is Saved

State is saved:
- After each phase completes
- After each agent returns
- Before presenting questions to user
- After user provides answers

### Atomic State Updates

```python
def save_state_atomically(index_path, updates):
    """
    Apply state updates atomically to prevent partial writes.
    """
    # Read current state
    current = read_index(index_path)

    # Apply updates
    for section, changes in updates.items():
        current[section].update(changes)

    # Write updated state
    write_index(index_path, current)

    # Update last_activity timestamp
    current.priority_loop_state.last_activity = now()
```

---

## Crash Recovery Scenarios

### Scenario 1: Crash During Scaffold

**Detection**: index.md doesn't exist or loop_status = "not_started"

**Recovery**: Start from Phase A1

```python
if not exists(index_path) or index.loop_status == "not_started":
    # Full restart from scaffold
    start_phase_a1()
```

### Scenario 2: Crash During Spec Writing

**Detection**: loop_status = "spec_writing"

**Recovery**: Re-run spec writer (idempotent)

```python
if index.loop_status == "spec_writing":
    # Spec writer is idempotent - safe to re-run
    start_phase_a2()
```

### Scenario 3: Crash During Validation

**Detection**: loop_status = "validating"

**Recovery**: Re-run validator

```python
if index.loop_status == "validating":
    # Check which phase we were in
    if index.current_iteration == 1:
        start_phase_a3()  # Initial validation
    else:
        start_phase_b3(index.current_iteration)  # Loop validation
```

### Scenario 4: Crash Waiting for User

**Detection**: loop_status = "clarifying", pending_questions not empty

**Recovery**: Re-present pending questions

```python
if index.loop_status == "clarifying":
    pending = index.pending_questions
    start_phase_b1(pending, index.current_iteration)
```

### Scenario 5: Crash After User Answered

**Detection**: loop_status = "clarifying", user_answers in state

**Recovery**: Apply answers, continue to validation

```python
if index.loop_status == "clarifying" and index.user_answers:
    # Answers received but not applied
    start_phase_b2(index.user_answers, index.current_iteration)
```

---

## Fresh Start Procedure

When user chooses to start fresh:

```python
def start_fresh(feature_dir):
    """
    Delete existing state and start over.
    """
    # Confirm with user
    if not confirm("This will delete all progress. Continue?"):
        return

    # Remove feature directory
    remove_directory(feature_dir)

    # Start from scratch
    start_phase_a1()
```

---

## State Integrity Checks

Before resuming, validate state integrity:

```python
def validate_state(index):
    """
    Check that saved state is consistent.
    """
    checks = []

    # Check loop_status is valid
    valid_statuses = ["not_started", "scaffolding", "spec_writing",
                      "validating", "clarifying", "completed", "terminated"]
    checks.append(index.loop_status in valid_statuses)

    # Check iteration is in range
    checks.append(1 <= index.current_iteration <= 10)

    # Check stale_count is in range
    checks.append(0 <= index.stale_count <= 3)

    # Check pending questions match gap queue
    if index.pending_questions:
        pending_ids = [q.id for q in index.pending_questions]
        clarifying_gaps = [g for g in index.gap_priority_queue
                         if g.status == "clarifying"]
        checks.append(len(pending_ids) == len(clarifying_gaps))

    return all(checks)
```

If validation fails, offer user options:
1. Attempt repair (if possible)
2. Start fresh
3. Manual intervention
