# Feature Index: {{feature_id}}

> Central registry for specification workflow state.
> Updated by specify workflow agents. Plan workflow will extend this file when it runs.

---

## Feature Metadata

| Field | Value |
|-------|-------|
| **ID** | {{feature_id}} |
| **Branch** | {{branch_name}} |
| **Created** | {{created_timestamp}} |
| **Last Updated** | {{updated_timestamp}} |
| **Original Description** | {{original_description}} |

---

## Document Availability Matrix

> Updated by agents when they create/modify documents.

| Document | Status | Path | Last Modified |
|----------|--------|------|---------------|
| spec.md | {{spec_status}} | `specs/{{feature_id}}/spec.md` | {{spec_modified}} |
| checklists/ | {{checklists_status}} | `specs/{{feature_id}}/checklists/` | {{checklists_modified}} |

**Status values**: `present` | `absent` | `incomplete`

---

## Workflow Status Table

> Specify workflow updates its row when status changes.
> Plan/tasks rows will be added when those workflows run.

| Workflow | Status | Last Run | Current Agent | Context File |
|----------|--------|----------|---------------|--------------|
| specify | {{specify_status}} | {{specify_lastrun}} | {{specify_agent}} | `specify-context.md` |

**Status values**: `not_started` | `in_progress` | `blocked` | `completed`

---

## Priority Loop State

> Tracks the unified specify-checklist validation loop state.

| Field | Value |
|-------|-------|
| **Loop Status** | {{loop_status}} |
| **Current Iteration** | {{iteration_count}} / 10 |
| **Last Activity** | {{last_activity}} |
| **Stale Count** | {{stale_count}} / 3 |
| **Deferred Minor Gaps** | {{deferred_count}} |

**Loop Status values**: `not_started` | `scaffolding` | `spec_writing` | `validating` | `clarifying` | `completed` | `terminated`

---

## Gap Priority Queue

> Classified gaps from checklist validation awaiting resolution.
> Priority determines termination: Critical+Important must be zero to complete.

| Priority | Gap ID | CHK Source | FR Reference | Question | Status |
|----------|--------|------------|--------------|----------|--------|

**Priority**: `Critical` (MUST resolve) | `Important` (MUST resolve) | `Minor` (CAN defer)
**Status**: `pending` | `clarifying` | `resolved` | `deferred`

---

## Traceability Matrix

> Bidirectional mapping between requirements and checklist validation.

### Requirements → Checklist Coverage

| FR ID | CHK IDs | Coverage Status | Notes |
|-------|---------|-----------------|-------|

**Coverage Status**: `✓ Covered` | `⚠ Gap Found` | `○ No validation`

### Checklist → Requirements Mapping

| CHK ID | FR IDs | Gap Type | Resolution |
|--------|--------|----------|------------|

**Gap Type**: `Completeness` | `Clarity` | `Consistency` | `Coverage` | `Edge Case`

---

## Unified Pending Questions

> Aggregated clarifications from specify workflow. Supervisor presents these to users.
> ID format: `Q-{workflow_prefix}{number}` (Q-S1 = specify, Q-C1 = checklist)

| ID | Workflow | Location | Question | Options | Priority | Status |
|----|----------|----------|----------|---------|----------|--------|

**Priority**: `scope` > `security` > `ux` > `technical`
**Status**: `pending` | `answered` | `deferred`

---

## Gap Resolution History

> Append-only log of how gaps were resolved across iterations.

| Gap ID | CHK Source | Original Gap | Priority | Resolution | Resolved Via | Iteration | Timestamp |
|--------|------------|--------------|----------|------------|--------------|-----------|-----------|

---

## Unified Decisions Log

> Append-only log of decisions made during specify workflow.
> Each agent appends entries here after completing its work.

| Timestamp | Workflow | Agent | Decision | Rationale |
|-----------|----------|-------|----------|-----------|
| {{created_timestamp}} | specify | scaffold | Created feature branch {{branch_name}} | Auto-generated from description |

---

## Feature Readiness

| Milestone | Ready | Blocker |
|-----------|-------|---------|
| Spec complete | {{spec_ready}} | {{spec_blocker}} |
| Clarifications resolved | {{clarify_ready}} | {{clarify_blocker}} |
| Planning ready | {{plan_ready}} | {{plan_blocker}} |

### Workflow Dependencies

```
specify (with integrated checklist validation) ──> plan ──> tasks ──> implement
```

- `specify` includes: scaffolding → spec writing → checklist validation → clarification loop
- `plan` depends on: specify (completed with Priority Loop at zero Critical+Important gaps)

### Global Flags

| Flag | Value | Description |
|------|-------|-------------|
| `version` | 1.0.0 | Index schema version |
| `last_sync` | {{last_sync}} | Last time any agent synced to this index |

---

## Context File Quick Links

- [specify-context.md](./specify-context.md) - Specify workflow state (includes checklist validation)
