# State Machine Modeling

Reference documentation for modeling entity state machines and status transitions.

## When to Model State

Model state machines when:
- Entity has a `status` or `state` field
- Requirements mention workflow or lifecycle
- Specific actions change entity state
- Certain actions only valid in certain states

## State Machine Format

```markdown
## State Machine: Task Status

### States

| State | Description | Entry Condition |
|-------|-------------|-----------------|
| `draft` | Initial state | Created by user |
| `active` | Work in progress | User starts task |
| `completed` | Work finished | User marks done |
| `archived` | No longer active | User archives |

### Transitions

| From | To | Trigger | Guard | Side Effects |
|------|-----|---------|-------|--------------|
| draft | active | user.startTask() | - | Set startedAt |
| active | completed | user.completeTask() | - | Set completedAt |
| active | draft | user.unpublish() | User is owner | Clear startedAt |
| completed | archived | user.archive() | - | - |
| * | archived | admin.archive() | Is admin | Log action |

### Diagram

```
[draft] ──start──▶ [active] ──complete──▶ [completed]
   │                  │                        │
   │                  ▼                        │
   └──────────▶ [archived] ◀───archive─────────┘
```
```

## State Documentation Components

### States Table

Each state should document:

| Column | Purpose |
|--------|---------|
| **State** | The state value (use backticks) |
| **Description** | What this state means |
| **Entry Condition** | How entity enters this state |

### Transitions Table

Each transition should document:

| Column | Purpose |
|--------|---------|
| **From** | Source state (`*` for any state) |
| **To** | Target state |
| **Trigger** | Action that causes transition |
| **Guard** | Condition that must be true |
| **Side Effects** | Other changes that occur |

## Common State Patterns

### Lifecycle Pattern

Standard create/active/archive lifecycle:

```
[draft] ──publish──▶ [active] ──archive──▶ [archived]
   ▲                    │
   └────unpublish───────┘
```

### Approval Workflow Pattern

Multi-step approval process:

```
[draft] ──submit──▶ [pending_review] ──approve──▶ [approved]
                           │
                           ├──reject──▶ [rejected]
                           │
                           └──request_changes──▶ [changes_requested]
                                                        │
                                                        ▼
                                                    [draft]
```

### Order/Payment Pattern

E-commerce order states:

```
[pending] ──pay──▶ [paid] ──ship──▶ [shipped] ──deliver──▶ [delivered]
    │                │                 │
    ▼                ▼                 ▼
[cancelled]     [refunded]        [returned]
```

## Guards and Side Effects

### Guard Examples

| Guard | Description |
|-------|-------------|
| `User is owner` | Only resource owner can perform action |
| `Is admin` | Requires admin role |
| `Within 24h` | Time-based constraint |
| `Has payment` | Prerequisite condition |
| `Not expired` | Validity check |

### Side Effect Examples

| Side Effect | Description |
|-------------|-------------|
| `Set startedAt` | Record timestamp |
| `Send notification` | Trigger notification |
| `Create audit log` | Record action |
| `Update parent` | Cascade to related entity |
| `Clear field` | Reset related data |

## State Machine in data-model.md

Include state machines in the data-model.md file:

```markdown
---

## State Machines

### Task Status

[States table]

[Transitions table]

[Diagram]

---
```

## Validation Checklist

- [ ] All states from requirements are documented
- [ ] Every state has a description
- [ ] All valid transitions are documented
- [ ] Guards specify who can perform transition
- [ ] Side effects are listed for complex transitions
- [ ] Diagram matches transitions table
- [ ] Initial state is clearly marked
- [ ] Terminal states (if any) are identified
