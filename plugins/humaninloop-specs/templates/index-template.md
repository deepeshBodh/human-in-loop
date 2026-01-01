# Feature Index: {{feature_id}}

> Unified state registry for specification workflow.
> All agents read from and write to this single file.
> Plan workflow will extend this file when it runs.

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

## Workflow Status

| Field | Value |
|-------|-------|
| **Current Phase** | {{current_phase}} |
| **Current Agent** | {{current_agent}} |
| **Last Run** | {{last_run}} |

**Phase values**: `scaffolding` | `spec_writing` | `validating` | `clarifying` | `completed`

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

## Specification Progress

> Updated by Spec Writer Agent after completing each section.

| Section | Status | Items Count | Notes |
|---------|--------|-------------|-------|
| User Stories | {{us_status}} | {{us_count}} | {{us_notes}} |
| Edge Cases | {{ec_status}} | {{ec_count}} | {{ec_notes}} |
| Functional Requirements | {{fr_status}} | {{fr_count}} | {{fr_notes}} |
| Key Entities | {{ke_status}} | {{ke_count}} | {{ke_notes}} |
| Success Criteria | {{sc_status}} | {{sc_count}} | {{sc_notes}} |

**Status values**: `not_started` | `in_progress` | `completed`

---

## Extracted Signals

> Signals extracted by Checklist Agent for validation focus.

### Domain Keywords

| Keyword | Source | Weight |
|---------|--------|--------|

**Weight**: user_input=3, spec=2, plan=1

### Risk Indicators

| Indicator | Source | Location |
|-----------|--------|----------|

### Focus Areas

| Rank | Area | Relevance | Source Signals |
|------|------|-----------|----------------|

**Relevance**: `high` | `medium` | `low`

---

## Checklist Configuration

| Dimension | Value | Rationale |
|-----------|-------|-----------|
| Theme | {{derived_theme}} | {{theme_rationale}} |
| Depth | {{derived_depth}} | {{depth_rationale}} |
| Audience | {{derived_audience}} | {{audience_rationale}} |
| Focus | {{derived_focus}} | {{focus_rationale}} |

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

### Requirements -> Checklist Coverage

| FR ID | CHK IDs | Coverage Status | Notes |
|-------|---------|-----------------|-------|

**Coverage Status**: `Covered` | `Gap Found` | `No validation`

### Checklist -> Requirements Mapping

| CHK ID | FR IDs | Gap Type | Resolution |
|--------|--------|----------|------------|

**Gap Type**: `Completeness` | `Clarity` | `Consistency` | `Coverage` | `Edge Case`

---

## Unified Pending Questions

> Aggregated clarifications from specify workflow. Supervisor presents these to users.
> ID format: `Q-S{n}` (spec writing) | `C{iter}.{n}` (gap-derived clarifications)

| ID | Source | Location | Question | Options | Priority | Status |
|----|--------|----------|----------|---------|----------|--------|

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

| Timestamp | Agent | Decision | Rationale |
|-----------|-------|----------|-----------|
| {{created_timestamp}} | scaffold | Created feature branch {{branch_name}} | Auto-generated from description |

---

## Agent Handoff Notes

> Critical context for the next agent. Updated by current agent before completing.

### Current Agent

| Field | Value |
|-------|-------|
| **Agent** | {{current_agent}} |
| **Started** | {{agent_started}} |
| **Status** | {{agent_status}} |

### Handoff from Previous Agent

<!-- Updated by each agent before completing -->

---

## Feature Readiness

| Milestone | Ready | Blocker |
|-----------|-------|---------|
| Spec complete | {{spec_ready}} | {{spec_blocker}} |
| Clarifications resolved | {{clarify_ready}} | {{clarify_blocker}} |
| Planning ready | {{plan_ready}} | {{plan_blocker}} |

### Workflow Dependencies

```
specify (with integrated checklist validation) --> plan --> tasks --> implement
```

- `specify` includes: scaffolding -> spec writing -> checklist validation -> clarification loop
- `plan` depends on: specify (completed with Priority Loop at zero Critical+Important gaps)

---

## Global Configuration

| Flag | Value | Description |
|------|-------|-------------|
| `version` | 1.0.0 | Index schema version |
| `last_sync` | {{last_sync}} | Last time any agent synced to this index |
