# Feature Index: {{feature_id}}

> Central registry for all workflow state and cross-feature coordination.
> Updated by all workflow agents. Each agent syncs its state here after completing.

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
| plan.md | {{plan_status}} | `specs/{{feature_id}}/plan.md` | {{plan_modified}} |
| tasks.md | {{tasks_status}} | `specs/{{feature_id}}/tasks.md` | {{tasks_modified}} |
| research.md | {{research_status}} | `specs/{{feature_id}}/research.md` | {{research_modified}} |
| data-model.md | {{datamodel_status}} | `specs/{{feature_id}}/data-model.md` | {{datamodel_modified}} |
| quickstart.md | {{quickstart_status}} | `specs/{{feature_id}}/quickstart.md` | {{quickstart_modified}} |
| contracts/ | {{contracts_status}} | `specs/{{feature_id}}/contracts/` | {{contracts_modified}} |
| checklists/ | {{checklists_status}} | `specs/{{feature_id}}/checklists/` | {{checklists_modified}} |
| codebase-inventory.json | {{inventory_status}} | `specs/{{feature_id}}/.workflow/codebase-inventory.json` | {{inventory_modified}} |

**Status values**: `present` | `absent` | `incomplete` | `skipped_greenfield`

---

## Codebase Discovery Summary

> Summary of existing codebase analysis from Phase A0 Discovery.
> Empty for greenfield projects. Populated by codebase-discovery agent.

| Field | Value |
|-------|-------|
| **Discovery Status** | {{discovery_status}} |
| **Inventory Path** | `specs/{{feature_id}}/.workflow/codebase-inventory.json` |
| **Last Run** | {{discovery_timestamp}} |
| **Greenfield** | {{is_greenfield}} |

### Existing Codebase Stats

| Metric | Count |
|--------|-------|
| Files Scanned | {{files_scanned}} |
| Entities Found | {{entities_count}} |
| Endpoints Found | {{endpoints_count}} |
| Features Identified | {{features_count}} |
| Collision Risks | {{collision_count}} |

### Detected Tech Stack

{{tech_stack_list}}

### Collision Risk Summary

> High-risk collisions requiring attention during planning.

| Type | Proposed (from spec) | Existing (in codebase) | Risk Level | Recommendation |
|------|----------------------|------------------------|------------|----------------|

**Discovery Status values**: `not_run` | `completed` | `partial` | `skipped_greenfield` | `failed`
**Risk Level**: `low` | `medium` | `high`
**Recommendation**: `auto_extend` | `auto_reuse` | `escalate` | `rename` | `version`

---

## Implementation Collision Log

> File collision decisions made during implementation.
> Updated by implement workflow Step 4.5.
> Recovery: Use `git diff` or `git checkout` to restore overwritten files.

| Timestamp | Task ID | File Path | Strategy | Status |
|-----------|---------|-----------|----------|--------|

**Strategy values**: `MERGE` | `OVERWRITE` | `SKIP` | `ABORT`
**Status values**: `pending` | `completed` | `skipped` | `aborted`

---

## Workflow Status Table

> Each workflow updates its row when status changes.
> Note: Checklist validation is integrated into the specify workflow via Priority Loop.

| Workflow | Status | Last Run | Current Agent | Context File |
|----------|--------|----------|---------------|--------------|
| specify | {{specify_status}} | {{specify_lastrun}} | {{specify_agent}} | `specify-context.md` |
| plan | {{plan_wf_status}} | {{plan_lastrun}} | {{plan_agent}} | `plan-context.md` |
| tasks | {{tasks_wf_status}} | {{tasks_lastrun}} | {{tasks_agent}} | `tasks-context.md` |
| implement | {{implement_status}} | {{implement_lastrun}} | {{implement_agent}} | `tasks-context.md` |

**Status values**: `not_started` | `in_progress` | `blocked` | `completed`

---

## Unified Pending Questions

> Aggregated clarifications from ALL workflows. Supervisor presents these to users.
> ID format: `Q-{workflow_prefix}{number}` (Q-S1 = specify, Q-C1 = checklist, Q-P1 = plan, Q-T1 = tasks)

| ID | Workflow | Location | Question | Options | Priority | Status |
|----|----------|----------|----------|---------|----------|--------|

**Priority**: `scope` > `security` > `ux` > `technical`
**Status**: `pending` | `answered` | `deferred`

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

## Plan Phase State

> Tracks the multi-agent planning workflow state (humaninloop:plan).

| Field | Value |
|-------|-------|
| **Phase** | {{plan_phase}} |
| **Phase Name** | {{plan_phase_name}} |
| **Current Iteration** | {{plan_iteration}} / 3 |
| **Total Iterations** | {{plan_total_iterations}} / 10 |
| **Last Activity** | {{plan_last_activity}} |
| **Stale Count** | {{plan_stale_count}} / 2 |

**Phase values**: `0: Research` | `1: Domain Model` | `2: Contracts` | `3: Final Validation`
**Status**: `not_started` | `researching` | `modeling` | `contracting` | `validating` | `completed` | `terminated`

---

## Tasks Phase State

> Tracks the multi-agent tasks workflow state (humaninloop:tasks).

| Field | Value |
|-------|-------|
| **Phase** | {{tasks_phase}} |
| **Phase Name** | {{tasks_phase_name}} |
| **Current Iteration** | {{tasks_iteration}} / 3 |
| **Total Iterations** | {{tasks_total_iterations}} / 6 |
| **Last Activity** | {{tasks_last_activity}} |
| **Stale Count** | {{tasks_stale_count}} / 2 |
| **Previous Gap Hash** | {{tasks_previous_gap_hash}} |

**Phase values**: `T0: Entry Gate` | `T1: Planning` | `T2: Generation` | `T3: Completion`
**Status**: `not_started` | `planning` | `generating` | `validating` | `completed` | `terminated`

---

## Gap Priority Queue

> Classified gaps from checklist validation awaiting resolution.
> Priority determines termination: Critical+Important must be zero to complete.

| Priority | Gap ID | CHK Source | FR Reference | Question | Status |
|----------|--------|------------|--------------|----------|--------|

**Priority**: `Critical` (MUST resolve) | `Important` (MUST resolve) | `Minor` (CAN defer)
**Status**: `pending` | `clarifying` | `resolved` | `deferred`

---

## Plan Gap Queue

> Gaps detected by plan validators awaiting resolution.
> Uses tiered handling: auto-resolve | auto-retry | escalate.

| Priority | Gap ID | Check Source | Phase | Artifact | Description | Tier | Status |
|----------|--------|--------------|-------|----------|-------------|------|--------|

**Priority**: `Critical` | `Important` | `Minor`
**Tier**: `auto-resolve` (agent fixes) | `auto-retry` (retry N times) | `escalate` (user decision)
**Status**: `pending` | `resolving` | `resolved` | `deferred`

---

## Tasks Gap Queue

> Gaps detected by task validators awaiting resolution.
> Uses tiered handling: auto-resolve | auto-retry | escalate.

| Priority | Gap ID | Check Source | Phase | Description | Tier | Status |
|----------|--------|--------------|-------|-------------|------|--------|

**Priority**: `Critical` | `Important` | `Minor`
**Check Source**: `mapping-checks` (Phase T1) | `task-checks` (Phase T2)
**Tier**: `auto-resolve` | `auto-retry` | `escalate`
**Status**: `pending` | `resolving` | `resolved` | `deferred`

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

## Plan Traceability

> Extended traceability: Requirements → Entities → Endpoints.
> Built progressively during plan workflow phases.

### Requirements → Entities

| FR ID | Requirement Summary | Entities | Coverage |
|-------|---------------------|----------|----------|

### Entities → Endpoints

| Entity | Endpoints | Coverage |
|--------|-----------|----------|

### Full Traceability Chain

| FR ID | Entity | Endpoint | Coverage |
|-------|--------|----------|----------|

**Coverage**: `✓ Full` | `⚠ Partial` | `○ None`

---

## Tasks Traceability

> Extended traceability: User Stories → Entities → Endpoints → Tasks.
> Built during tasks workflow, maps implementation tasks to design artifacts.

### User Stories → Tasks

| Story | Priority | Entities | Endpoints | Tasks | Coverage |
|-------|----------|----------|-----------|-------|----------|

### Tasks → Files

| Task ID | Story | File Path | Brownfield Marker | Status |
|---------|-------|-----------|-------------------|--------|

**Brownfield Marker**: `(none)` | `[EXTEND]` | `[MODIFY]` | `[CONFLICT]`
**Status**: `pending` | `in_progress` | `completed` | `blocked`

### Coverage Summary

| Metric | Count |
|--------|-------|
| Total Tasks | {{total_tasks}} |
| Tasks Covered | {{tasks_covered}} |
| Coverage Percentage | {{coverage_pct}}% |

---

## Gap Resolution History

> Append-only log of how gaps were resolved across iterations.

| Gap ID | CHK Source | Original Gap | Priority | Resolution | Resolved Via | Iteration | Timestamp |
|--------|------------|--------------|----------|------------|--------------|-----------|-----------|

---

## Unified Decisions Log

> Append-only log of decisions made across ALL workflows.
> Each agent appends entries here after completing its work.

| Timestamp | Workflow | Agent | Decision | Rationale |
|-----------|----------|-------|----------|-----------|
| {{created_timestamp}} | specify | scaffold | Created feature branch {{branch_name}} | Auto-generated from description |

---

## Cross-Workflow Notes

### Feature Readiness

| Milestone | Ready | Blocker |
|-----------|-------|---------|
| Spec complete | {{spec_ready}} | {{spec_blocker}} |
| Clarifications resolved | {{clarify_ready}} | {{clarify_blocker}} |
| Planning ready | {{plan_ready}} | {{plan_blocker}} |
| Implementation ready | {{impl_ready}} | {{impl_blocker}} |

### Workflow Dependencies

```
specify (with integrated checklist validation) ──> plan ──> tasks ──> implement
```

- `specify` includes: scaffolding → spec writing → checklist validation → clarification loop
- `plan` depends on: specify (completed with Priority Loop at zero Critical+Important gaps)
- `tasks` depends on: plan (completed)
- `implement` depends on: tasks (completed)

### Global Flags

| Flag | Value | Description |
|------|-------|-------------|
| `version` | 1.0.0 | Index schema version |
| `last_sync` | {{last_sync}} | Last time any agent synced to this index |

---

## Context File Quick Links

- [specify-context.md](./specify-context.md) - Specify workflow state (includes checklist validation)
- [plan-context.md](./plan-context.md) - Plan workflow state
- [tasks-context.md](./tasks-context.md) - Tasks workflow state
