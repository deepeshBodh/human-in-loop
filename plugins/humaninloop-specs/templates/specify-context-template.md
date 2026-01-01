# Specify Workflow Context: {{feature_id}}

> Minimal workflow-specific state for specify workflow (spec writing + validation + clarification).
> Shared state is in [index.md](./index.md) - this file contains only agent handoff notes and checklist signals.

---

## Workflow Metadata

| Field | Value |
|-------|-------|
| **Workflow** | specify |
| **Feature ID** | {{feature_id}} |
| **Status** | {{status}} |
| **Last Run** | {{last_run}} |
| **Current Agent** | {{current_agent}} |

**Status values**: `scaffolding` | `writing` | `validating` | `clarifying` | `ready`

---

## Quick Links

- **Index**: [index.md](./index.md) - Shared feature state (Priority Loop, Traceability, Gap Queue)
- **Spec**: [spec.md](../spec.md)
- **Checklists**: [../checklists/](../checklists/)

---

## Paths

| Path | Location |
|------|----------|
| Feature Dir | `specs/{{feature_id}}/` |
| Spec File | `specs/{{feature_id}}/spec.md` |
| Checklists | `specs/{{feature_id}}/checklists/` |
| Context | `specs/{{feature_id}}/.workflow/specify-context.md` |
| Index | `specs/{{feature_id}}/.workflow/index.md` |

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

> Signals extracted by Checklist Context Analyzer for validation focus.

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

> Derived configuration for checklist generation runs.

| Dimension | Value | Source |
|-----------|-------|--------|
| Theme | {{derived_theme}} | {{theme_source}} |
| Depth | {{derived_depth}} | {{depth_source}} |
| Audience | {{derived_audience}} | {{audience_source}} |

---

## Agent Handoff Notes

> Critical context for the next agent. Updated by each agent before completing.

### From Scaffold Agent

- Branch created: {{branch_name}}
- Spec template copied to: specs/{{feature_id}}/spec.md
- Context initialized: {{timestamp}}
- Ready for: Spec Writer Agent

### From Spec Writer Agent

- Sections completed:
- User stories count:
- Requirements count:
- Ready for: Checklist Context Analyzer

### From Checklist Context Analyzer

- Signals extracted:
- Focus areas identified:
- Ready for: Checklist Writer Agent

### From Checklist Writer Agent

- Items generated:
- Gaps identified: Critical={{critical}}, Important={{important}}, Minor={{minor}}
- Ready for: Gap Classifier Agent (if gaps) or Completion (if no gaps)

### From Gap Classifier Agent

- Clarifications generated:
- Grouped from gaps:
- Ready for: User clarification via Supervisor

### From Spec Clarify Agent

- Round:
- Answers applied:
- Remaining gaps:
- Ready for: Re-validation or Completion

---

## Handoff to Index

> Summary of what should be synced to index.md after this workflow step.

**Decisions to log**:
<!-- List decisions made this session -->

**Priority Loop State update**:
<!-- loop_status, iteration_count, stale_count -->

**Gap Queue updates**:
<!-- New gaps to add, gaps resolved -->

**Traceability updates**:
<!-- FR ↔ CHK mappings -->

**Status update**: specify -> {{new_status}}
