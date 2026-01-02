# State Management

State transitions and artifact application patterns for the specification workflow.

---

## The Stateless Agent Pattern

> **Core Principle**: Agents are stateless functions. The workflow owns all state.

```
+----------+     +--------+     +----------+
| Workflow | --> | Agent  | --> | Workflow |
|  (state) |     | (pure) |     |  (state) |
+----------+     +--------+     +----------+
     |                               |
     v                               v
  Read files                    Write files
  Inject context                Apply artifacts
                                Update state
```

### Pattern Benefits

| Benefit | Explanation |
|---------|-------------|
| Crash recovery | State persisted in files, not memory |
| Retry safety | Agents can be re-run without side effects |
| Auditability | All changes tracked in index.md |
| Testability | Agents are pure functions of inputs |

---

## State Flow

### Agent Input/Output

Agents receive context and return artifacts:

```python
# Workflow prepares input
agent_input = {
    "context": {
        "feature_id": "005-user-auth",
        "workflow": "specify",
        "iteration": 1
    },
    "paths": {
        "index": "specs/005-user-auth/.workflow/index.md",
        "spec": "specs/005-user-auth/spec.md"
    },
    "task": {
        "action": "create",
        "params": {...}
    },
    "prior_context": [...]
}

# Agent returns output
agent_output = {
    "success": True,
    "summary": "...",
    "artifacts": [...],
    "state_updates": {...},
    "notes": [...],
    "recommendation": "proceed"
}
```

### Artifact Application

After every agent call, the workflow applies artifacts:

```python
def apply_artifacts(result):
    """
    Write agent artifacts to disk.
    """
    for artifact in result.artifacts:
        if artifact.operation == "create":
            write_file(artifact.path, artifact.content)
        elif artifact.operation == "update":
            write_file(artifact.path, artifact.content)
        elif artifact.operation == "delete":
            delete_file(artifact.path)
```

### State Update Application

Apply state updates to index.md:

```python
def apply_state_updates(index_path, state_updates):
    """
    Merge state updates into index.md.
    """
    # Read current index
    index = read_index(index_path)

    # Apply each section update
    for section, updates in state_updates.items():
        if section == "priority_loop_state":
            index.priority_loop_state.update(updates)
        elif section == "gap_priority_queue":
            merge_gap_queue(index.gap_priority_queue, updates)
        elif section == "traceability_matrix":
            merge_traceability(index.traceability_matrix, updates)
        # ... other sections

    # Write updated index
    write_index(index_path, index)
```

---

## Loop Status Values

| Status | Phase | Meaning |
|--------|-------|---------|
| `not_started` | Pre-A | Workflow not begun |
| `scaffolding` | A1 | Creating branch/directories |
| `spec_writing` | A2 | Generating spec content |
| `validating` | A3/B3 | Running validation checks |
| `clarifying` | B1 | Waiting for user answers |
| `completed` | C4 | Workflow finished successfully |
| `terminated` | - | Workflow ended (various reasons) |

### Status Transitions

```
not_started --> scaffolding --> spec_writing --> validating
                                                     |
     +-----------------------------------------------+
     |                                               |
     v                                               v
clarifying <------------------------------------> validating
     |                                               |
     +-------------------+---------------------------+
                         |
                         v
                 completed OR terminated
```

---

## Priority Loop State Structure

```markdown
## Priority Loop State

| Field | Value |
|-------|-------|
| **Loop Status** | {status} |
| **Current Iteration** | {n} / 10 |
| **Last Activity** | {ISO timestamp} |
| **Stale Count** | {n} / 3 |
| **Termination Reason** | {reason or null} |
| **Deferred Minor Gaps** | {count} |
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| Loop Status | enum | Current workflow phase |
| Current Iteration | number | 1-10, current loop iteration |
| Last Activity | ISO datetime | Timestamp of last state change |
| Stale Count | number | 0-3, iterations with unchanged gaps |
| Termination Reason | string | Why workflow ended (if terminated) |
| Deferred Minor Gaps | number | Count of deferred minor gaps |

---

## Gap Priority Queue

The central tracking structure for gaps.

### Queue Structure

```markdown
## Gap Priority Queue

| Priority | Gap ID | CHK Source | FR Reference | Question | Status | Stale | Clarification |
|----------|--------|------------|--------------|----------|--------|-------|---------------|
| Critical | G-001 | CHK015 | FR-003 | Auth failure? | resolved | 0 | C1.1 |
| Important | G-002 | CHK022 | FR-007 | Session timeout? | clarifying | 1 | C2.1 |
| Minor | G-003 | CHK030 | FR-012 | Button color? | deferred | 0 | - |
```

### Gap Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Gap identified, not yet addressed |
| `clarifying` | Question presented, awaiting answer |
| `resolved` | User answer applied to spec |
| `deferred` | Minor gap, deferred to later |
| `known_gap` | Stale gap, documented as known |

### Queue Operations

```python
def update_gap_status(queue, gap_id, new_status, details=None):
    """
    Update a gap's status in the queue.
    """
    for gap in queue:
        if gap.id == gap_id:
            gap.status = new_status
            if details:
                gap.resolution_details = details
            return

def add_gap(queue, gap):
    """
    Add a new gap to the queue.
    """
    gap.id = generate_gap_id()
    gap.status = "pending"
    gap.stale_count = 0
    queue.append(gap)

def remove_resolved_gaps(queue):
    """
    Clean up resolved gaps (optional, for clarity).
    """
    # Keep in queue for audit trail, but mark as resolved
    pass
```

---

## Gap Resolution History

Audit trail of gap handling.

```markdown
## Gap Resolution History

| Gap ID | Iteration | Action | Details | Timestamp |
|--------|-----------|--------|---------|-----------|
| G-001 | 1 | created | From CHK015 validation | 2024-01-15T10:00:00Z |
| G-001 | 1 | clarifying | Question C1.1 presented | 2024-01-15T10:05:00Z |
| G-001 | 1 | resolved | Answer: "Display inline error" | 2024-01-15T10:10:00Z |
| G-002 | 1 | created | From CHK022 validation | 2024-01-15T10:00:00Z |
| G-002 | 2 | clarifying | Question C2.1 presented | 2024-01-15T11:00:00Z |
```

---

## Traceability Matrix

Maps requirements to validation items.

```markdown
## Traceability Matrix

| FR ID | CHK IDs | Coverage Status | Gap IDs | Notes |
|-------|---------|-----------------|---------|-------|
| FR-001 | CHK001, CHK015 | Covered | - | - |
| FR-002 | CHK005 | Covered | - | - |
| FR-003 | CHK010, CHK011 | Gap Found | G-001 | Resolved in iter 1 |
| FR-007 | CHK022 | Gap Found | G-002 | Pending |
```

### Coverage Status Values

| Status | Meaning |
|--------|---------|
| Covered | All validation passed |
| Gap Found | Validation found issues |
| Partial | Some checks passed |
| Not Validated | No checks defined |

---

## State Update Patterns

### After Scaffold

```python
state_updates = {
    "priority_loop_state": {
        "loop_status": "spec_writing",
        "current_iteration": 1,
        "last_activity": now()
    },
    "document_availability": {
        "index": "present",
        "spec": "template"
    }
}
```

### After Spec Writer (Create)

```python
state_updates = {
    "priority_loop_state": {
        "loop_status": "validating"
    },
    "document_availability": {
        "spec": "present"
    },
    "specification_progress": {
        "user_stories": count,
        "requirements": count,
        "success_criteria": count
    }
}
```

### After Validation

```python
state_updates = {
    "gap_priority_queue": gaps,
    "traceability_matrix": coverage,
    "validation_summary": {
        "result": "partial",
        "critical": 2,
        "important": 5,
        "minor": 3
    }
}
```

### After Answer Application

```python
state_updates = {
    "priority_loop_state": {
        "loop_status": "validating",
        "current_iteration": iteration + 1
    },
    "gap_priority_queue": [
        {"id": "G-001", "status": "resolved"},
        {"id": "G-002", "status": "resolved"}
    ],
    "gap_resolution_history": [
        {"gap_id": "G-001", "action": "resolved", "details": answer}
    ]
}
```

### After Completion

```python
state_updates = {
    "priority_loop_state": {
        "loop_status": "completed",
        "termination_reason": "success"
    },
    "workflow_status": {
        "specify": "completed",
        "completed_at": now()
    }
}
```
