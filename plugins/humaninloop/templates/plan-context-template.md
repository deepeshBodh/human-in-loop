# Plan Workflow Context: {{feature_id}}

> Workflow-specific state for the plan workflow (technical design + architecture).
> Part of hybrid context architecture - see [index.md](./index.md) for shared state.

---

## Workflow Metadata

| Field | Value |
|-------|-------|
| **Workflow** | plan |
| **Feature ID** | {{feature_id}} |
| **Status** | {{status}} |
| **Last Run** | {{last_run}} |
| **Current Agent** | {{current_agent}} |

**Status values**: `not_started` | `researching` | `modeling` | `contracting` | `validating` | `completed` | `terminated`

---

## Plan Phase State (Local)

> Local tracking of multi-agent phase progress.

| Field | Value |
|-------|-------|
| **Current Phase** | {{current_phase}} |
| **Phase Name** | {{phase_name}} |
| **Phase Iterations** | {{phase_iterations}} / 3 |
| **Last Agent** | {{last_agent}} |
| **Next Agent** | {{next_agent}} |

---

## Quick Links

- **Index**: [index.md](./index.md) - Shared feature state
- **Spec**: [spec.md](../spec.md)
- **Plan**: [plan.md](../plan.md)
- **Other Contexts**: [specify](./specify-context.md) | [checklist](./checklist-context.md) | [tasks](./tasks-context.md)

---

## Prerequisites Check

| Prerequisite | Status | Notes |
|--------------|--------|-------|
| spec.md exists | {{spec_exists}} | |
| specify workflow completed | {{specify_completed}} | |
| clarifications resolved | {{clarify_resolved}} | |
| constitution.md exists | {{constitution_exists}} | |
| codebase discovery completed | {{discovery_completed}} | Required for brownfield |

---

## Codebase Context

> Filtered context from codebase discovery, injected per phase.
> Each planning agent receives only the sections relevant to its work.
> Empty for greenfield projects.

### Discovery Status

| Field | Value |
|-------|-------|
| **Status** | {{codebase_discovery_status}} |
| **Inventory Path** | {{codebase_inventory_path}} |
| **Greenfield** | {{is_greenfield}} |

### For Research Agent (Phase 0)

> Dependencies and tech stack context for technology decisions.

**Detected Tech Stack**:
{{detected_tech_stack}}

**Key Dependencies**:
{{detected_dependencies}}

**Architecture Pattern**: {{architecture_pattern}}

**Technology Decision Guidance**:
- Prefer technologies already in use when compatible
- Document justification when deviating from existing stack
- Consider integration complexity with existing systems

### For Domain Model Agent (Phase 1)

> Existing entities and vocabulary for collision avoidance.

**Existing Entities**:

| Entity | Source File | Fields | Collision Risk |
|--------|-------------|--------|----------------|

**Domain Vocabulary**:

| Term | Definition | Canonical Entity | Source |
|------|------------|------------------|--------|

**Entity Collision Guidance**:
- If entity name matches existing: Check field compatibility
- Compatible fields: Use `auto_extend` strategy (add new fields only)
- Conflicting fields: Escalate to user for resolution
- Use vocabulary mappings to align terminology

### For Contract Agent (Phase 2)

> Existing endpoints and API patterns for consistency.

**Existing Endpoints**:

| Method | Path | Handler | Related Entity |
|--------|------|---------|----------------|

**API Patterns Detected**:

| Pattern | Value |
|---------|-------|
| Base Path | {{api_base_path}} |
| Versioning | {{api_versioning}} |
| Auth Mechanism | {{api_auth_mechanism}} |
| Error Format | {{api_error_format}} |

**Endpoint Collision Guidance**:
- If exact path match: Escalate to user (high risk)
- If extending existing resource: Propose sub-resource or action endpoint
- Follow detected API patterns for consistency
- Match existing authentication requirements

### Collision Risk Summary

> Collisions requiring resolution before/during planning.

| Type | Proposed | Existing | Compatibility | Action | Status |
|------|----------|----------|---------------|--------|--------|

**Compatibility**: `compatible_extend` | `compatible_reuse` | `conflict` | `semantic_conflict`
**Action**: `auto_extend` | `escalate` | `rename` | `version` | `skip`
**Status**: `pending` | `resolved` | `deferred`

### Collision Resolutions

> Decisions made about how to handle collisions.

| Collision | Decision | Rationale | Decided By |
|-----------|----------|-----------|------------|

---

## Constitution Compliance

> Results of progressive constitution checking across phases.
> Each phase checks relevant principles only; Phase 3 performs full sweep.

### Phase Check Results

| Phase | Principles Checked | Result | Violations | Justification |
|-------|-------------------|--------|------------|---------------|
| 0: Research | Technology Choices | {{p0_result}} | {{p0_violations}} | {{p0_justification}} |
| 1: Domain Model | Data Privacy | {{p1_result}} | {{p1_violations}} | {{p1_justification}} |
| 2: Contracts | API Standards | {{p2_result}} | {{p2_violations}} | {{p2_justification}} |
| 3: Final | Full Sweep | {{p3_result}} | {{p3_violations}} | {{p3_justification}} |

**Result values**: `pass` | `violation` | `override_approved` | `pending`

### Violation Log

| Principle | Phase | Violation | Justification | Approved By |
|-----------|-------|-----------|---------------|-------------|

> Constitution violations are ALWAYS escalated to user. User must approve or justify override.

---

## Technical Decisions

> Key technology and architecture decisions made during planning.

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|-------------------------|-----------|

---

## Generated Artifacts

| Artifact | Status | Path | Notes |
|----------|--------|------|-------|
| plan.md | {{plan_status}} | `specs/{{feature_id}}/plan.md` | |
| research.md | {{research_status}} | `specs/{{feature_id}}/research.md` | |
| data-model.md | {{datamodel_status}} | `specs/{{feature_id}}/data-model.md` | |
| quickstart.md | {{quickstart_status}} | `specs/{{feature_id}}/quickstart.md` | |
| contracts/ | {{contracts_status}} | `specs/{{feature_id}}/contracts/` | |

---

## Entity Registry

> Quick reference of entities for downstream agents. Built during Phase 1 (Domain Model).

| Entity | Attributes | Relationships | Validation Rules | Source FRs |
|--------|------------|---------------|------------------|------------|

---

## Endpoint Registry

> Quick reference of endpoints for traceability. Built during Phase 2 (Contracts).

| Method | Path | Request Schema | Response Schema | Error Codes | Source FRs |
|--------|------|----------------|-----------------|-------------|------------|

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

> Each agent updates its section after completing. Supervisor reads these for context.

### From Research Agent (Phase 0)

- **Unknowns resolved**:
- **Decisions made**:
- **Unresolved count**: {{research_unresolved}}
- **Constitution principles checked**: Technology Choices
- **Ready for**: Validator (research-checks)

### From Domain Model Agent (Phase 1)

- **Entities created**:
- **Relationships defined**:
- **Validation rules**:
- **State machines**:
- **Constitution principles checked**: Data Privacy
- **Ready for**: Validator (model-checks)

### From Contract Agent (Phase 2)

- **Endpoints created**:
- **Schemas defined**:
- **Error responses**:
- **Quickstart scenarios**:
- **Constitution principles checked**: API Standards
- **Ready for**: Validator (contract-checks)

### From Validator Agent

- **Check module used**: {{check_module}}
- **Result**: {{validation_result}}
- **Checks passed**: {{checks_passed}} / {{checks_total}}
- **Gaps found**: Critical={{critical_gaps}}, Important={{important_gaps}}, Minor={{minor_gaps}}
- **Auto-resolved**: {{auto_resolved_count}}
- **Escalated**: {{escalated_count}}
- **Ready for**: {{next_action}}

### From Supervisor (Phase C)

- **Total iterations**:
- **Gaps resolved**:
- **Gaps deferred**:
- **Constitution overrides**:
- **Ready for**: Tasks Workflow

---

## Handoff to Index

> Summary of what should be synced to index.md after this workflow step.

**Decisions to log**:
<!-- List technical decisions made -->

**Questions to add** (prefix with Q-P#):
<!-- List new pending questions -->

**Status update**: plan -> {{new_status}}

**Document updates**:
<!-- List artifacts created -->
- plan.md: created
- research.md: created
- data-model.md: created (if applicable)
- contracts/: created (if applicable)
- quickstart.md: created
