# Tasks Workflow Context: {{feature_id}}

> Workflow-specific state for the tasks workflow (task generation + implementation tracking).
> Part of hybrid context architecture - see [index.md](./index.md) for shared state.

---

## Workflow Metadata

| Field | Value |
|-------|-------|
| **Workflow** | tasks |
| **Feature ID** | {{feature_id}} |
| **Status** | {{status}} |
| **Last Run** | {{last_run}} |
| **Current Agent** | {{current_agent}} |

**Status values**: `not_started` | `planning` | `validating_mapping` | `generating` | `validating_tasks` | `completed` | `implementing`

---

## Quick Links

- **Index**: [index.md](./index.md) - Shared feature state
- **Spec**: [spec.md](../spec.md)
- **Plan**: [plan.md](../plan.md)
- **Tasks**: [tasks.md](../tasks.md)
- **Other Contexts**: [specify](./context.md) | [checklist](./checklist-context.md) | [plan](./plan-context.md)

---

## Prerequisites Check

| Prerequisite | Status | Notes |
|--------------|--------|-------|
| spec.md exists | {{spec_exists}} | |
| plan.md exists | {{plan_exists}} | |
| specify workflow completed | {{specify_completed}} | |
| plan workflow completed | {{plan_completed}} | |

---

## Input Documents

> Documents consumed by task agents. Checksums detect changes requiring re-planning.

| Document | Path | Status | Checksum |
|----------|------|--------|----------|
| spec.md | `specs/{{feature_id}}/spec.md` | {{spec_doc_status}} | {{spec_checksum}} |
| plan.md | `specs/{{feature_id}}/plan.md` | {{plan_doc_status}} | {{plan_checksum}} |
| data-model.md | `specs/{{feature_id}}/data-model.md` | {{datamodel_doc_status}} | {{datamodel_checksum}} |
| contracts/ | `specs/{{feature_id}}/contracts/` | {{contracts_doc_status}} | - |
| research.md | `specs/{{feature_id}}/research.md` | {{research_doc_status}} | {{research_checksum}} |
| codebase-inventory.json | `specs/{{feature_id}}/.workflow/codebase-inventory.json` | {{inventory_doc_status}} | {{inventory_checksum}} |

**Status**: `valid` | `modified` | `missing` | `not_required`

---

## Phase T1: Planner Handoff

> State from task-planner agent. Produces task-mapping.md.

| Field | Value |
|-------|-------|
| **Status** | {{t1_status}} |
| **Iterations** | {{t1_iterations}} / 3 |
| **Artifact** | task-mapping.md |

### Extraction Summary

| Metric | Count |
|--------|-------|
| Stories extracted | {{stories_count}} |
| P1 stories | {{p1_stories}} |
| P2 stories | {{p2_stories}} |
| P3 stories | {{p3_stories}} |
| Entities mapped | {{entities_mapped}} |
| Endpoints mapped | {{endpoints_mapped}} |

### Brownfield Summary

| Risk Level | Count | Status |
|------------|-------|--------|
| High-risk collisions | {{high_risk_count}} | {{high_risk_status}} |
| Medium-risk | {{medium_risk_count}} | {{medium_risk_status}} |
| Low-risk | {{low_risk_count}} | {{low_risk_status}} |

### Planner Handoff Notes

{{t1_handoff_notes}}

---

## Phase T2: Generator Handoff

> State from task-generator agent. Produces tasks.md.

| Field | Value |
|-------|-------|
| **Status** | {{t2_status}} |
| **Iterations** | {{t2_iterations}} / 3 |
| **Artifact** | tasks.md |

### Generation Summary

| Metric | Value |
|--------|-------|
| Tasks generated | {{tasks_generated}} |
| Phases created | {{phases_created}} |
| Parallel opportunities | {{parallel_opportunities}} |

### Brownfield Markers Applied

| Marker | Count |
|--------|-------|
| [EXTEND] | {{extend_count}} |
| [MODIFY] | {{modify_count}} |
| [CONFLICT] | {{conflict_count}} |

### Generator Handoff Notes

{{t2_handoff_notes}}

---

## Pending Gaps

> Active gaps from validation awaiting resolution. Empty when workflow completes.

| Gap ID | Phase | Check | Severity | Description | Tier | Status |
|--------|-------|-------|----------|-------------|------|--------|

**Severity**: `Critical` | `Important` | `Minor`
**Tier**: `auto-resolve` | `auto-retry` | `escalate`
**Status**: `pending` | `resolving` | `resolved` | `deferred`

---

## User Decisions Log

> Decisions made by user during workflow (e.g., brownfield collision resolution).

| Timestamp | Decision | Context | Choice |
|-----------|----------|---------|--------|

---

## Task Generation Stats

| Metric | Value |
|--------|-------|
| Total Tasks | {{total_tasks}} |
| Phases | {{phase_count}} |
| Parallelizable Tasks | {{parallel_count}} |
| Sequential Tasks | {{sequential_count}} |

---

## Phase Summary

| Phase | User Story | Task Count | Status |
|-------|------------|------------|--------|
| Phase 1 | {{us1}} | {{p1_count}} | {{p1_status}} |
| Phase 2 | {{us2}} | {{p2_count}} | {{p2_status}} |
| Phase 3 | {{us3}} | {{p3_count}} | {{p3_status}} |

---

## Coverage Validation

> Mapping of requirements to tasks.

| Requirement | Task(s) | Coverage |
|-------------|---------|----------|
| FR-001 | T001, T002 | full |
| FR-002 | T003 | full |
| FR-003 | - | missing |

**Coverage values**: `full` | `partial` | `missing`

---

## Dependency Graph

> Task dependencies for execution ordering.

```
T001 ──> T002 ──> T003
           │
           └──> T004 ──> T005
```

---

## Implementation Progress

> Updated during /humaninloop-impl:implement execution.

| Task ID | Description | Status | File(s) Modified |
|---------|-------------|--------|------------------|

**Status values**: `pending` | `in_progress` | `completed` | `blocked` | `skipped`

---

## Workflow-Specific Clarifications

### Pending

| ID | Question | Options | Priority |
|----|----------|---------|----------|

### Resolved

| ID | Question | Answer | Applied To |
|----|----------|--------|------------|

---

## Agent Handoff Notes

### From Task-Planner Agent (Phase T1)

- **Stories extracted**: {{planner_stories}}
- **Entities mapped**: {{planner_entities}}
- **Endpoints mapped**: {{planner_endpoints}}
- **Brownfield risks identified**: High={{planner_high_risk}}, Medium={{planner_medium_risk}}, Low={{planner_low_risk}}
- **Orphaned items**: {{planner_orphans}}
- **Ready for**: Validator (mapping-checks)

### From Task-Generator Agent (Phase T2)

- **Tasks generated**: {{generator_tasks}}
- **Phases created**: {{generator_phases}}
- **Parallel opportunities**: {{generator_parallel}}
- **Brownfield markers applied**: EXTEND={{generator_extend}}, MODIFY={{generator_modify}}, CONFLICT={{generator_conflict}}
- **Dependencies validated**: {{generator_deps_valid}}
- **Ready for**: Validator (task-checks)

### From Task-Validator Agent

- **Check module used**: {{validator_module}}
- **Result**: {{validator_result}}
- **Checks passed**: {{validator_passed}} / {{validator_total}}
- **Gaps found**: Critical={{validator_critical}}, Important={{validator_important}}, Minor={{validator_minor}}
- **Auto-resolved**: {{validator_auto_resolved}}
- **Escalated**: {{validator_escalated}}
- **Ready for**: {{validator_next_action}}

### From Implement Agent

- **Tasks completed**: {{implement_completed}}
- **Tasks remaining**: {{implement_remaining}}
- **Files modified**: {{implement_files}}
- **Tests passing**: {{implement_tests}}
- **Ready for**: Review

---

## Handoff to Index

> Summary of what should be synced to index.md after this workflow step.

**Decisions to log**:
<!-- List task organization decisions -->

**Questions to add** (prefix with Q-T#):
<!-- List new pending questions -->

**Status update**: tasks -> {{new_status}}

**Document updates**:
- tasks.md: created/updated
